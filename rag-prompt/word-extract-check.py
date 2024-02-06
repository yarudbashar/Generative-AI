import os
import docx2txt
# from win32com import client as wc
import shutil
import subprocess
# shutil.move('filename','md')

def extract_text_data_from_doc(path):
    return docx2txt.process(path)

def split_line_data_convert(data):
    temp = data
    text = [line.replace('\t', ' ') for line in temp.split('\n\n\n') if line]
    final_text = ' '.join(text)
    return final_text


print(split_line_data_convert('word/testfile.docx'))
from pathlib import Path
# directory = 'word//'
# directory_path = 'word/'
# directory_path1 = "word/"
directory_path=os.chdir("word/")
# ne=os.path.basename(directory_path1)
def process_data(dir_path):
    for file in os.listdir(dir_path):
        ext = os.path.splitext(file)[1]
        print(111111111,ext)
        if ext == '.docx' or ext == '.doc':
            new_file = shutil.copy2(file,'../wordmd/')
            print('nnnnnnnnnn',new_file)
            create_markdown_file = new_file.replace(ext, "_markdown.md")
            file_exist=os.path.splitext(new_file)[0]
            print("there",file_exist)
            # if not new_file.endswith("._markdown.md"):
            if file_exist:
                # if not os.path.exists(file_exist):
                f = Path(new_file)
                print('newssss',f)
                # if os.path.exists(f):
                f.rename(create_markdown_file)

            #     # not os.path.exists('../wordmd')
            #     print('mmmmmm', create_markdown_file)

            # else:
            #     print("File Already Exist")


            # print(00000,f)
            # markdown_path = os.path.join('../wordmd/', create_markdown_file)
            # print('Yarud',markdown_path)

            # shutil.co
            # shutil.copy2(create_markdown_file, '../wordmd')
            word_text = extract_text_data_from_doc(directory_path)
            markdown_text = split_line_data_convert(word_text)

            with open(create_markdown_file, "w" , encoding="utf-8") as f:
                f.write(markdown_text)
            html_filename = file.replace(".docx", "_html.html")
            html_path = os.path.join('../wordmd/', html_filename)
            subprocess.run(["pandoc", create_markdown_file, "-o", html_path])

            # if not os.path.exists('../wordmd'):
            #     os.mkdir('../wordmd')

        print(file)
# print(process_data(directory_path))