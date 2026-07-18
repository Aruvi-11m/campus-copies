import os
import time
import requests
import subprocess
import tempfile

API_URL = os.environ.get("API_URL", "http://localhost:8000")
AGENT_KEY = os.environ.get("AGENT_KEY", "default-agent-key-change-me")
POLL_INTERVAL = int(os.environ.get("POLL_INTERVAL", "10"))

HEADERS = {
    "X-Agent-Key": AGENT_KEY
}

def update_status(order_id, status):
    res = requests.put(f"{API_URL}/agent/orders/{order_id}/status", json={"status": status}, headers=HEADERS)
    res.raise_for_status()

def log_print(order_id, printer_used, options_used, status, error_message=""):
    requests.post(f"{API_URL}/agent/logs", params={
        "order_id": order_id,
        "printer_used": printer_used,
        "options_used": options_used,
        "status": status,
        "error_message": error_message
    }, headers=HEADERS)

def download_file(url, local_path):
    # In a real deployed environment, the file_path in DB might be a URL (S3) or relative path.
    # Here we assume local dev where the agent and backend might share disk, or the agent fetches via a download endpoint.
    # We will simulate downloading if it's a URL, or copy if it's local.
    if url.startswith("http"):
        r = requests.get(url, stream=True)
        r.raise_for_status()
        with open(local_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    else:
        # Assuming local path for dev
        with open(url, 'rb') as src, open(local_path, 'wb') as dst:
            dst.write(src.read())

def process_order(order):
    order_id = order["id"]
    color = order["color"]
    print_type = order["print_type"]
    copies = order["copies"]
    file_path = order["file_path"]

    # We transition to PRINTING immediately upon picking it up
    update_status(order_id, "PRINTING")

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        local_pdf_path = tmp.name

    try:
        download_file(file_path, local_pdf_path)

        if color == "color":
            # Manual routing to Canon G3012
            printer = "Canon G3012"
            options = "Manual"
            log_print(order_id, printer, options, "manual_pending")
            print(f"Order {order_id} flagged for MANUAL COLOR print.")
            
        elif color == "black_white":
            # Automatic routing to Epson M1170
            printer = "Epson M1170"
            lp_cmd = ["lp", "-d", printer, "-n", str(copies)]
            options = ""

            if print_type == "single_side":
                pass
            elif print_type == "double_side":
                lp_cmd.extend(["-o", "sides=two-sided-long-edge"])
                options = "two-sided-long-edge"
            elif print_type == "multi_page":
                lp_cmd.extend(["-o", "number-up=2", "-o", "sides=two-sided-short-edge"])
                options = "number-up=2, two-sided-short-edge"

            lp_cmd.append(local_pdf_path)
            
            print(f"Executing: {' '.join(lp_cmd)}")
            # In a real environment with the printer installed, we would run this:
            # result = subprocess.run(lp_cmd, capture_output=True, text=True)
            # if result.returncode == 0:
            
            # Simulated success for demonstration without physical printer
            # In production, use the subprocess result check
            success = True
            
            if success:
                update_status(order_id, "READY_FOR_PICKUP")
                log_print(order_id, printer, options, "success")
                print(f"Order {order_id} printed successfully.")
            else:
                log_print(order_id, printer, options, "failed", "lp command failed")
                print(f"Order {order_id} print failed.")

    except Exception as e:
        log_print(order_id, "Unknown", "", "failed", str(e))
        print(f"Order {order_id} encountered error: {e}")
    finally:
        if os.path.exists(local_pdf_path):
            os.remove(local_pdf_path)

def main():
    print(f"Starting Campus Copies Print Agent. Polling every {POLL_INTERVAL} seconds...")
    while True:
        try:
            res = requests.get(f"{API_URL}/agent/orders/pending", headers=HEADERS)
            if res.status_code == 200:
                orders = res.json()
                for order in orders:
                    print(f"Found pending order: {order['order_number']}")
                    process_order(order)
            else:
                print(f"Error fetching orders: HTTP {res.status_code}")
        except Exception as e:
            print(f"Connection error: {e}")
        
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
