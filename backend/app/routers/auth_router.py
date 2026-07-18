from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import models, schemas, auth, database

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/student/register", response_model=schemas.StudentResponse)
def register_student(student: schemas.StudentCreate, db: Session = Depends(database.get_db)):
    db_student = db.query(models.Student).filter(models.Student.mobile_number == student.mobile_number).first()
    if db_student:
        raise HTTPException(status_code=400, detail="Mobile number already registered")
    
    hashed_password = auth.get_password_hash(student.password)
    new_student = models.Student(
        name=student.name,
        mobile_number=student.mobile_number,
        department=student.department,
        password_hash=hashed_password
    )
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student

@router.post("/student/login", response_model=schemas.Token)
def login_student(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    student = db.query(models.Student).filter(models.Student.mobile_number == form_data.username).first()
    if not student or not auth.verify_password(form_data.password, student.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect mobile number or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": str(student.id), "role": "student"})
    return {"access_token": access_token, "token_type": "bearer", "role": "student"}

@router.post("/admin/login", response_model=schemas.Token)
def login_admin(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    admin = db.query(models.Admin).filter(models.Admin.username == form_data.username).first()
    if not admin or not auth.verify_password(form_data.password, admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": str(admin.id), "role": "admin"})
    return {"access_token": access_token, "token_type": "bearer", "role": "admin"}
