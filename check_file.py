#!/usr/bin/env python3

import requests
import os
from dotenv import load_dotenv

load_dotenv()

def check_uploaded_file():
    """Check if the uploaded file exists and is accessible via the API"""
    
    BASE_URL = os.getenv('API_HOST', 'http://localhost:38707')
    AUTH_TOKEN = os.getenv('API_TOKEN')

    session = requests.Session()
    if AUTH_TOKEN:
        session.headers.update({'Authorization': f'Bearer {AUTH_TOKEN}'})

    # Try to access the uploaded file directly
    filename = 'I_am_not_what_I_was.wav'
    entity_id = 'temp'
    file_url = f'{BASE_URL}/api/soundfragments/files/{entity_id}/{filename}'

    print('=== File Check Results ===')
    print(f'URL: {file_url}')
    
    try:
        response = session.get(file_url)
        print(f'Status: {response.status_code}')
        
        if response.status_code == 200:
            size = len(response.content)
            content_type = response.headers.get('Content-Type', 'N/A')
            print(f'SUCCESS: File found! Size: {size} bytes, Type: {content_type}')
            return True
        elif response.status_code == 404:
            print('ERROR: File not found (404)')
            return False
        else:
            print(f'ERROR: Status {response.status_code}')
            print(f'Response: {response.text[:100]}...')
            return False
            
    except Exception as e:
        print(f'ERROR: Request failed - {str(e)}')
        return False

if __name__ == "__main__":
    check_uploaded_file()
