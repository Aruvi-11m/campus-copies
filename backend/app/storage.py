import os
import shutil
from fastapi import UploadFile

# A simple swappable storage interface.
# Defaulting to local disk for dev, can be replaced with S3/GCS/Cloudinary for production.

STORAGE_DIR = os.environ.get("STORAGE_DIR", "uploads")
if not os.path.exists(STORAGE_DIR):
    os.makedirs(STORAGE_DIR)

def save_file(upload_file: UploadFile, filename: str) -> str:
    file_path = os.path.join(STORAGE_DIR, filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    return file_path

def get_file_path(filename: str) -> str:
    return os.path.join(STORAGE_DIR, filename)
