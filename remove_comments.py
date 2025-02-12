import re

def remove_comments_from_html(file_path, output_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Remove HTML comments
    cleaned_content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
    
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(cleaned_content)

if __name__ == "__main__":
    input_file = 'pages/trok/F. C. Yee - Avatar, The Rise of Kyoshi (The Last Airbender) Audiobook - Goldenaudiobooks.html'
    output_file = 'pages/trok/F. C. Yee - Avatar, The Rise of Kyoshi (The Last Airbender) Audiobook - Goldenaudiobooks_cleaned.html'
    remove_comments_from_html(input_file, output_file)
    print(f"Comments removed. Cleaned file saved as {output_file}")