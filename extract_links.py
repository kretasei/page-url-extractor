import argparse
from bs4 import BeautifulSoup

def extract_links(file_path, extensions):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        soup = BeautifulSoup(content, 'html.parser')
        links = []
        for tag in soup.find_all(['a', 'audio', 'video', 'source']):
            link = None
            for attr in ['href', 'src']:
                if tag.has_attr(attr):
                    link = tag[attr]
                    break
            if link and any(link.endswith(ext) for ext in extensions):
                links.append(link)
        return links

def main():
    parser = argparse.ArgumentParser(description="A simple CLI application.")
    parser.add_argument('file_path', type=str, help='Path to the HTML file')
    parser.add_argument('output_file', type=str, help='Path to the output file')
    parser.add_argument('--extensions', nargs='+', required=True, help='Filter links by file extensions')
    args = parser.parse_args()
    
    links = extract_links(args.file_path, args.extensions)
    links.sort()
    
    with open(args.output_file, 'w', encoding='utf-8') as file:
        for link in links:
            file.write(link + '\n')

if __name__ == "__main__":
    main()