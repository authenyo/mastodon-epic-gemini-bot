#!/usr/bin/env python3
"""
Danbooru Image Updater Script
This script fetches random yaoi images from Danbooru and updates a local file
every 30 seconds.
"""

import os
import time
import random
import requests
from PIL import Image
from io import BytesIO
import json

# Configuration
TARGET_FILE = "./image.png"
UPDATE_INTERVAL = 30  # seconds
TAGS = "yaoi rating:general"
MAX_RETRIES = 3
BACKOFF_TIME = 5  # seconds

# Danbooru API configuration
# You can optionally set these to your account credentials
# for higher API limits
API_KEY = os.getenv("DANBOORU_API_KEY")  # Your API key
USERNAME = os.getenv("DANBOORU_USERNAME")  # Your username
BASE_URL = "https://danbooru.donmai.us"

def get_auth_params():
    """Return authentication parameters if credentials are provided"""
    if USERNAME and API_KEY:
        return {"login": USERNAME, "api_key": API_KEY}
    return {}

def fetch_image_urls(page=1):
    """Fetch a list of image URLs matching the tags"""
    params = {
        "tags": TAGS,
        "limit": 20,  # Request multiple posts to pick a random one
        "page": page,
    }
    params.update(get_auth_params())

    url = f"{BASE_URL}/posts.json"

    try:
        response = requests.get(url, params=params)

        if response.status_code == 200:
            posts = response.json()
            # Filter posts that have a file URL
            valid_posts = [post for post in posts if 'file_url' in post]
            return valid_posts
        else:
            print(f"API request failed: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return []
    except Exception as e:
        print(f"Error fetching posts: {e}")
        return []

def get_random_image():
    """Get a random image from Danbooru matching the tags"""
    for attempt in range(MAX_RETRIES):
        try:
            # Try different pages to increase randomness
            page = random.randint(1, 5)
            posts = fetch_image_urls(page)

            if not posts:
                print(f"No posts found on page {page}, trying another approach...")
                # Try the first page as fallback
                if page != 1:
                    posts = fetch_image_urls(1)

            if posts:
                # Select a random post from the results
                post = random.choice(posts)
                file_url = post['file_url']
                print(f"Found image: ID {post.get('id')} - {os.path.basename(file_url)}")

                # Download the image
                response = requests.get(file_url)
                if response.status_code == 200:
                    return response.content
                else:
                    print(f"Failed to download image: HTTP {response.status_code}")
            else:
                print("No suitable posts found.")

            # Add backoff time between retries
            if attempt < MAX_RETRIES - 1:
                backoff = BACKOFF_TIME * (attempt + 1)
                print(f"Backing off for {backoff} seconds before retry...")
                time.sleep(backoff)

        except Exception as e:
            print(f"Error in attempt {attempt+1}: {e}")
            time.sleep(BACKOFF_TIME)

    return None

def save_as_png(image_data, target_path):
    """Convert image to PNG and save it to the specified path"""
    try:
        img = Image.open(BytesIO(image_data))

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(target_path), exist_ok=True)

        # Save as PNG
        img.save(target_path, "PNG")
        print(f"Image saved to {target_path}")
        return True
    except Exception as e:
        print(f"Error saving image: {e}")
        return False

def main():
    """Main function to run the image updater"""
    print(f"Starting Danbooru Image Updater")
    print(f"Images will be saved to {TARGET_FILE}")
    print(f"Update interval: {UPDATE_INTERVAL} seconds")
    print(f"Using tags: {TAGS}")

    while True:
        try:
            print("\nFetching new image...")
            image_data = get_random_image()

            if image_data:
                save_as_png(image_data, TARGET_FILE)
            else:
                print("Failed to fetch a valid image after multiple attempts.")

            print(f"Waiting {UPDATE_INTERVAL} seconds before next update...")
            time.sleep(UPDATE_INTERVAL)

        except KeyboardInterrupt:
            print("\nShutting down...")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
            print(f"Retrying in {UPDATE_INTERVAL} seconds...")
            time.sleep(UPDATE_INTERVAL)

if __name__ == "__main__":
    main()
