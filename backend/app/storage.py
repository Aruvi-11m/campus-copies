import os
import shutil
import json
import io
from fastapi import UploadFile

# Try importing Cloudinary
try:
    import cloudinary
    import cloudinary.uploader
except ImportError:
    cloudinary = None

# Try importing Google Drive libraries
try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseUpload
except ImportError:
    service_account = None

# Fallback Local Storage Configuration
STORAGE_DIR = os.environ.get("STORAGE_DIR", "uploads")
if not os.path.exists(STORAGE_DIR):
    os.makedirs(STORAGE_DIR)

SCOPES = ['https://www.googleapis.com/auth/drive']

def save_file(upload_file: UploadFile, filename: str) -> str:
    # Option 1: Cloudinary (Incredibly simple setup!)
    cloudinary_url = os.environ.get("CLOUDINARY_URL")
    if cloudinary_url and cloudinary:
        try:
            # Cloudinary handles setup automatically when CLOUDINARY_URL is in the environment
            upload_result = cloudinary.uploader.upload(
                upload_file.file,
                public_id=filename.split('.')[0],
                resource_type="auto"
            )
            return upload_result.get("secure_url")
        except Exception as e:
            print("Cloudinary upload failed, checking other storages. Error:", e)
            upload_file.file.seek(0)

    # Option 2: Google Drive
    service_account_info_str = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    folder_id = os.environ.get("GOOGLE_DRIVE_FOLDER_ID")
    
    if service_account_info_str and service_account:
        try:
            # Read file contents
            file_content = upload_file.file.read()
            upload_file.file.seek(0) # Reset pointer
            
            # Setup Google Drive Service
            service_account_info = json.loads(service_account_info_str)
            creds = service_account.Credentials.from_service_account_info(
                service_account_info, scopes=SCOPES
            )
            service = build('drive', 'v3', credentials=creds)
            
            # File Metadata
            file_metadata = {'name': filename}
            if folder_id:
                file_metadata['parents'] = [folder_id]
                
            media = MediaIoBaseUpload(
                io.BytesIO(file_content),
                mimetype=upload_file.content_type or 'application/octet-stream',
                resumable=True
            )
            
            # Upload to Drive
            drive_file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink'
            ).execute()
            
            file_id = drive_file.get('id')
            
            # Make the uploaded file publicly viewable by anyone with the link
            try:
                permission = {
                    'type': 'anyone',
                    'role': 'reader',
                }
                service.permissions().create(
                    fileId=file_id,
                    body=permission
                ).execute()
            except Exception as perm_err:
                print("Failed to set permission on Google Drive file:", perm_err)
            
            # Return webViewLink for direct browser redirect
            return drive_file.get('webViewLink') or f"https://drive.google.com/file/d/{file_id}/view"
            
        except Exception as e:
            print("Google Drive upload failed, falling back to local storage. Error:", e)
            upload_file.file.seek(0)
            
    # Fallback: Save file to local container storage
    file_path = os.path.join(STORAGE_DIR, filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    return file_path


def get_file_path(filename: str) -> str:
    return os.path.join(STORAGE_DIR, filename)

