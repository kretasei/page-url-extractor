import argparse
from bs4 import BeautifulSoup

def extract_links(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
        soup = BeautifulSoup(content, 'html.parser')
        links = [a['href'] for a in soup.find_all('a', href=True)]
        return links

def main():
    parser = argparse.ArgumentParser(description="A simple CLI application.")
    parser.add_argument('file_path', type=str, help='Path to the HTML file')
    parser.add_argument('output_file', type=str, help='Path to the output file')
    args = parser.parse_args()
    
    links = extract_links(args.file_path)
    links.sort()
    
    with open(args.output_file, 'w') as file:
        for link in links:
            file.write(f"{link}\n")

if __name__ == "__main__":
    main()