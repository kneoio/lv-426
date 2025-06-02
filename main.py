import os
import subprocess
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Get the API token from .env
api_token = os.getenv('API_TOKEN')

# API endpoint
url = "http://localhost:38707/api/soundfragments"

# Using curl
result = subprocess.run(
    ['curl',
     '--request', 'GET',
     '--url', f'{url}?limit=100&offset=0&sourceType=LOCAL',
     '--header', f'authorization: Bearer {api_token}'],
    capture_output=True, text=True
)

if result.returncode == 0:
    try:
        data = json.loads(result.stdout)
        entries = data['payload']['viewData']['entries']
        print(f"\nFound {len(entries)} entries:")
        for entry in entries:
            print(f"{entry['title']} by {entry['artist']}")
    except Exception as e:
        print(f"\nError: {str(e)}")
        print("Raw response:")
        print(result.stdout)
else:
        print("\nError:", result.stderr)
