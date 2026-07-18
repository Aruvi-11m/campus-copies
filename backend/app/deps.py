from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from . import auth, database, models

oauth2_scheme_student = OAuth2PasswordBearer(tokenUrl="/auth/student/login")
oauth2_scheme_admin = OAuth2PasswordBearer(tokenUrl="/auth/admin/login")

def get_current_user_from_token(token: str, db: Session, expected_role: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        user_id: str = payload.get("sub")
        role: str = payload.get("role")
        if user_id is None or role != expected_role:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    if expected_role == "student":
        user = db.query(models.Student).filter(models.Student.id == int(user_id)).first()
    elif expected_role == "admin":
        user = db.query(models.Admin).filter(models.Admin.id == int(user_id)).first()
    else:
        raise credentials_exception

    if user is None:
        raise credentials_exception
    return user

def get_current_student(token: str = Depends(oauth2_scheme_student), db: Session = Depends(database.get_db)):
    return get_current_user_from_token(token, db, "student")

def get_current_admin(token: str = Depends(oauth2_scheme_admin), db: Session = Depends(database.get_db)):
    return get_current_user_from_token(token, db, "admin")
