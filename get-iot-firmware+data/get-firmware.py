import boto3
import json

def get_all_things(iot_client):
    """Fetch all IoT things (devices) from AWS IoT Core."""
    things = []
    paginator = iot_client.get_paginator('list_things')
    for page in paginator.paginate():
        things.extend(page['things'])
    return [thing['thingName'] for thing in things]

def get_thing_shadow(iot_data_client, thing_name):
    """Fetch shadow document for a specific thing."""
    try:
        response = iot_data_client.get_thing_shadow(thingName=thing_name)
        shadow_payload = json.loads(response['payload'].read())
        return shadow_payload
    except Exception as e:
        print(f"Error getting shadow for {thing_name}: {e}")
        return None

def extract_firmware_versions():
    iot_client = boto3.client('iot', region_name='ap-southeast-2')  # Specify your AWS region
    iot_data_client = boto3.client('iot-data', region_name='ap-southeast-2')  # Uses the same region

    firmware_map = {}

    thing_names = get_all_things(iot_client)
    print(f"Found {len(thing_names)} things.")

    for thing_name in thing_names:
        shadow = get_thing_shadow(iot_data_client, thing_name)
        
        if not shadow:
            continue
        try:
            version = shadow['state']['reported']['FirmwareVersion']
            print(f"Thing: {thing_name}, Firmware Version: {version}")
            firmware_map[thing_name] = version
        except KeyError:
            print(f"No firmware_version for {thing_name}")
            continue

    print("\n=== Firmware Versions ===")
    output_file = "firmware_versions.json"
    with open(output_file, "w") as f:
        json.dump(firmware_map, f, indent=2)
    print(f"Firmware versions saved to {output_file}")

if __name__ == "__main__":
    extract_firmware_versions()
