from dotenv import load_dotenv
import os
import subprocess
def set_open_key():
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    try:
        if openai_api_key:
            print("Open API Key Successfully Set")
    except Exception as e:
        print("Print Open API KEY",e)

def subprocess_call_for_convert_markdown_to_html(markdown_path, html_path):
    try:
        subprocess.run(["where","pandoc", markdown_path, "-o", html_path],check=True, capture_output=True, text=True)
       #Access denied issue with this command # subprocess.run(["D:\\GenAIProject\\envs\\Lib\\site-packages\\pandoc", markdown_path, "-o", html_path],check=True, capture_output=True, textdir=True)
        # subprocess.run(["pandoc", markdown_path, "-o", html_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error converting {markdown_path} to HTML. Error: {e}")