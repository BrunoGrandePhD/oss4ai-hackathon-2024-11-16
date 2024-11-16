import argparse
import mimetypes
import os
from pathlib import Path

import requests


def upload_images(folder_path: str, api_url: str) -> None:
    """
    Upload all images from the specified folder to the API endpoint

    Args:
        folder_path: Path to folder containing images
        api_url: URL of the API endpoint
    """
    # Convert string path to Path object
    image_dir = Path(folder_path)

    # Ensure the directory exists
    if not image_dir.exists():
        raise FileNotFoundError(f"Directory not found: {folder_path}")

    # Get all files from the directory
    image_files = [f for f in image_dir.iterdir() if f.is_file()]

    # Common image extensions
    valid_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

    for image_path in image_files:
        # Skip files that aren't images
        if image_path.suffix.lower() not in valid_extensions:
            print(f"Skipping non-image file: {image_path.name}")
            continue

        # Get the mime type
        mime_type, _ = mimetypes.guess_type(str(image_path))

        try:
            with open(image_path, "rb") as img_file:
                files = {"file": (image_path.name, img_file, mime_type)}

                # Send POST request to API
                response = requests.post(api_url, files=files)

                if response.status_code == 200:
                    print(f"Successfully uploaded: {image_path.name}")
                else:
                    print(
                        f"Failed to upload {image_path.name}. Status code: {response.status_code}"
                    )
                    print(f"Response: {response.text}")

        except Exception as e:
            print(f"Error uploading {image_path.name}: {str(e)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Upload images from a folder to an API endpoint"
    )
    parser.add_argument("folder", help="Path to the folder containing images")
    args = parser.parse_args()

    # API endpoint configuration
    API_ENDPOINT = "http://localhost:5000/upload_image"

    upload_images(args.folder, API_ENDPOINT)
