import firebase_admin
from firebase_admin import credentials, firestore
import json
from datetime import datetime
# Initialize the Firebase app
cred = credentials.Certificate("/home/dharmik-healtech/Documents/Other-Docs/Credentials/foundspace-prod-serviceaccount-firebase.json")
firebase_admin.initialize_app(cred)

# Initialize Firestore client
db = firestore.client()

# Example: Get all user documents from the "users" collection
# def serialize_firestore_data(obj):
#     if isinstance(obj, dict):
#         return {k: serialize_firestore_data(v) for k, v in obj.items()}
#     elif isinstance(obj, list):
#         return [serialize_firestore_data(v) for v in obj]
#     elif isinstance(obj, datetime):
#         return obj.isoformat()
#     else:
#         return obj

# def get_all_users():
#     users_ref = db.collection('users')
#     docs = users_ref.stream()
#     user_data = {doc.id: serialize_firestore_data(doc.to_dict()) for doc in docs}
#     return user_data

# def save_to_json(data, filename="users_data.json"):
#     with open(filename, "w") as f:
#         json.dump(data, f, indent=4)
#     print(f"Saved {len(data)} users to {filename}")

# if __name__ == "__main__":
#     users = get_all_users()
#     save_to_json(users)



# def serialize_datetime(obj):
#     if isinstance(obj, datetime):
#         return obj.isoformat()
#     return obj

# def get_all_dobs():
#     users_ref = db.collection('users')
#     docs = users_ref.stream()

#     dob_data = {}
#     for doc in docs:
#         user = doc.to_dict()
#         dob = user.get("DOB") or user.get("dob")  # handle possible key case variations
#         dob_data[doc.id] = serialize_datetime(dob) if dob else None

#     return dob_data

# def save_dobs_to_json(data, filename="user_data_dob.json"):
#     with open(filename, "w") as f:
#         json.dump(data, f, indent=4)
#     print(f"Saved DOBs of {len(data)} users to {filename}")

# if __name__ == "__main__":
#     dob_dict = get_all_dobs()
#     save_dobs_to_json(dob_dict)


def get_all_goals():
    users_ref = db.collection('users')
    docs = users_ref.stream()

    goals_data = {}
    for doc in docs:
        user = doc.to_dict()
        goals = user.get("goals")
        goals_data[doc.id] = goals

    return goals_data

def save_goals_to_json(data, filename="user_data_goals.json"):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Saved goals of {len(data)} users to {filename}")

if __name__ == "__main__":
    goals_dict = get_all_goals()
    save_goals_to_json(goals_dict)