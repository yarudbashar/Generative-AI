from flask import Flask, render_template, request, jsonify
import requests
# from transformers import pipeline
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.vectorstores import Chroma
from langchain.llms import HuggingFacePipeline
from langchain.chains import RetrievalQA
# from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
# import torch
import os

app = Flask(__name__)

# Settings
persist_directory = "db"
checkpoint = "MBZUAI/LaMini-T5-738M"
# device = torch.device('cpu')

# Confluence API endpoint for fetching content
content_url = "https://agreeya-atulagrahari.atlassian.net/wiki/rest/api/content/?expand=body.view"

# Confluence credentials (replace with your Confluence email and API token)
email = "888sanjeev.kumar@agreeya.com"
# api_token = "ATATT3xFfGF0JlSvI4R1lx3kZmBAUG-MWC_bnfKkz4Qh-rdkRkI8b6lvqBS4VgtZaZoaFwwc55ex5ZIOcx75-LwIRR-b8p8Uf1OsGBdgINz6gwdc_qmRc1Y8JYguI6TYjwBjb5-Gzl4UVw3km_bx_LDLcK5-TyqdEsfwd3_oxEGv9Fh9-D2ed84=58E94295"
api_token = "uuuATATT3xFfGF04gNxWjacTxlehAOBl299R_j4oulTTLIjnFaZhlrcOb3SegG2jHkAvLGydYPiDcN3DD7iR2rvCHLEdNyx4gYcF9jEoIeqmUtQVkt3L3zhSlxlyYsUnbCCoRZ5G4g_XWw058vohztRGeyAx_Lefdj5lIqHd7vOUGCxxFRz7vS4tUs=249B11FA"

# Headers for authentication
headers = {
    "Content-Type": "application/json",
}

# Function to extract textdir from HTML content
def extract_text_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup.get_text()

# Function to replace invalid characters in filenames
def sanitize_filename(filename):
    return filename.replace(':', '_')

# Function to fetch data from Confluence API
def fetch_data(url):
    response = requests.get(url, headers=headers, auth=HTTPBasicAuth(email, api_token))

    if response.status_code == 200:
        return response.json().get("results", [])
    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
        print(f"Response content: {response.content}")
        return []

# Fetch content for the specified page
content = fetch_data(content_url)

# Define the directory to save the markdown files
output_directory = "data"

# Extract textdir from HTML content for target IDs
for item in content:
    item_id = item.get("id")
    title = item.get("title")
    body_content = item.get("body", {}).get("view", {}).get("value", "")

    if body_content and isinstance(body_content, str):
        # Create a sanitized filename for each item
        sanitized_title = sanitize_filename(title)
        # Create a markdown file for each item
        output_file_path = os.path.join(output_directory, f"{sanitized_title}.md")

        # Write the item_id, title, and plain_text_content to the markdown file
        with open(output_file_path, 'w', encoding='utf-8') as file:
            file.write(f"Item ID: {item_id}\n")
            file.write(f"Title: {title}\n")
            file.write(extract_text_from_html(body_content) + '\n')

        print(f"Contents saved to {output_file_path}")
