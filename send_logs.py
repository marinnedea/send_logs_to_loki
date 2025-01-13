import json
import requests
from datetime import datetime

# Configuration
log_file = "generated_logs.json"  # Log file containing JSON entries

# Loki URL and credentials
loki_url = "https://loki.URL.com/loki/api/v1/push"  # Loki endpoint
username = "tenant_id"
password = "token"

# Function to convert datestamp to nanoseconds
def convert_to_nanoseconds(datestamp):
    try:
        dt = datetime.strptime(datestamp, "%Y-%m-%d %H:%M:%S")
        return int(dt.timestamp() * 1e9)  # Convert to nanoseconds
    except ValueError as e:
        print(f"Invalid datestamp: {datestamp}, Error: {e}")
        return None

# Function to send logs to Loki
def send_to_loki(logs):
    for log in logs:
        account_number = log.get("account_number")
        account_name = log.get("account_name")
        datestamp = log.get("datestamp")

        # Validate required fields
        if not all([account_number, account_name, datestamp]):
            print(f"Skipping invalid log: {log}")
            continue

        # Convert datestamp to nanoseconds
        timestamp = convert_to_nanoseconds(datestamp)
        if not timestamp:
            print(f"Skipping log with invalid datestamp: {log}")
            continue

        # Construct payload
        payload = {
            "streams": [
                {
                    "stream": {
                        "account_number": account_number,
                        "account_name": account_name,
                        "datestamp": datestamp,
                    },
                    "values": [[str(timestamp), json.dumps(log)]],
                }
            ]
        }

        # Send payload to Loki
        response = requests.post(
            loki_url,
            json=payload,
            auth=(username, password),
            headers={"Content-Type": "application/json"},
        )

        # Handle response
        if response.status_code == 204:
            print(f"Log successfully sent: {log}")
        else:
            print(f"Failed to send log: {log}")
            print(f"Loki response: {response.status_code}, {response.text}")

# Main logic
if __name__ == "__main__":
    try:
        # Load logs from file
        with open(log_file, "r") as f:
            logs = json.load(f)

        # Send logs to Loki
        send_to_loki(logs)

    except FileNotFoundError:
        print(f"Log file not found: {log_file}")
    except json.JSONDecodeError as e:
        print(f"Error parsing log file: {e}")

