import time
import requests
import subprocess
import os

API_BASE_URL = "http://localhost:8000"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

PRINTER_BW = "Epson-M1170"
PRINTER_COLOR = "Canon-G3012"

def get_admin_token():
    try:
        response = requests.post(f"{API_BASE_URL}/auth/login", data={
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            print(f"Failed to login: {response.text}")
    except Exception as e:
        print(f"Error authenticating: {e}")
    return None

def fetch_ready_orders(token):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(f"{API_BASE_URL}/admin/orders?status=Payment Received", headers=headers)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error fetching orders: {e}")
    return []

def update_order_status(token, order_id, status):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        requests.put(f"{API_BASE_URL}/admin/orders/{order_id}/status?status={status}", headers=headers)
        print(f"Order {order_id} status updated to {status}")
    except Exception as e:
        print(f"Error updating order {order_id}: {e}")

def log_print_job(token, printer_name, pages_printed):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        requests.post(f"{API_BASE_URL}/admin/print-logs", json={
            "printer_name": printer_name,
            "pages_printed": pages_printed
        }, headers=headers)
    except Exception as e:
        print(f"Error logging print job: {e}")

def print_pdf(filepath, printer_name, copies=1, print_type="single_side"):
    sides = "two-sided-long-edge" if print_type == "double_side" else "one-sided"
    cmd = ["lp", "-d", printer_name, "-n", str(copies), "-o", f"sides={sides}", filepath]
    print(f"Executing: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(f"Print result: {result.stdout}")
        return result.returncode == 0
    except Exception as e:
        print(f"Print execution failed: {e}")
        return False

def process_order(token, order):
    order_id = order["id"]
    file_info = order["file"]
    filepath = file_info["filepath"]
    download_url = f"{API_BASE_URL}/{filepath}"
    
    local_pdf = f"temp_print_{order_id}.pdf"
    
    try:
        print(f"Downloading PDF from {download_url}...")
        r = requests.get(download_url, stream=True)
        if r.status_code == 200:
            with open(local_pdf, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    f.write(chunk)
            
            update_order_status(token, order_id, "Printing")
            
            printer_name = PRINTER_COLOR if order["color_type"] == "color" else PRINTER_BW
            
            success = print_pdf(local_pdf, printer_name, copies=order["copies"], print_type=order["print_type"])
            
            if success:
                pages_printed = file_info["page_count"] * order["copies"]
                log_print_job(token, printer_name, pages_printed)
                update_order_status(token, order_id, "Ready For Pickup")
            else:
                print(f"Failed to print order {order_id}")
                
            os.remove(local_pdf)
        else:
            print(f"Failed to download PDF for order {order_id}, status code: {r.status_code}")
    except Exception as e:
        print(f"Error processing order {order_id}: {e}")

def run_agent():
    print("Starting Print Agent...")
    token = None
    while True:
        if not token:
            token = get_admin_token()
        
        if token:
            orders = fetch_ready_orders(token)
            if orders:
                print(f"Found {len(orders)} orders ready to print.")
                for order in orders:
                    process_order(token, order)
        
        time.sleep(5)

if __name__ == "__main__":
    run_agent()
