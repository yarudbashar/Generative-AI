from langchain.vectorstores.chroma import Chroma
from langchain.schema import Document
# from langchain.document_loaders import DirectoryLoader
# from langchain.document_loaders import DirectoryLoader
from langchain_community.document_loaders import DirectoryLoader
# from langchain.document_loaders
# from langchaincommunity.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_community.embeddings.openai import OpenAIEmbeddings
from langchain_openai import OpenAIEmbeddings
import shutil
from utils import *
set_open_key()

CHROMA_PATH = "chroma_text"
#data source index list
DATA_PATH = "textdir"


def main():
    # import sys
    # sys.path.append("D:\pycharm-debug")
    # import pydevd
    # pydevd.settrace('localhost', port=8087, stdoutToServer=True, stderrToServer=True)
    generate_data_store()


def generate_data_store():
    documents = load_documents()
    chunks = split_text(documents)
    save_to_chroma(chunks)


def load_documents():
    loader = DirectoryLoader(DATA_PATH, glob="*.txt")
    documents = loader.load()
    return documents


def split_text(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        #300/o100
        chunk_size=2000,
        chunk_overlap=500,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)
    print("Split {len(documents)} documents into {len(chunks)} chunks.")
    document = chunks
    print("Chunks>>>>>>>>..",chunks)
    # print(document.page_content)
    # print(document.metadata)
    return chunks


def save_to_chroma(chunks: list[Document]):
    # Clear out the database first.
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

    # Create a new DB from the documents.
    db = Chroma.from_documents(
        chunks, OpenAIEmbeddings(), persist_directory=CHROMA_PATH
    )
    db.persist()
    print("Saved {len(chunks)} chunks to {CHROMA_PATH}.")


if __name__ == "__main__":
    main()
# from langchain.document_loaders import DirectoryLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
# from langchain.embeddings import OpenAIEmbeddings
