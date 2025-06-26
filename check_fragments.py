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
    print(f"\nChecking sound fragments at: {url}")
    print(f"API Token: {api_token[:10]}... (truncated for security)")
    print("\n")
    
    try:
        print("Request Parameters:", {'limit': 100, 'offset': 0, 'sourceType': 'LOCAL'})
        print("\n")
        print("Request Headers:", {'Authorization': f'Bearer {api_token[:10]}...'})
        print("\n")
        
        response = requests.get(
            url,
            headers={'Authorization': f'Bearer {api_token}'},
            params={'limit': 100, 'offset': 0, 'sourceType': 'LOCAL'},
            timeout=10
        )

        print("\nResponse Status Code:", response.status_code)
        print("\n")
        print("Response Headers:", response.headers)
        print("\n")
        print("Response Text:", response.text)
        print("\n")

        if response.status_code == 200:
            data = response.json()
            print(f"\nResponse data: {data}")  # Show full response data
            
            if 'payload' in data and 'viewData' in data['payload'] and 'entries' in data['payload']['viewData']:
                entries = data['payload']['viewData']['entries']
                print(f"\nFound {len(entries)} sound fragments:")
                
                if isinstance(entries, list):
                    for i, entry in enumerate(entries, 1):
                        print(f"\nFragment {i}:")
                        print(f"Title: {entry.get('title', 'Unknown')}")
                        print(f"Artist: {entry.get('artist', 'Unknown')}")
                        print(f"Genre: {entry.get('genre', 'Unknown')}")
                        print(f"Type: {entry.get('type', 'Unknown')}")
                        if 'newlyUploaded' in entry:
                            print("Files:", entry['newlyUploaded'])
                        print("-" * 40)
            print(f"\nResponse data: {data}")  # Show full response data
            
            if 'payload' in data and 'viewData' in data['payload'] and 'entries' in data['payload']['viewData']:
                entries = data['payload']['viewData']['entries']
                print(f"\nFound {len(entries)} sound fragments:")
                
                if isinstance(entries, list):
                    for i, entry in enumerate(entries, 1):
                        print(f"\nFragment {i}:")
                        print(f"Title: {entry.get('title', 'Unknown')}")
                        print(f"Artist: {entry.get('artist', 'Unknown')}")
                        print(f"Genre: {entry.get('genre', 'Unknown')}")
                        print(f"Type: {entry.get('type', 'Unknown')}")
                        if 'newlyUploaded' in entry:
                            print("Files:", entry['newlyUploaded'])
                        print("-" * 40)
                else:
                    print("\nUnexpected entries format:")
                    print(entries)
            else:
                print("\nUnexpected response structure:")
                print(data)
        else:
            print(f"\nError: {response.status_code}")
            print("Response:", response.text)
            
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        print("\nDetailed error:")
        print(traceback.format_exc())


if __name__ == "__main__":
    check_uploaded_sound_fragments()