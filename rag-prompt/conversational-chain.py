from flask import Flask, render_template, request, jsonify
from langchain.vectorstores.chroma import Chroma
# from langchain.embeddings import OpenAIEmbeddings
# from langchain.chat_models import ChatOpenAI
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferMemory
from flask_cors import CORS
from langchain_openai import OpenAI
import tiktoken
# import os
# os.environ["OPENAI_API_KEY"] = "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"
from utils import *
set_open_key()

from langchain_experimental.agents import create_csv_agent


# import os
# os.environ["OPENAI_API_KEY"] = "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"
# encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
import asyncio

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

CHROMA_PATH = "chroma_text"
PROMPT_TEMPLATE = """
Answer the question based only on the following context:
{history}

{context}

---

Answer the question based on the above context: {question}
"""

# Add a variable to store chat history globally
chat_history = []
# agent for csv toggle
agent_mode = "False"
memory = ConversationBufferMemory(llm=OpenAI(), max_token_limit=4000)
# Initialize the conversation chain
llm = ChatOpenAI(model="gpt-3.5-turbo-1106")
conversation = ConversationChain(llm=llm, memory=memory, verbose=True)
import pandas as pd

df = pd.read_csv('csv/Customers.csv', encoding='latin1')
# df = pd.read_csv('csv/Orders-With Nulls.xlsx', encoding='latin1')
agent = create_csv_agent(OpenAI(temperature=0),
                         'csv/Customers.csv',
                         verbose=True)
# agent.agent.llm_chain.prompt.template

# f= pd.ExcelFile('csv/Orders.xlsx')
# df1 = pd.read_excel("csv/Orders.xlsx", sheet_name='Sheet1')
# print(">>>>>>>>",df1)
# df1 = f.parse(f)
@app.route('/')
async def index():
    return render_template('index.html')


@app.route('/query', methods=['POST'])
def query():
    global chat_history
    global CHROMA_PATH  # Access the global variable
    global agent_mode
    # import sys
    # sys.path.append("D:\pycharm-debug")
    # import pydevd
    # pydevd.settrace('localhost', port=8087, stdoutToServer=True, stderrToServer=True)
    query_text = request.form['query_text']

    # handle data_source switching if requested
    # ----------------------------------------------
    # Check if the user is asking to change the data source
    if "change data source" in query_text.lower():
        # Prepare the prompt
        print("Change Triggered")
        prompt = f"Generate textdir for asking user to choose one option to switch data sources between Pdf, Word, Text, Csv, Excel and confluence also ask user to give one word input only for their choice"

        # Use the conversation chain to predict the response
        response_text = conversation.predict(input=prompt)
        return jsonify({'query_text': query_text, 'response_text': response_text})

    if query_text == "confluence":
        # Update the data source
        agent_mode = "False"
        CHROMA_PATH = "confluence"
        prompt = f"Generate textdir for -> your data source is Successfully to confluence now ask question related to it"
        chat_history.clear()
        response_text = conversation.predict(input=prompt)
        return jsonify({'query_text': query_text, 'response_text': response_text})

    if query_text == "pdf":
        # Update the data source
        agent_mode = "False"
        CHROMA_PATH = "chroma_pdf"
        prompt = f"Generate textdir for -> your data source is Successfully to PDF files now ask question related to it"
        chat_history.clear()
        response_text = conversation.predict(input=prompt)
        return jsonify({'query_text': query_text, 'response_text': response_text})

    if query_text == "word":
        # Update the data source
        agent_mode = "False"
        CHROMA_PATH = "chroma_doc"
        prompt = f"Generate textdir for -> your data source is Successfully to Document files now ask question related to it"
        chat_history.clear()
        response_text = conversation.predict(input=prompt)
        return jsonify({'query_text': query_text, 'response_text': response_text})

    if query_text == "text":
        # Update the data source
        agent_mode = "False"
        CHROMA_PATH = "chroma_text"
        prompt = f"Generate textdir for -> your data source is Successfully to Text files now ask question related to it"
        chat_history.clear()
        response_text = conversation.predict(input=prompt)
        return jsonify({'query_text': query_text, 'response_text': response_text})

    if query_text == "csv":
        # Update the data source
        agent_mode = "True"
        prompt = f"Generate textdir for -> your data source is Successfully to CSV files now ask question related to it"
        chat_history.clear()
        response_text = conversation.predict(input=prompt)
        return jsonify({'query_text': query_text, 'response_text': response_text})

    if query_text == "excel":
        # Update the data source
        agent_mode = "True"
        prompt = f"Generate textdir for -> your data source is Successfully to Excel files now ask question related to it"
        chat_history.clear()
        response_text = conversation.predict(input=prompt)
        return jsonify({'query_text': query_text, 'response_text': response_text})
    # Prepare the DB.
    embedding_function = OpenAIEmbeddings()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
    if agent_mode == "False":
        # Search the DB.
        results = db.similarity_search_with_relevance_scores(query_text, k=3)
        if len(results) == 0 or results[0][1] < 0.7:
            # ------before--conversation memory
            # response_text = "Unable to find matching results."
            sources = []
            # -----------------------------------------------
            prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
            prompt = prompt_template.format(context="give response on basis of below", history=chat_history,
                                            question=query_text)
            # Token Limit hit handling

            # Use the conversation chain to predict the response
            response_text = conversation.predict(input=prompt)
            # Append the current conversation to the chat history
            chat_history.append(f"User: {query_text} | Bot: {response_text} | Sources: {', '.join(sources)}")
            print(conversation.memory.buffer)

        else:
            context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
            prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
            prompt = prompt_template.format(context=context_text, history=chat_history, question=query_text)
            # Token limit Hit handling

            # Use the conversation chain to predict the response
            response_text = conversation.predict(input=prompt)

            sources = [doc.metadata.get("source", None) for doc, _score in results]

            # Append the current conversation to the chat history
            chat_history.append(f"User: {query_text} | Bot: {response_text} | Sources: {', '.join(sources)}")
            print(conversation.memory.buffer)

            # Modify the response_text format
            # formatted_response_text = response_text.replace('. ', '.\n\n')
        formatted_response_text = response_text
        return jsonify({
            'query_text': query_text,
            'response_text': formatted_response_text,
            'sources': sources,
            'chat_history': chat_history  # Include chat history in the response
        })
    if agent_mode == "True":
        response_text = agent.run(query_text)
        formatted_response_text = response_text
        return jsonify({
            'query_text': query_text,
            'response_text': formatted_response_text
        })


if __name__ == '__main__':
    app.run(debug=True)
