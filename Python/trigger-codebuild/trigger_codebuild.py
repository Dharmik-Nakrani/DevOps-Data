#!/usr/bin/env python3


import boto3
from botocore.exceptions import ClientError, NoCredentialsError


def start_codebuild_process(project_name, firmware_environment,s1_firmware_branch, s1_sauna_manager_branch, s1_web_branch, username, region='ap-southeast-2'):
    """Start the AWS CodeBuild process with specified environment variables."""
    try:
        client = boto3.client('codebuild', region_name=region)
        response = client.start_build(
            projectName=project_name,
            sourceVersion=s1_firmware_branch,  # Change Source Branch
            computeTypeOverride='BUILD_GENERAL1_LARGE',  # Change Server Type 
            environmentVariablesOverride=[
                {'name': 'ENVIRONMENT', 'value': firmware_environment, 'type': 'PLAINTEXT'},
                {'name': 'DRAFTER', 'value': username, 'type': 'PLAINTEXT'},
                {'name': 'S1_FIRMWARE_BRANCH', 'value': s1_firmware_branch, 'type': 'PLAINTEXT'},
                {'name': 'S1_FIRMWARE_SAUNA_MANAGER', 'value': s1_sauna_manager_branch, 'type': 'PLAINTEXT'},
                {'name': 'S1_WEB', 'value': s1_web_branch, 'type': 'PLAINTEXT'},
            ],
        )
        build_id = response['build']['id']
        print(f"✅ CodeBuild started successfully!")
        print(f"   Build ID: {build_id}")
        return build_id
    except ClientError as e:
        print(f"❌ AWS Error: {e.response['Error']['Code']} - {e.response['Error']['Message']}")
        raise
    except Exception as e:
        print(f"❌ Failed to start CodeBuild: {str(e)}")
        raise


# start_codebuild_process(
#     project_name="Healtech-ss-firmware-specific-branch",
#     firmware_environment="dev",
#     s1_firmware_branch="feature/flutter-version-upgrade",
#     s1_sauna_manager_branch="feature/slot_blocked_schedule",
#     s1_web_branch="HT-471_update-version",
#     username="Dharmik Nakrani"
# )

start_codebuild_process(
    project_name="Healtech-S1-Firmware-Release-Specific-Device",
    firmware_environment="prod",
    s1_firmware_branch="hotfix/autosuspend-issue",
    s1_sauna_manager_branch="main",
    s1_web_branch="main",
    username="Dharmik Nakrani"
)
