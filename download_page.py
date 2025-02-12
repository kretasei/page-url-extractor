import argparse
import os
import requests
from bs4 import BeautifulSoup
import re

def sanitize_filename(filename):
    # Remove invalid characters for filenames
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def download_page(url, dest_dir):
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        content = response.text
        soup = BeautifulSoup(content, 'html.parser')
        title = soup.title.string if soup.title else "index"
        title = sanitize_filename(title)
        filename = f"{title}.html"
        filepath = os.path.join(dest_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Downloaded {url} as {filepath}")
    except Exception as e:
        print(f"Error downloading {url}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Download the index (HTML) of a page")
    parser.add_argument("url", help="URL to download")
    parser.add_argument("dest_dir", help="Destination directory to save the downloaded file")
    args = parser.parse_args()

    os.makedirs(args.dest_dir, exist_ok=True)
    download_page(args.url, args.dest_dir)

if __name__ == "__main__":
    main()