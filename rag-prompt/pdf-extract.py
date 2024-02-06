import os
from pdfminer.high_level import extract_text
import subprocess

def extract_text_from_pdf(pdf_path):
    return extract_text(pdf_path)

def convert_to_markdown(text):
    lines = text.split("\\\\n")
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.isupper() and len(stripped) < 50:
            lines[i] = f"## {stripped}"
    return "\\\\n".join(lines)

def process_pdfs_in_directory(pdf_directory, markdown_directory):
    for filename in os.listdir(pdf_directory):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(pdf_directory, filename)
            markdown_filename = filename.replace(".pdf", "_markdown.md")
            markdown_path = os.path.join(markdown_directory, markdown_filename)
            
            # Check if the markdown file already exists
            if os.path.exists(markdown_path):
                print(f"Markdown for {filename} already exists. Skipping...")
                continue

            # Extract textdir from the PDF file
            pdf_text = extract_text_from_pdf(pdf_path)
            
            # Convert the extracted textdir to Markdown format
            markdown_text = convert_to_markdown(pdf_text)
            
            # Save the converted Markdown textdir to a file
            with open(markdown_path, "w" , encoding="utf-8") as f:
                f.write(markdown_text)
                
            # Convert the Markdown file to HTML using pandoc
            html_filename = filename.replace(".pdf", "_html.html")
            html_path = os.path.join(markdown_directory, html_filename)
            subprocess.run(["pandoc", markdown_path, "-o", html_path])

    print("All PDF files have been processed successfully!")

def main():
    pdf_directory = 'pdf'
    markdown_directory = 'md'
    process_pdfs_in_directory(pdf_directory, markdown_directory)

if __name__ == "__main__":
    main()
