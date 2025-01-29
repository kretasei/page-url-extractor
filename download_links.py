import argparse
import os
import requests
from tqdm import tqdm

def download_file(url, directory):
    local_filename = os.path.join(directory, url.split('/')[-1])
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        total_size = int(r.headers.get('content-length', 0))
        with open(local_filename, 'wb') as f, tqdm(
            desc=local_filename,
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for chunk in r.iter_content(chunk_size=8192):
                size = f.write(chunk)
                bar.update(size)
    return local_filename

def main():
    parser = argparse.ArgumentParser(description="Download files from a list of URLs.")
    parser.add_argument('input_file', type=str, help='Path to the input file containing URLs')
    parser.add_argument('download_subdirectory', type=str, help='Subdirectory within the Downloads directory to save the files')
    parser.add_argument('--start-index', type=int, default=0, help='Index to start downloading from')
    args = parser.parse_args()
    
    download_directory = os.path.join(os.path.expanduser('~/Downloads'), args.download_subdirectory)
    os.makedirs(download_directory, exist_ok=True)
    
    with open(args.input_file, 'r') as file:
        urls = file.readlines()
    
    for index, url in enumerate(urls):
        if index < args.start_index:
            continue
        url = url.strip()
        if url:
            print(f"Downloading {url}...")
            download_file(url, download_directory)
            print(f"Downloaded {url}")
            input("Press Enter to download the next file...")

if __name__ == "__main__":
    main()