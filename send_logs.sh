#!/bin/bash


# Log file containing JSON lines
log_file="generated_logs.json"

# Loki URL and credentials
loki_url = "https://loki.URL.com/loki/api/v1/push"  # Loki endpoint
username = "tenant_id"
password = "token"


# Function to convert datestamp to nanoseconds
convert_to_nanoseconds() {
  local datestamp="$1"
  python3 -c "from datetime import datetime; print(int(datetime.strptime('$datestamp', '%Y-%m-%d %H:%M:%S').timestamp() * 1e9))" 2>/dev/null || echo ""
}


# Read each log entry and send it to Loki
jq -c '.[]' "$log_file" | while IFS= read -r log_line; do
  # Extract fields using jq
  account_number=$(echo "$log_line" | jq -r '.account_number')
  account_name=$(echo "$log_line" | jq -r '.account_name')
  datestamp=$(echo "$log_line" | jq -r '.datestamp')

  # Validate extracted fields
  if [[ -z "$account_number" || -z "$account_name" || -z "$datestamp" ]]; then
    echo "Skipping invalid log line: $log_line"
    continue
  fi

  # Convert datestamp to nanoseconds
  timestamp=$(convert_to_nanoseconds "$datestamp")

  # Validate timestamp
  if [[ -z "$timestamp" ]]; then
    echo "Skipping log line with invalid datestamp: $log_line"
    continue
  fi

  # Format the payload
  payload=$(jq -n --arg ts "$timestamp" --argjson msg "$log_line" \
                 --arg account_number "$account_number" \
                 --arg account_name "$account_name" \
                 --arg datestamp "$datestamp" '{
    streams: [
      {
        stream: {
          account_number: $account_number,
          account_name: $account_name,
          datestamp: $datestamp
        },
        values: [[ $ts, ($msg | @json) ]]
      }
    ]
  }')

  # Log the payload for debugging
  echo "Generated Payload: $payload"

  # Validate payload JSON structure
  if ! jq empty <<< "$payload" 2>/dev/null; then
    echo "Invalid payload generated for log line: $log_line"
    continue
  fi

  # Send to Loki and capture the response
  response=$(curl -u "$username:$password" -H "Content-Type: application/json" -X POST -s -w "%{http_code}" -o /tmp/loki_response.log "$loki_url" --data "$payload")
  http_code=$(tail -n1 <<< "$response")  # Get the HTTP status code

  # Check the HTTP status code
  if [[ "$http_code" -eq 204 ]]; then
    echo "Log successfully sent: $log_line"
  else
    echo "Failed to send log: $log_line"
    echo "Loki response: $(cat /tmp/loki_response.log)"
    echo "Payload: $payload"  # Output the payload for inspection
  fi
done
