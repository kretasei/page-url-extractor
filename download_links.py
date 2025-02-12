import argparse
import os
import requests
from tqdm import tqdm
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

def download_file(url, directory):
    parsed_url = urlparse(url)
    local_filename = os.path.join(directory, os.path.basename(parsed_url.path))
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
    parser.add_argument('download_directory', type=str, help='Subdirectory within the Downloads directory to save the files or an absolute path')
    parser.add_argument('--start-index', type=int, default=1, help='Index to start downloading from (1-based)')
    parser.add_argument('--prompt', action='store_true', help='Enable prompt before downloading each file')
    parser.add_argument('--parallel', type=int, default=1, help='Number of parallel downloads')
    args = parser.parse_args()
    
    if args.download_directory.startswith(f'.{os.path.sep}') or args.download_directory.startswith('./'):
        download_directory = os.path.normpath(os.path.join(os.getcwd(), args.download_directory[2:]))
    elif os.path.isabs(args.download_directory):
        download_directory = os.path.normpath(args.download_directory)
    else:
        download_directory = os.path.normpath(os.path.join(os.path.expanduser('~/Downloads'), args.download_directory))
    
    os.makedirs(download_directory, exist_ok=True)
    
    with open(args.input_file, 'r') as file:
        urls = [url.strip() for url in file.readlines()]
    
    with ThreadPoolExecutor(max_workers=args.parallel) as executor:
        future_to_url = {executor.submit(download_file, url, download_directory): url for url in urls[args.start_index - 1:]}
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                future.result()
                print(f"Downloaded {url}")
            except Exception as e:
                print(f"Error downloading {url}: {e}")
            if args.prompt:
                while True:
                    user_input = input("Type 'next' (n) to download the next file or 'stop' (s) to end: ").strip().lower()
                    if user_input == 'n':
                        break
                    elif user_input == 's':
                        print("Stopping downloads.")
                        return
                    else:
                        print("Invalid input. Please type 'n' or 's'.")

if __name__ == "__main__":
    main()