import json
import os
import requests

with open('soundfragment_data.json', 'r') as f:
    data = json.load(f)

api_host = os.environ["API_HOST"]
api_key = os.environ["API_TOKEN"]

for file_info in data['uploadedFiles']:
    print(f"\nChecking access to {file_info['name']} (ID: {file_info['id']})...")
    url = f"{api_host}/api/soundfragments/files/{data['id']}/{file_info['id']}"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        print(f"Content-Length: {response.headers.get('content-length')} bytes")
    except Exception as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Status code: {e.response.status_code}")
            print(f"Response: {e.response.text}")
        raise
