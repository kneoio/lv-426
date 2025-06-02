import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the API token from .env
api_token = os.getenv('API_TOKEN')

if not api_token:
    raise ValueError("API token not found in .env file")

# API endpoint
url = "http://localhost:38707/api/soundfragments"

# Make the request with query parameters
response = requests.get(
    url,
    headers={
        'Authorization': f'Bearer {api_token}'
    },
    params={
        'limit': 100,
        'offset': 0,
        'sourceType': 'LOCAL'
    }
)

# Check response status
if response.status_code == 200:
    print("Request successful!")
    data = response.json()
    print("Response data:", data)
else:
    print(f"Request failed with status code {response.status_code}")
    print("Error:", response.text)
