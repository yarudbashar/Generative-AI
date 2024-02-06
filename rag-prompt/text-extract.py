import os
def read_text_file(file_path):
    for filename in os.listdir(file_path):
        file_path = os.path.join(file_path, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text_content = file.read().strip()
            return text_content
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.")
        except Exception as e:
            print(f"Error reading file '{file_path}': {e}")

if __name__ == "__main__":
    text_file_path = 'textdir'
    extracted_text = read_text_file(text_file_path)
    if extracted_text:
        print(extracted_text)