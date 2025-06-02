import os
import requests
from dotenv import load_dotenv
from urllib.parse import urljoin

load_dotenv()
api_token = os.getenv('API_TOKEN')
api_host = os.getenv('API_HOST')

if not api_host:
    raise ValueError("API_HOST not found in environment variables")

def check_uploaded_sound_fragments():
    url = urljoin(api_host, "api/soundfragments")

    try:
        response = requests.get(
            url,
            headers={'Authorization': f'Bearer {api_token}'},
            params={'limit': 100, 'offset': 0, 'sourceType': 'LOCAL'},
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            entries = data['payload']['viewData']['entries']
            print(f"\nFound {len(entries)} entries:")
            
            # Handle different response formats
            if isinstance(entries, list):
                for entry in entries:
                    print(f"- Title: {entry.get('title', 'Unknown')}")
                    print(f"  Artist: {entry.get('artist', 'Unknown')}")
                    print(f"  Genre: {entry.get('genre', 'Unknown')}")
                    print(f"  Type: {entry.get('type', 'Unknown')}")
                    if 'newlyUploaded' in entry:
                        print("  Files:", entry['newlyUploaded'])
                    print()
            else:
                print("\nUnexpected response format:", entries)
        else:
            print(f"\nError: {response.status_code}")
            print("Response:", response.text)
            
    except Exception as e:
        print(f"\nError: {str(e)}")


if __name__ == "__main__":
    check_uploaded_sound_fragments()