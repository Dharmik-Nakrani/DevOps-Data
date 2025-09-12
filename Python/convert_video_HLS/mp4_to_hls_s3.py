#!/usr/bin/env python3
import os
import subprocess
import logging
import boto3
from pathlib import Path
from botocore.exceptions import ClientError, NoCredentialsError
from typing import List

# Configuration from environment variables
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'ss-video-content-dev')
AWS_REGION = os.getenv('AWS_REGION', 'ap-southeast-2')

# HLS conversion parameters
HLS_TIME = 6  # Segment duration in seconds
HLS_LIST_SIZE = 0  # Keep all segments in playlist

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hls_conversion.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def setup_aws_client():
    """Initialize and return S3 client using default credential chain."""
    if not S3_BUCKET_NAME:
        logger.error("❌ S3_BUCKET_NAME environment variable not set")
        return None
    
    try:
        # Create session using default credential chain
        session = boto3.Session()
        s3_client = session.client('s3', region_name=AWS_REGION)
        
        # Test authentication by getting caller identity
        sts_client = session.client('sts', region_name=AWS_REGION)
        identity = sts_client.get_caller_identity()
        logger.info(f"✅ Authenticated as: {identity.get('Arn', 'Unknown')}")
        
        # Test S3 connection
        s3_client.head_bucket(Bucket=S3_BUCKET_NAME)
        logger.info(f"✅ Successfully connected to S3 bucket: {S3_BUCKET_NAME}")
        
        return s3_client
        
    except NoCredentialsError:
        logger.error("❌ AWS credentials not found. Please configure your credentials.")
        logger.info("💡 Run 'aws configure' or 'aws sso login' or set environment variables")
        return None
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'NoSuchBucket':
            logger.error(f"❌ S3 bucket '{S3_BUCKET_NAME}' does not exist")
        elif error_code == 'AccessDenied':
            logger.error(f"❌ Access denied to S3 bucket '{S3_BUCKET_NAME}'")
        else:
            logger.error(f"❌ S3 error: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Unexpected error setting up S3 client: {e}")
        return None


def convert_to_hls(input_path: str, output_folder: str) -> bool:
    """
    Convert MP4 video to HLS format using ffmpeg.
    
    Args:
        input_path: Path to input MP4 file
        output_folder: Path to output folder
        
    Returns:
        bool: True if conversion successful, False otherwise
    """
    video_name = Path(input_path).stem
    output_file = os.path.join(output_folder, f"{video_name}.m3u8")
    
    ffmpeg_cmd = [
        'ffmpeg',
        '-i', input_path,
        '-hls_time', str(HLS_TIME),
        '-hls_list_size', str(HLS_LIST_SIZE),
        '-f', 'hls',
        '-y',  # Overwrite output files
        output_file
    ]
    
    try:
        logger.info(f"🎬 Starting HLS conversion for: {input_path}")
        result = subprocess.run(
            ffmpeg_cmd,
            check=True,
            capture_output=True,
            text=True
        )
        logger.info(f"✅ Successfully converted {input_path} to HLS format")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ FFmpeg conversion failed for {input_path}")
        logger.error(f"Error: {e.stderr}")
        return False
    except FileNotFoundError:
        logger.error("❌ ffmpeg not found. Please install ffmpeg and ensure it's in your PATH")
        return False


def upload_folder_to_s3(s3_client, local_folder: str, s3_prefix: str) -> bool:
    """
    Upload entire folder to S3 while preserving folder structure.
    
    Args:
        s3_client: Boto3 S3 client
        local_folder: Path to local folder
        s3_prefix: S3 key prefix (folder name in bucket)
        
    Returns:
        bool: True if upload successful, False otherwise
    """
    try:
        folder_path = Path(local_folder)
        uploaded_files = 0
        
        for file_path in folder_path.rglob('*'):
            if file_path.is_file():
                # Calculate relative path from the base folder
                relative_path = file_path.relative_to(folder_path.parent)
                s3_key = str(relative_path).replace('\\', '/')  # Ensure forward slashes for S3
                
                # Upload file with progress
                file_size = file_path.stat().st_size
                logger.info(f"📤 Uploading: {s3_key} ({file_size:,} bytes)")
                
                s3_client.upload_file(
                    str(file_path),
                    S3_BUCKET_NAME,
                    s3_key
                )
                uploaded_files += 1
        
        logger.info(f"✅ Successfully uploaded {uploaded_files} files from {local_folder}")
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ExpiredToken':
            logger.error("❌ AWS token expired. Please re-authenticate")
        else:
            logger.error(f"❌ S3 upload failed for {local_folder}: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error during upload: {e}")
        return False


def process_video(video_path: str, s3_client) -> bool:
    """
    Process a single video: convert to HLS and upload to S3.
    
    Args:
        video_path: Path to MP4 video file
        s3_client: Boto3 S3 client
        
    Returns:
        bool: True if processing successful, False otherwise
    """
    try:
        # Validate input file
        if not os.path.exists(video_path):
            logger.error(f"❌ Input file not found: {video_path}")
            return False
        
        if not video_path.lower().endswith('.mp4'):
            logger.error(f"❌ Input file is not an MP4: {video_path}")
            return False
        
        # Extract video name and create output folder
        video_name = Path(video_path).stem
        output_folder = os.path.join(os.getcwd(), video_name)
        
        # Create output folder
        os.makedirs(output_folder, exist_ok=True)
        logger.info(f"📁 Created output folder: {output_folder}")
        
        # Convert to HLS
        if not convert_to_hls(video_path, output_folder):
            return False
        
        # Upload to S3
        if s3_client and not upload_folder_to_s3(s3_client, output_folder, video_name):
            return False
        
        logger.info(f"🎉 Successfully processed: {video_path}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Unexpected error processing {video_path}: {e}")
        return False


def process_videos(video_paths: List[str]) -> None:
    """
    Process a list of MP4 videos.
    
    Args:
        video_paths: List of paths to MP4 video files
    """
    if not video_paths:
        logger.error("❌ No video paths provided")
        return
    
    # Setup S3 client
    s3_client = setup_aws_client()
    if not s3_client:
        logger.warning("⚠️ S3 client setup failed. Videos will be converted but not uploaded.")
    
    successful = 0
    failed = 0
    
    logger.info(f"🚀 Starting processing of {len(video_paths)} videos")
    
    for i, video_path in enumerate(video_paths, 1):
        logger.info(f"📹 Processing video {i}/{len(video_paths)}: {video_path}")
        
        if process_video(video_path, s3_client):
            successful += 1
        else:
            failed += 1
    
    # Summary
    logger.info("="*60)
    logger.info(f"📊 Processing Summary:")
    logger.info(f"✅ Successful: {successful}")
    logger.info(f"❌ Failed: {failed}")
    logger.info(f"📁 Total: {len(video_paths)}")
    logger.info("="*60)


def main():
    """Main function to run the script."""
    # Example usage - replace with your video file paths
    video_files = [
        "path/to/your/video1.mp4",
        "path/to/your/video2.mp4",
        # Add more video paths here
    ]
    
    # Alternative: Read video paths from command line arguments
    import sys
    if len(sys.argv) > 1:
        video_files = sys.argv[1:]
        logger.info(f"Using video files from command line: {video_files}")
    else:
        # Example with relative paths - update these with your actual video files
        video_files = [
            "/home/dharmik-healtech/Videos/Uploaded/Sauna_Mastery_5.mp4",
        ]
        logger.info("Using default video file list. Update the script with your video paths.")
    
    # Process all videos
    process_videos(video_files)


if __name__ == "__main__":
    main()