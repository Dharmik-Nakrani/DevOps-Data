import json
import re

with open("Prod Device.md", "r") as f:
    table_data = f.read()

with open("firmware_versions.json", "r") as f:
    devices = json.load(f)

results = []
for line in table_data.splitlines():
    if not line.startswith("|") or "Device ID" in line or "---" in line:
        continue
    
    cols = [c.strip() for c in line.strip("|").split("|")]
    if len(cols) < 3:
        continue
    
    device_id, status, display = cols
    if "WingCool" in display:
        version = devices.get(device_id, "N/A")
        results.append((device_id, display, version))

# ---------- Print Output ----------
print("| Device ID | Display   | Version |")
print("|-----------|-----------|---------|")
for device_id, display, version in results:
    print(f"| {device_id} | {display} | {version} |")