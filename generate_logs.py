import json
from datetime import datetime, timedelta
import random

# Output file for generated logs
output_file = "generated_logs.json"

# Define dummy data templates
account_numbers = ["1111111", "2222222", "3333333"]
account_names = ["account-111111", "account-222222", "account-333333"]
statuses = ["info", "warning", "critical"]
regions = ["us-east-1", "eu-west-1", "ap-southeast-1"]

# Generate logs
logs = []
start_time = datetime.now()

for i in range(100):  # Generate 100 log entries
    log_entry = {
        "title": "Inactive NAT Gateways",
        "account_number": random.choice(account_numbers),
        "account_name": random.choice(account_names),
        "datestamp": (start_time - timedelta(minutes=i)).strftime("%Y-%m-%d %H:%M:%S"),
        "resource_id": f"nat-{random.randint(100000000000000, 999999999999999)}",
        "status": random.choice(statuses),
        "region": random.choice(regions),
    }
    logs.append(log_entry)

# Write logs to a JSON file as an array
with open(output_file, "w") as f:
    json.dump(logs, f, indent=2)

output_file

