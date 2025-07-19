import os
import requests
import json
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

api_host = os.getenv('API_HOST')
api_token = os.getenv('API_TOKEN')

if not api_token:
    logger.error("API token not found in .env file. Please ensure it's set.")
    exit(1)

GENRES_FILE_PATH = "genres.json"

def fetch_and_save_genres():
    """Fetch available genres from the API and save them to a JSON file."""
    url = f"{api_host}/api/genres"
    logger.info(f"Fetching genres from {url}...")
    logger.info(f"Preparing to make GET request to {url} with token {api_token[:20]}... (token truncated for log)")

    try:
        response = requests.get(
            url,
            headers={'Authorization': f'Bearer {api_token}'},
            timeout=10
        )
        logger.info(f"Request to {url} completed with status: {response.status_code}")
        response.raise_for_status()  
        logger.info("Attempting to parse JSON response...")
        genres_data = response.json()
        logger.info(f"Successfully parsed JSON response. Raw data: {genres_data}")

        genre_names = []
        if isinstance(genres_data, list) and genres_data:
            if isinstance(genres_data[0], dict) and 'name' in genres_data[0]:
                genre_names = [genre['name'] for genre in genres_data if 'name' in genre and genre['name']]
            elif isinstance(genres_data[0], str):
                genre_names = [genre for genre in genres_data if genre]
        
        if not genre_names:
            logger.warning("No genre names found or API returned an unexpected format.")
            with open(GENRES_FILE_PATH, 'w') as f:
                json.dump([], f, indent=4)
            logger.info(f"Saved empty list to {GENRES_FILE_PATH}")
            return

        with open(GENRES_FILE_PATH, 'w') as f:
            json.dump(sorted(list(set(genre_names))), f, indent=4)
        logger.info(f"Successfully fetched {len(genre_names)} genres and saved to {GENRES_FILE_PATH}")

    except requests.exceptions.RequestException as e:
        logger.error(f"Error during request to {url}: {e}")
    except ValueError: 
        logger.error(f"Error decoding JSON from response. Status: {response.status_code if 'response' in locals() else 'N/A'}, Text: {response.text if 'response' in locals() else 'N/A'}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    fetch_and_save_genres()
