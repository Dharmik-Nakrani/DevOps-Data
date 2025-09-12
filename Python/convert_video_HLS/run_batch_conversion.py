#!/usr/bin/env python3
"""
Simple script to run batch video conversion using the CodeBuild trigger
"""

import sys
import os
from trigger_codebuild import CodeBuildTrigger
from config import *

def main():
    print("🎬 HLS Video Batch Conversion Tool")
    print("=" * 50)
    
    # Initialize the trigger
    trigger = CodeBuildTrigger(region_name=AWS_REGION)
    
    # Check if video list file exists
    if not os.path.exists(VIDEO_LIST_FILE):
        print(f"❌ Error: Video list file '{VIDEO_LIST_FILE}' not found")
        sys.exit(1)
    
    # Read and display video count
    video_paths = trigger.read_video_list(VIDEO_LIST_FILE)
    print(f"📁 Found {len(video_paths)} videos to process")
    
    if len(video_paths) == 0:
        print("❌ No videos found in the list file")
        sys.exit(1)
    
    # Display first few videos
    print("\n📋 Video files to process:")
    for i, path in enumerate(video_paths[:5], 1):
        filename = os.path.basename(path)
        print(f"   {i}. {filename}")
    
    if len(video_paths) > 5:
        print(f"   ... and {len(video_paths) - 5} more files")
    
    # Confirm before proceeding
    print(f"\n⚙️  Configuration:")
    print(f"   CodeBuild Project: {CODEBUILD_PROJECT_NAME}")
    print(f"   AWS Region: {AWS_REGION}")
    print(f"   Max Concurrent Builds: {MAX_CONCURRENT_BUILDS}")
    print(f"   Output Bucket: {OUTPUT_BUCKET}")
    
    response = input(f"\n🚀 Proceed with batch conversion? (y/n): ")
    if response.lower() != 'y':
        print("❌ Operation cancelled")
        sys.exit(0)
    
    # Prepare environment overrides
    env_overrides = HLS_SETTINGS.copy()
    env_overrides.update({
        'OUTPUT_BUCKET': OUTPUT_BUCKET,
        'NOTIFICATION_TOPIC': SNS_TOPIC_ARN,
        'BUILD_TIMEOUT': str(BUILD_TIMEOUT),
        'BUILD_IMAGE': BUILD_IMAGE,
    })
    
    # Trigger the build
    trigger.trigger_build(
        project_name=CODEBUILD_PROJECT_NAME,
        env_overrides=env_overrides,
        video_paths=video_paths,
        max_concurrent_builds=MAX_CONCURRENT_BUILDS
    )

if __name__ == "__main__":
    main()
