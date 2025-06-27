import os
import sys
import json
import requests
from dotenv import load_dotenv

def save_response_data(data, filename='soundfragment_data.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def upsert_soundfragment(api_host, api_key, payload=None):
    if payload is None:
        payload = {
            "title": "sleeping lala",
            "artist": "luliu",
            "genre": "Funk",
            "type": "SONG",
            "newlyUploaded": ["lala.mp3"]
        }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        f"{api_host}/api/soundfragments/",
        json=payload,
        headers=headers
    )
    
    if response.status_code in (200, 201):
        data = response.json()
        save_response_data(data)
        return data
    
    raise Exception(f"Upsert failed with status {response.status_code}: {response.text}")

def main():
    load_dotenv()
    
    try:
        api_host = os.environ["API_HOST"]
        api_key = os.environ["API_TOKEN"]
        
        data = upsert_soundfragment(api_host, api_key)
        
        print(f"Status: {200 if data else 500}")
        print(f"Response: {json.dumps(data, indent=2)}")
        print("Upsert successful!")
        print(f"Saved response data to soundfragment_data.json")
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())