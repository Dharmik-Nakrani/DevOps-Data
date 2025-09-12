import google
from google.auth.transport.requests import Request
from google.oauth2 import service_account

# Path to your Firebase service account JSON file
service_account_file = './healtech-s1-uat-383df7c33ca8.json'
# service_account_file = './healtech-s1-uat-firebase-adminsdk-fbsvc-5cb8d91936.json'

# Load credentials from the service account
credentials = service_account.Credentials.from_service_account_file(
    service_account_file, scopes=["https://www.googleapis.com/auth/firebase.messaging"]
)

# Refresh the credentials to get the access token
credentials.refresh(Request())

# Get the access token
access_token = credentials.token
print("Access Token:", access_token)