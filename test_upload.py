import requests

API_URL = "http://localhost:8000"

# Login
login_data = {"username": "admin", "password": "r718906#"}
res = requests.post(f"{API_URL}/auth/admin/login", data=login_data)
token = res.json().get("access_token")

# Upload
with open("test.jpg", "wb") as f:
    f.write(b"fake image data")

files = {"file": ("test.jpg", open("test.jpg", "rb"), "image/jpeg")}
headers = {"Authorization": f"Bearer {token}"}
res = requests.post(f"{API_URL}/admin/pricing/qr-code", headers=headers, files=files)
print(res.status_code, res.text)
