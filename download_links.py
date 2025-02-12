import argparse
import os
import requests
from tqdm import tqdm
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def download_file(url, local_filename, min_speed, retry_delay, resume_header):
    file_mode = 'ab'
    existing_file_size = 0
    max_retries = 5
    retries = 0
    delay_factor = 1.2

    while retries < max_retries:
        try:
            with requests.get(url, stream=True, headers=resume_header, timeout=30) as r:
                if r.status_code == 416:  # Range Not Satisfiable
                    print(f"{local_filename} is already fully downloaded.")
                    return local_filename
                r.raise_for_status()
                total_size = int(r.headers.get('content-length', 0)) + existing_file_size
                with open(local_filename, file_mode) as f, tqdm(
                    desc=local_filename,
                    total=total_size,
                    initial=existing_file_size,
                    unit='iB',
                    unit_scale=True,
                    unit_divisor=1024,
                ) as bar:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            size = f.write(chunk)
                            bar.update(size)
                            rate = bar.format_dict['rate']
                            if rate is not None:
                                speed = rate / 1024  # Speed in KiB/s
                                if speed < min_speed:
                                    print(f"Download speed dropped below {min_speed} KiB/s. Retrying in {retry_delay} seconds...")
                                    retries += 1
                                    time.sleep(retry_delay)
                                    retry_delay *= delay_factor
                                    break
                    else:
                        return local_filename
        except requests.exceptions.RequestException as e:
            print(f"Error downloading {url}: {e}. Retrying in {retry_delay} seconds...")
            retries += 1
            time.sleep(retry_delay)
            retry_delay *= delay_factor

    print(f"Failed to download {url} after {max_retries} attempts.")
    return None

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
    
    input_file_base = os.path.splitext(os.path.basename(args.input_file))[0]
    failed_log_file = f"./logs/{input_file_base}_failed_downloads.txt"
    os.makedirs('logs', exist_ok=True)
    
    with open(failed_log_file, 'a') as failed_log:
        with ThreadPoolExecutor(max_workers=args.parallel) as executor:
            future_to_url = {executor.submit(download_file, url, os.path.join(download_directory, os.path.basename(urlparse(url).path)), 50, 5, {}): url for url in urls[args.start_index - 1:]}
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result()
                    if result:
                        print(f"Downloaded {url}")
                    else:
                        failed_log.write(f"{url}\n")
                except Exception as e:
                    print(f"Error downloading {url}: {e}")
                    failed_log.write(f"{url}\n")
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