import requests

API_URL = "https://campus-copies.onrender.com"

login_data = {"username": "aruvi11m", "password": "r718906#"}
res = requests.post(f"{API_URL}/auth/admin/login", data=login_data)
token = res.json().get("access_token")

headers = {"Authorization": f"Bearer {token}"}

pricing_payload = {
    "single_side_price": "1",
    "double_side_price": "1.55",
    "multi_page_price": "2",
    "color_price": "10",
    "spiral_binding_price": "35",
    "soft_binding_price": "40",
    "gst_percent": "0",
    "upi_id": "6381056942",
    "qr_code_path": None,
    "id": 1,
    "updated_at": "2026-07-18T10:00:00Z"
}

res = requests.put(f"{API_URL}/admin/pricing", json=pricing_payload, headers=headers)
print("PUT pricing response:", res.status_code, res.text)
