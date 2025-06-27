import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

FILENAME = "lala.mp3"

def upload_file(file_path, api_url, api_token):
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (Path(file_path).name, f)}
            headers = {'Authorization': f'Bearer {api_token}'}
            print(f"Uploading {file_path}...")
            response = requests.post(api_url, files=files, headers=headers)
            response.raise_for_status()
            return response.json().get('id')
    except Exception as e:
        print(f"Error uploading file: {e}")
        return None

def main():
    load_dotenv()
    api_host = os.environ['API_HOST']
    api_token = os.environ['API_TOKEN']
    
    file_path = os.path.join(os.environ['MUSIC_DIR'], FILENAME)
    uploaded_file_path = os.path.join(os.environ['UPLOADS_DIR'], 'nuno', 'temp', FILENAME)
    
    api_url = f"{api_host}/api/soundfragments/files/temp"
    upload_id = upload_file(file_path, api_url, api_token)
    
    if upload_id:
        print(f"Upload successful! ID: {upload_id}")
        print(f"File should be at: {uploaded_file_path}")
        return 0
    print("Upload failed")
    return 1

if __name__ == "__main__":
    sys.exit(main())
