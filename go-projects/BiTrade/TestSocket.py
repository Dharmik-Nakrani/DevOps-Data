from websocket import create_connection

auth_token = "39257bfa-753f-45c8-8d49-7a398a08a22b"
device_id = "ba4f946db27e5a66a221066920ac43b8"

url = f"wss://ws.binomo.com/?authtoken={auth_token}&device=web&device_id={device_id}&v=2&vsn=2.0.0"
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
}

try:
    ws = create_connection(url, header=headers)
    print("✅ WebSocket connected successfully!")
except Exception as e:
    print("❌ WebSocket connection failed:", e)
