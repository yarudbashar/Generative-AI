import os
import docx2txt
import subprocess
import distutils
# from utils import *
from . import utils
def extract_text_data_from_docx(path):
    data = docx2txt.process(path)
    text = [line.replace('\t', ' ') for line in data.split('\n\n\n') if line]
    final_text = ''.join(text)
    return final_text

def process_words_in_directory(doc_directory, markdown_directory):
    for filename in os.listdir(doc_directory):
        if filename.endswith(os.path.splitext(filename)[1]):#It will return the extension of any file
            doc_path = os.path.abspath(os.path.join(doc_directory, filename))
            markdown_path = os.path.abspath( os.path.join(markdown_directory, os.path.splitext(filename)[0] + ".md"))
            html_path = os.path.abspath(os.path.join(markdown_directory, os.path.splitext(filename)[0] + ".html"))
            # Extract textdir from .doc file

            if os.path.exists(markdown_path):
                print(f"Markdown for {filename} already exists. Skipping...")
                continue

            # Extract textdir from document file
            extracted_text = extract_text_data_from_docx(doc_path)

            # Save extracted textdir to a markdown file
            with open(markdown_path, "w", encoding="utf-8") as markdown_file:
                markdown_file.write(extracted_text)

                # Convert markdown to HTML using Pandoc
            utils.subprocess_call_for_convert_markdown_to_html(markdown_path, html_path)

def main():
    doc_directory = 'word'
    markdown_directory = 'wordmd'
    process_words_in_directory(doc_directory, markdown_directory)


if __name__ == "__main__":
    main()
