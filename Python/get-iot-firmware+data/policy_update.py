import boto3

# ---------- Config ----------
# Update with your IoT Policy name
POLICY_NAME = "Healtech_Device_Update_Deny"

# List of IoT Things (replace with your actual device IDs or Thing Names)
things_to_update = [
"fb5b0c0d-ec57-4a15-a7ee-d962a1b48cb9",
"a1bdad74-b8a8-4494-9970-410684fe7935",
"53549cad-2ec2-4586-9afc-87be7c11ec1d",
"ece7e88c-885b-4f93-b22b-50bf8eb56676",
"a373df09-70c3-4b92-bf85-c7a5ac563c52",
]

# ---------- AWS Clients ----------
iot = boto3.client("iot", region_name='ap-southeast-2')

def attach_policy_to_things(things, policy_name):
    for thing_name in things:
        try:
            # 1. Get certificates attached to the Thing
            principals = iot.list_thing_principals(thingName=thing_name)["principals"]

            if not principals:
                print(f"[WARN] No certificate attached to {thing_name}")
                continue

            for principal in principals:
                # 2. Attach IoT Policy to each certificate
                iot.attach_policy(policyName=policy_name, target=principal)
                print(f"[OK] Policy '{policy_name}' attached to {thing_name} ({principal})")

        except Exception as e:
            print(f"[ERROR] Failed for {thing_name}: {e}")

if __name__ == "__main__":
    attach_policy_to_things(things_to_update, POLICY_NAME)
