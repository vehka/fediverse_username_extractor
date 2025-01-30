import sys
import re
import os
import subprocess

def extract_fediverse_usernames(text):
    """
    Extracts fediverse usernames from a given text using regular expressions.

    Args:
        text: The input text.

    Returns:
        A set of unique fediverse usernames.
    """
    pattern = r'@[^@\s]+@[^]\s]+'  # Modified regex
    usernames = re.findall(pattern, text)
    return set(usernames)

def clean_usernames(usernames):
    """
    Removes trailing parentheses from usernames.

    Args:
        usernames: A list of usernames.

    Returns:
        A list of cleaned usernames.
    """
    cleaned_usernames = []
    for username in usernames:
        # Remove trailing dots, parentheses, and backticks
        while username.endswith((".", ")", "`", ",")):
            username = username[:-1]

        cleaned_usernames.append(username)
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
