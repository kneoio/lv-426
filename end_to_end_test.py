#!/usr/bin/env python3
"""
End-to-End Test for SoundFragment File Upload and Retrieval Flow

This script tests the complete flow:
1. Upload a file to temp directory
2. Create/upsert SoundFragment with file reference
3. Retrieve the SoundFragment and verify uploadedFiles list
4. Access the attached file by UUID (simulate frontend click)
5. Verify file exists and can be downloaded

Simulates the complete user experience from upload to file access.
"""

import requests
import json
import os
from pathlib import Path
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Configuration
API_HOST = os.getenv('API_HOST', 'http://localhost:38707')
API_TOKEN = os.getenv('API_TOKEN')
TEST_FILE = r"C:\Users\justa\Music\lala.mp3"

# Headers for authenticated requests
headers = {
    'Authorization': f'Bearer {API_TOKEN}',
    'Accept': 'application/json'
}

def print_step(step_num, description):
    """Print a formatted step header"""
    print(f"\n{'='*60}")
    print(f"STEP {step_num}: {description}")
    print(f"{'='*60}")

def print_success(message):
    """Print success message in green"""
    print(f" {message}")

def print_error(message):
    """Print error message in red"""
    print(f" {message}")

def print_info(message):
    """Print info message"""
    print(f"  {message}")

def upload_file():
    """Step 1: Upload file to temp directory"""
    print_step(1, "Upload File to Temp Directory")
    
    if not os.path.exists(TEST_FILE):
        print_error(f"Test file not found: {TEST_FILE}")
        return None
    
    file_name = os.path.basename(TEST_FILE)
    print_info(f"Uploading file: {file_name}")
    
    with open(TEST_FILE, 'rb') as f:
        files = {'file': (file_name, f, 'audio/mpeg')}
        response = requests.post(
            f'{API_HOST}/api/soundfragments/files/temp',
            files=files,
            headers={'Authorization': f'Bearer {API_TOKEN}'}
        )
    
    if response.status_code == 200:
        print_success(f"File uploaded successfully")
        print_info(f"Response: {response.text}")
        return file_name
    else:
        print_error(f"Upload failed: {response.status_code} - {response.text}")
        return None

def create_sound_fragment(file_name):
    """Step 2: Create SoundFragment with file reference"""
    print_step(2, "Create SoundFragment with File Reference")
    
    payload = {
        "title": "End-to-End Test Fragment",
        "artist": "Test Artist",
        "genre": "Test Genre",
        "album": "Test Album",
        "newlyUploaded": [file_name]  # Reference the uploaded file
    }
    
    print_info(f"Creating SoundFragment with payload:")
    print(json.dumps(payload, indent=2))
    
    response = requests.post(
        f'{API_HOST}/api/sound-fragments',
        json=payload,
        headers=headers
    )
    
    if response.status_code in [200, 201]:
        result = response.json()
        entity_id = result.get('id')
        print_success(f"SoundFragment created with ID: {entity_id}")
        print_info(f"Response: {json.dumps(result, indent=2)}")
        return entity_id
    else:
        print_error(f"Creation failed: {response.status_code} - {response.text}")
        return None

def retrieve_sound_fragment(entity_id):
    """Step 3: Retrieve SoundFragment and verify uploadedFiles"""
    print_step(3, "Retrieve SoundFragment and Verify uploadedFiles")
    
    print_info(f"Retrieving SoundFragment with ID: {entity_id}")
    
    response = requests.get(
        f'{API_HOST}/api/sound-fragments/{entity_id}',
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        uploaded_files = result.get('uploadedFiles', [])
        
        print_success(f"SoundFragment retrieved successfully")
        print_info(f"Number of uploaded files: {len(uploaded_files)}")
        
        if uploaded_files:
            print_info("Uploaded files details:")
            for i, file_info in enumerate(uploaded_files):
                print(f"  File {i+1}:")
                print(f"    - ID: {file_info.get('id')}")
                print(f"    - Original Name: {file_info.get('fileOriginalName')}")
                print(f"    - MIME Type: {file_info.get('mimeType')}")
                print(f"    - Storage Type: {file_info.get('storageType')}")
                print(f"    - File Key: {file_info.get('fileKey')}")
        else:
            print_error("No uploaded files found in response!")
            
        return result
    else:
        print_error(f"Retrieval failed: {response.status_code} - {response.text}")
        return None

def access_file_by_uuid(uploaded_files):
    """Step 4: Access attached file by UUID (simulate frontend click)"""
    print_step(4, "Access Attached File by UUID (Simulate Frontend Click)")
    
    if not uploaded_files:
        print_error("No uploaded files to access")
        return False
    
    # Get the first file's UUID
    first_file = uploaded_files[0]
    file_id = first_file.get('id')
    file_name = first_file.get('fileOriginalName')
    
    print_info(f"Attempting to access file: {file_name} (ID: {file_id})")
    
    # Try to download the file by UUID
    response = requests.get(
        f'{API_HOST}/api/sound-fragments/file/{file_id}',
        headers=headers
    )
    
    if response.status_code == 200:
        content_length = len(response.content)
        content_type = response.headers.get('Content-Type', 'unknown')
        
        print_success(f"File accessed successfully!")
        print_info(f"Content-Type: {content_type}")
        print_info(f"Content-Length: {content_length} bytes")
        
        # Verify it's actually file content (not an error page)
        if content_length > 1000:  # Audio files should be substantial
            print_success("File content appears to be valid (substantial size)")
            return True
        else:
            print_error(f"File content seems too small ({content_length} bytes)")
            return False
    else:
        print_error(f"File access failed: {response.status_code} - {response.text}")
        return False

def verify_file_system_storage(entity_id, file_name):
    """Step 5: Verify file exists in file system"""
    print_step(5, "Verify File Exists in File System")
    
    # Construct expected file path
    expected_path = Path(f"C:/Users/justa/tmp/broadcaster/controller-uploads/sound-fragments-controller/nuno/{entity_id}/{file_name}")
    
    print_info(f"Checking file system path: {expected_path}")
    
    if expected_path.exists():
        file_size = expected_path.stat().st_size
        print_success(f"File exists in file system!")
        print_info(f"File size: {file_size} bytes")
        return True
    else:
        print_error(f"File not found in expected location: {expected_path}")
        
        # Check if it might be in temp directory still
        temp_path = Path(f"C:/Users/justa/tmp/broadcaster/controller-uploads/sound-fragments-controller/nuno/temp/{file_name}")
        if temp_path.exists():
            print_error(f"File still in temp directory: {temp_path}")
        
        return False

def main():
    """Run the complete end-to-end test"""
    print(" Starting End-to-End SoundFragment File Upload Test")
    print(f"API Host: {API_HOST}")
    print(f"Test File: {TEST_FILE}")
    
    # Step 1: Upload file
    file_name = upload_file()
    if not file_name:
        return
    
    # Step 2: Create SoundFragment
    entity_id = create_sound_fragment(file_name)
    if not entity_id:
        return
    
    # Small delay to ensure processing is complete
    print_info("Waiting 2 seconds for processing to complete...")
    time.sleep(2)
    
    # Step 3: Retrieve SoundFragment
    fragment_data = retrieve_sound_fragment(entity_id)
    if not fragment_data:
        return
    
    uploaded_files = fragment_data.get('uploadedFiles', [])
    
    # Step 4: Access file by UUID
    file_access_success = access_file_by_uuid(uploaded_files)
    
    # Step 5: Verify file system storage
    file_system_success = verify_file_system_storage(entity_id, file_name)
    
    # Final summary
    print_step("SUMMARY", "End-to-End Test Results")
    
    results = {
        "File Upload": " SUCCESS" if file_name else " FAILED",
        "SoundFragment Creation": " SUCCESS" if entity_id else " FAILED",
        "File Metadata Retrieval": " SUCCESS" if uploaded_files else " FAILED",
        "File Access by UUID": " SUCCESS" if file_access_success else " FAILED",
        "File System Storage": " SUCCESS" if file_system_success else " FAILED"
    }
    
    for test, result in results.items():
        print(f"{test}: {result}")
    
    all_success = all("SUCCESS" in result for result in results.values())
    
    if all_success:
        print("\n ALL TESTS PASSED! The complete flow is working correctly.")
    else:
        print("\n SOME TESTS FAILED! Check the results above for details.")
    
    return all_success

if __name__ == "__main__":
    main()
