#!/usr/bin/env python3

import os
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()


class SoundFragmentTester:
    def __init__(self, base_url="http://localhost:8080", auth_token=None):
        self.base_url = base_url.rstrip('/')
        self.api_path = "/api/soundfragments"
        self.session = requests.Session()

        if auth_token:
            self.session.headers.update({'Authorization': f'Bearer {auth_token}'})

    def test_upsert_new(self, sound_fragment_data):
        """Test creating a new sound fragment"""
        url = f"{self.base_url}{self.api_path}"

        response = self.session.post(url, json=sound_fragment_data)

        print(f"POST {url}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code == 201:
            return response.json()
        return None

    def test_upsert_existing(self, entity_id, sound_fragment_data):
        url = f"{self.base_url}{self.api_path}/{entity_id}"

        response = self.session.post(url, json=sound_fragment_data)

        print(f"POST {url}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code == 200:
            return response.json()
        return None

    def test_file_upload(self, entity_id, file_path):
        url = f"{self.base_url}{self.api_path}/files/{entity_id}"

        if not Path(file_path).exists():
            print(f"File not found: {file_path}")
            return None

        with open(file_path, 'rb') as f:
            files = {'file': (Path(file_path).name, f, 'audio/wav')}
            response = self.session.post(url, files=files)

        print(f"POST {url}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code == 200:
            return response.json()
        return None

    def test_upload_progress(self, upload_id):
        url = f"{self.base_url}{self.api_path}/upload-progress/{upload_id}"

        response = self.session.get(url)

        print(f"GET {url}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code == 200:
            return response.json()
        return None

    def test_get_by_id(self, entity_id, lang="en"):
        url = f"{self.base_url}{self.api_path}/{entity_id}"
        params = {'lang': lang}
        response = self.session.get(url, params=params)

        print(f"GET {url}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code == 200:
            return response.json()
        return None

    def test_get_file(self, entity_id, filename):
        """Test getting uploaded file"""
        url = f"{self.base_url}{self.api_path}/files/{entity_id}/{filename}"

        response = self.session.get(url)

        print(f"GET {url}")
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"Content-Length: {response.headers.get('Content-Length', 'N/A')}")

        if response.status_code == 200:
            return response.content
        return None


def run_upload_only(tester, test_audio_file):
    """Run only the file upload test"""
    print("=== Upload Only Test ===\n")

    if not Path(test_audio_file).exists():
        print(f"Test audio file not found: {test_audio_file}")
        print("Please update TEST_AUDIO_FILE variable with path to existing audio file")
        return

    print("1. Testing file upload...")
    temp_entity_id = "temp"
    upload_result = tester.test_file_upload(temp_entity_id, test_audio_file)

    if not upload_result or not upload_result.get('id'):
        print("File upload failed.")
        return

    upload_id = upload_result['id']
    print(f"Upload started with ID: {upload_id}")

    print("\n2. Monitoring upload progress...")
    while True:
        time.sleep(0.5)
        progress_data = tester.test_upload_progress(upload_id)

        if progress_data:
            status = progress_data.get('status', 'unknown')
            percentage = progress_data.get('percentage', 0)

            print(f"\rProgress: {percentage}% - Status: {status}", end='', flush=True)

            if status == 'finished':
                print("\nUpload completed successfully!")
                break
            elif status == 'error':
                print("\nUpload failed!")
                return
        else:
            print("\nCould not get upload progress")
            break

    print("\n=== Upload Only Test Completed ===")


def run_full_flow(tester, test_audio_file, sound_fragment_data):
    """Run the complete flow including upload and upsert"""
    print("=== Full Flow Test ===\n")

    print("1. Testing get template for new sound fragment...")
    template = tester.test_get_by_id("new")
    print()

    print("2. Testing file upload...")

    if not Path(test_audio_file).exists():
        print(f"Test audio file not found: {test_audio_file}")
        print("Please update TEST_AUDIO_FILE variable with path to existing audio file")
        return

    temp_entity_id = "temp"
    upload_result = tester.test_file_upload(temp_entity_id, test_audio_file)

    if not upload_result or not upload_result.get('id'):
        print("File upload failed. Cannot proceed with upsert.")
        return

    upload_id = upload_result['id']
    print(f"Upload started with ID: {upload_id}")
    print("\n3. Monitoring upload progress...")
    progress_data = None
    while True:
        time.sleep(0.5)
        progress_data = tester.test_upload_progress(upload_id)

        if progress_data:
            status = progress_data.get('status', 'unknown')
            percentage = progress_data.get('percentage', 0)

            print(f"\rProgress: {percentage}% - Status: {status}", end='', flush=True)

            if status == 'finished':
                print("\nUpload completed successfully!")
                break
            elif status == 'error':
                print("\nUpload failed!")
                return
        else:
            print("\nCould not get upload progress")
            break

    print()

    print("4. Testing upsert (create new) with uploaded file...")
    created_fragment = tester.test_upsert_new(sound_fragment_data)

    if not created_fragment:
        print("Failed to create sound fragment.")
        return

    entity_id = created_fragment.get('id')
    if not entity_id:
        print("No ID returned from create.")
        return

    print(f"Created fragment with ID: {entity_id}\n")
    print("5. Testing get by ID...")
    fragment = tester.test_get_by_id(entity_id)
    print()

    print("6. Testing file download...")
    filename = Path(test_audio_file).name
    file_content = tester.test_get_file(entity_id, filename)

    if file_content:
        print(f"Successfully downloaded file, size: {len(file_content)} bytes")
    print()
    print("7. Testing upsert (update existing)...")
    sound_fragment_data['title'] = "sleeping lala - updated"
    sound_fragment_data['genre'] = "Jazz Funk"
    updated_fragment = tester.test_upsert_existing(entity_id, sound_fragment_data)
    print()

    print("=== Full Flow Test Completed ===")


def main():
    BASE_URL = os.getenv('API_HOST', 'http://localhost:8080')
    AUTH_TOKEN = os.getenv('API_TOKEN')
    TEST_AUDIO_FILE = 'C:/Users/justa/Music/I_am_not_what_I_was.wav'

    # Toggle switch - set to True for upload only, False for full flow
    UPLOAD_ONLY = True

    print(f"Using API Host: {BASE_URL}")
    print(f"Using Token: {AUTH_TOKEN[:20]}..." if AUTH_TOKEN and len(AUTH_TOKEN) > 20 else f"Using Token: {AUTH_TOKEN}")
    print(f"Test Audio File: {TEST_AUDIO_FILE}")
    print(f"Mode: {'Upload Only' if UPLOAD_ONLY else 'Full Flow'}")
    print()

    tester = SoundFragmentTester(BASE_URL, AUTH_TOKEN)

    sound_fragment_data = {
        "title": "sleeping lala",
        "artist": "luliu",
        "type": "SONG",
        "genre": "Funk",
        "newlyUploaded": [
            Path(TEST_AUDIO_FILE).name
        ]
    }

    if UPLOAD_ONLY:
        run_upload_only(tester, TEST_AUDIO_FILE)
    else:
        run_full_flow(tester, TEST_AUDIO_FILE, sound_fragment_data)


if __name__ == "__main__":
    try:
        from dotenv import load_dotenv
    except ImportError:
        print("python-dotenv not installed. Install it with: pip install python-dotenv")
        exit(1)

    main()