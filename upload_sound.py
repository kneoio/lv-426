import os
import requests
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Get the API token from .env
api_token = os.getenv('API_TOKEN')

if not api_token:
    raise ValueError("API token not found in .env file")


def upload_file(file_path):
    """Upload a file to the sound fragments API"""
    url = "http://localhost:38707/api/soundfragments/files/null"

    # Convert file path to absolute path
    file_path = Path(file_path).absolute()

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Get the filename from the path
    filename = file_path.name

    # Prepare the files dictionary
    files = {
        'file': (filename, open(file_path, 'rb'))
    }

    # Make the request
    response = requests.post(
        url,
        headers={
            'Authorization': f'Bearer {api_token}'
        },
        files=files
    )

    if response.status_code == 200:
        print(f"File {filename} uploaded successfully!")
        return filename
    else:
        print(f"File upload failed with status code {response.status_code}")
        print("Error:", response.text)
        return None


def create_sound_fragment(filename, title, artist, genre):
    """Create a sound fragment with the uploaded file"""
    url = "http://localhost:38707/api/soundfragments/"

    # Prepare the data payload
    data = {
        "title": title,
        "artist": artist,
        "type": "SONG",
        "genre": genre,
        "newlyUploaded": [filename]
    }

    # Make the request
    response = requests.post(
        url,
        headers={
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        },
        json=data
    )

    if response.status_code == 200:
        print(f"Sound fragment created successfully!")


def main():
    # Get all audio files from the music directory
    #music_dir = Path("C:/Users/justa/Music/44")
    #music_dir = Path("C:/Users/justa/Music/44/Flevans - The Foundation (2025)")
    #music_dir = Path("C:/Users/justa/Music/44/VA - Planeta Mix Hits 2024- Winter Edition (2023)")
    music_dir = Path("C:/Users/justa/Music/44/Avicii - 2025 - Avicii Forever")
    audio_files = list(music_dir.glob("*.mp3"))

    if not audio_files:
        print("No MP3 files found in the music directory")
        return

    # Limit to first 2 files
    audio_files = audio_files[:30]
    print(f"\nFound {len(audio_files)} MP3 files")
    print("Processing first 2 files")

    # Process each audio file
    for file_path in audio_files:
        print(f"\nProcessing file: {file_path.name}")

        # Upload the file
        uploaded_filename = upload_file(file_path)
        if not uploaded_filename:
            print(f"Failed to upload {file_path.name}")
            continue

        # Create sound fragment
        # For now, we'll use the filename as title and artist
        title = file_path.stem  # Remove the .mp3 extension
        artist = "Avicii"
        genre = "House"  # You might want to add genre detection later

        result = create_sound_fragment(
            uploaded_filename,
            title,
            artist,
            genre
        )

        if result:
            print("Successfully created sound fragment")
        else:
            print("Failed to create sound fragment")


if __name__ == "__main__":
    main()
