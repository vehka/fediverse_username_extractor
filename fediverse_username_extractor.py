import sys
import re
import os
import subprocess

def convert_url_to_username(url):
    """
    Converts a Fediverse URL to a username format.
    Examples: 
    - https://instan.ce/@user -> @user@instan.ce
    - https://small.town/@user/ -> @user@small.town

    Args:
        url: The Fediverse URL.

    Returns:
        A properly formatted Fediverse username.
    """
    # Extract the domain and username from the URL
    url_pattern = r'https?://([^/]+)/@([^/\s]+)/?'
    match = re.match(url_pattern, url)
    if match:
        domain, username = match.groups()
        # Clean up username if it ends with a trailing slash or other characters
        username = username.rstrip('/')
        return f"@{username}@{domain}"
    return None

def extract_fediverse_usernames(text):
    """
    Extracts fediverse usernames from a given text using regular expressions.
    Handles both standard username format (@user@instance) and URL format.

    Args:
        text: The input text.

    Returns:
        A set of unique fediverse usernames.
    """
    # Pattern for standard username format - only allow word chars, dots, and underscores in usernames
    username_pattern = r'@[\w._-]+@[\w.-]+\w+'
    # Pattern for URL format (e.g., https://instan.ce/@username)
    url_pattern = r'https?://[^/\s]+/@[^/\s]+/?'
    
    usernames = set()
    
    # Find standard format usernames
    standard_usernames = re.findall(username_pattern, text)
    usernames.update(standard_usernames)
    
    # Find and convert URL format usernames
    url_matches = re.findall(url_pattern, text)
    for url in url_matches:
        username = convert_url_to_username(url)
        if username:
            usernames.add(username)
    
    return usernames

def clean_usernames(usernames):
    """
    Cleans usernames by removing special characters and ensuring proper format.

    Args:
        usernames: A list of usernames.

    Returns:
        A list of cleaned usernames.
    """
    cleaned_usernames = []
    for username in usernames:
        # Split the username into parts
        if not username.count('@') == 2:
            continue
            
        parts = username.split('@')
        if len(parts) != 3:
            continue
            
        # Clean the username part (middle part) - only allow alphanumeric, dots, underscores, and hyphens
        cleaned_user = re.sub(r'[^\w._-]', '', parts[1])
        # Clean the domain part (last part) - only allow alphanumeric, dots, and hyphens
        cleaned_domain = re.sub(r'[^\w.-]', '', parts[2])
        
        if cleaned_user and cleaned_domain:
            cleaned_username = f"@{cleaned_user}@{cleaned_domain}"
            cleaned_usernames.append(cleaned_username)
            
    return cleaned_usernames

def main():
    """
    Converts a PDF or Markdown file to text, extracts fediverse usernames, and saves them to a CSV file.
    """

    if len(sys.argv) != 3:
        print("Usage: python script.py <listname> <input_file>")
        sys.exit(1)

    listname = sys.argv[1]
    input_file = sys.argv[2]
    file_extension = os.path.splitext(input_file)[1].lower()

    if file_extension == ".pdf":
        # Convert PDF to text using pdftotext
        txt_file = "temp.txt"  # Temporary file to store the text output
        try:
            subprocess.run(["pdftotext", input_file, txt_file], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error during PDF to text conversion: {e}")
            sys.exit(1)

        # Read the text from the temporary file
        with open(txt_file, "r") as f:
            text = f.read()
        
        # Clean up the temporary text file
        os.remove(txt_file)
    elif file_extension in (".md", ".txt"):
        # Read the text directly from the Markdown or text file
        with open(input_file, "r") as f:
            text = f.read()
    else:
        print("Unsupported file format. Please provide a PDF, Markdown (.md), or text (.txt) file.")
        sys.exit(1)
        

    # Extract usernames
    usernames = extract_fediverse_usernames(text)

    # Clean usernames (remove trailing parentheses)
    cleaned_usernames = clean_usernames(usernames)

    # Eliminate duplicates using a set
    unique_usernames = list(set(cleaned_usernames))

    # Save usernames to CSV
    csv_file = "fediverse_usernames.csv"
    with open(csv_file, "w") as f:
        f.write("listname,username\n")
        for username in unique_usernames:
            f.write(f"{listname},{username}\n")

    print(f"Fediverse usernames extracted and saved to {csv_file}")

if __name__ == "__main__":
    main()
