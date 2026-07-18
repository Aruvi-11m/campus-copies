import os
import sys
from app.database import SessionLocal, engine
from app import models, auth

def seed():
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    username = os.environ.get("ADMIN_USERNAME")
    password = os.environ.get("ADMIN_PASSWORD")
    
    if not username or not password:
        print("Error: ADMIN_USERNAME and ADMIN_PASSWORD environment variables must be set.")
        sys.exit(1)
        
    admin = db.query(models.Admin).filter(models.Admin.username == username).first()
    if admin:
        print(f"Admin user '{username}' already exists.")
    else:
        hashed_password = auth.get_password_hash(password)
        new_admin = models.Admin(username=username, password_hash=hashed_password)
        db.add(new_admin)
        db.commit()
        print(f"Admin user '{username}' created successfully.")
        
    db.close()

if __name__ == "__main__":
    seed()
