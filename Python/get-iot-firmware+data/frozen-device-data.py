import json
import re

# Read table file
with open("Prod Device.md", "r", encoding="utf-8") as f:
    table_data = f.read()

# Read firmware versions JSON
with open("firmware_versions.json", "r", encoding="utf-8") as f:
    firmware_versions = json.load(f)
# Extract rows for Frozen Device
frozen_list = []
for line in table_data.strip().splitlines():
    match = re.match(r"\|\s*([a-f0-9\-]+)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|", line)
    if match:
        device_id, status, display = match.groups()
        if status.strip() == "Frozen Device":
            version = firmware_versions.get(device_id, "Unknown")
            frozen_list.append((device_id, status.strip(), display.strip(), version))

# Print result
print("| Device ID | Frozen | Display | Version |")
print("|-----------|--------|---------|---------|")
for device_id, status, display, version in frozen_list:
    print(f"| {device_id} | {status} | {display} | {version} |")