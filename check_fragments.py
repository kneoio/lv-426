import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_token = os.getenv('API_TOKEN')

def check_uploaded_sound_fragments():
    url = "http://localhost:38707/api/soundfragments"
    
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
            for entry in entries:
                print(f"{entry['title']} by {entry['artist']}")
        else:
            print(f"\nError: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"\nError: {str(e)}")

check_uploaded_sound_fragments()
        print(data)  # Print parsed data
        
        # Handle different response formats
        if isinstance(data, list):
            print("\nFormatted fragments:")
            for fragment in data:
                print(f"- Title: {fragment.get('title', 'Unknown')}")
                print(f"  Artist: {fragment.get('artist', 'Unknown')}")
                print(f"  Genre: {fragment.get('genre', 'Unknown')}")
                print(f"  Type: {fragment.get('type', 'Unknown')}")
                print("  Files:", fragment.get('newlyUploaded', []))
                print()
        else:
            # If we get a single string or other format
            print("\nResponse data:", data)
    else:
        print(f"Failed to check sound fragments with status code {response.status_code}")
        print("Error:", response.text)

if __name__ == "__main__":
    check_uploaded_sound_fragments()
