#!/bin/bash

# AWS Region
REGION="ap-southeast-2"  # Change to your region

# Shadow name to check
SHADOW_NAME="public"  # Change if using a different named shadow

# AWS Account ID (replace with your actual account ID)
ACCOUNT_ID="811544304562"  # Change this to your AWS account ID

# Get all Things from AWS IoT
get_all_things() {
  echo "🔍 Fetching all Things from AWS IoT..."
  aws iot list-things \
    --region "$REGION" \
    --output json > things.json

  if [ $? -eq 0 ]; then
    THING_NAMES=($(jq -r '.things[].thingName' things.json))
    if [ ${#THING_NAMES[@]} -eq 0 ]; then
      echo "⚠️ No Things found in your AWS IoT account."
      exit 1
    fi
    echo "✅ Found ${#THING_NAMES[@]} Things."
  else
    echo "❌ Failed to fetch Things. Check your AWS configuration."
    exit 1
  fi
}

# Get named shadow data
get_shadow_data() {
  local thing_name=$1
  echo "🔍 Checking shadow availability for $thing_name..."
  aws iot-data get-thing-shadow \
    --thing-name "$thing_name" \
    --shadow-name "$SHADOW_NAME" \
    --region "$REGION" \
    --output json > /dev/null 2>&1

  if [ $? -eq 0 ]; then
    echo "✅ Shadow '$SHADOW_NAME' is available for $thing_name."
  else
    echo "⚠️ Shadow '$SHADOW_NAME' is NOT available or failed to retrieve for $thing_name."
  fi
}

# Search fleet index for a Thing
search_fleet_index() {
  local thing_name=$1
  echo "🔍 Searching fleet index for $thing_name..."
  aws iot search-index \
    --index-name "AWS_Things" \
    --query-string "thingName:'$thing_name'" \
    --region "$REGION" \
    --output json > index.json 2>/dev/null

  if [ $? -eq 0 ]; then
    if [ "$(jq '.things | length' index.json)" -gt 0 ]; then
      echo "✅ Fleet index data for $thing_name:"
      jq '.' index.json
    else
      echo "⚠️ No results found in fleet index for $thing_name."
    fi
  else
    echo "❌ Failed to search fleet index for $thing_name."
  fi
}

# List jobs for a Thing
list_jobs() {
  local thing_name=$1
  echo "🔍 Listing jobs for $thing_name..."
  aws iot list-jobs \
    --target-arn "arn:aws:iot:$REGION:$ACCOUNT_ID:thing/$thing_name"

  if [ $? -eq 0 ]; then
    if [ "$(jq '.jobs | length' jobs.json)" -gt 0 ]; then
      echo "✅ Jobs for $thing_name:"
      jq '.' jobs.json
    else
      echo "⚠️ No jobs found for $thing_name."
    fi
  else
    echo "❌ Failed to list jobs for $thing_name."
  fi
}

# Validate all devices
validate_devices() {
  get_all_things

  for thing_name in "${THING_NAMES[@]}"; do
    echo -e "\n🔎 Validating device: $thing_name"
    get_shadow_list "$thing_name"
    get_shadow_data "$thing_name"
    # search_fleet_index "$thing_name"
    # list_jobs "$thing_name"
  done
}

# Run the validation
validate_devices
