from flask import Flask, render_template, request, jsonify
from langchain.vectorstores.chroma import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferMemory
from flask_cors import CORS
from langchain_openai import OpenAI
import tiktoken
# from dotenv import load_dotenv
# load_dotenv()
import os
os.environ["OPENAI_API_KEY"] = "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"
# OPENAI_API_KEY="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"
# os.environ["OPENAI_API_KEY"] = "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"

encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

CHROMA_PATH = "chroma_pdf"
PROMPT_TEMPLATE = """
Answer the question based only on the following context:
{history}

{context}

---

Answer the question based on the above context: {question}
"""

# Add a variable to store chat history globally
chat_history = []
memory=ConversationBufferMemory(llm=OpenAI(),max_token_limit=4000)
# Initialize the conversation chain
llm = ChatOpenAI()
conversation = ConversationChain(llm=llm, memory=memory ,verbose=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query():
    # import sys
    # sys.path.append("D:\pycharm-debug")
    # import pydevd
    # pydevd.settrace('localhost', port=8087, stdoutToServer=True, stderrToServer=True)
    global chat_history
    global CHROMA_PATH  # Access the global variable

    query_text = request.form['query_text']
    
    #handle data_source switching if requested
    #----------------------------------------------
        # Check if the user is asking to change the data source
    if "change data source" in query_text.lower():
        # Prepare the prompt
        print("Change Triggered")
        prompt = "ask user to choose one option to switch data source and then in return generate one output in one word only i.e either (pdf or confluence) note your output must be only -> pdf or confluence "
        # prompt ="fruits"
        # Use the conversation chain to predict the response
        response_text = conversation.predict(input=prompt)
        return jsonify({'query_text': query_text,'response_text': response_text})
        
    if query_text == "confluence":
        # Update the data source
        CHROMA_PATH = "confluence"
        prompt = "Generate textdir for -> your data source is Successfully to confluence now ask question related to it"
        chat_history.clear()
        response_text = conversation.predict(input=prompt)
        return jsonify({'query_text': query_text,'response_text': response_text})

    
    if query_text == "pdf":
        # Update the data source
        CHROMA_PATH = "chroma_pdf"
        response_text = "Successfully changed data source to PDF"
        chat_history.clear()
        return jsonify({'query_text': query_text,'response_text': response_text})


    # Prepare the DB.
    embedding_function = OpenAIEmbeddings()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Search the DB.
    results = db.similarity_search_with_relevance_scores(query_text, k=3)
    if len(results) == 0 or results[0][1] < 0.7:
        #------before--conversation memory
        #response_text = "Unable to find matching results."
        sources = []
        #-----------------------------------------------
        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        prompt = prompt_template.format(context="give response on basis of below",history=chat_history ,question=query_text)
        #Token Limit hit handling 

        # Use the conversation chain to predict the response
        response_text = conversation.predict(input=prompt)
        # Append the current conversation to the chat history
        chat_history.append("User: {query_text} | Bot: {response_text} | Sources: {', '.join(sources)}")
        print(conversation.memory.buffer)

    else:
        context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        prompt = prompt_template.format(context=context_text,history=chat_history ,question=query_text)
        #Token limit Hit handling
  
        # Use the conversation chain to predict the response
        response_text = conversation.predict(input=prompt)

        sources = [doc.metadata.get("source", None) for doc, _score in results]

        # Append the current conversation to the chat history
        chat_history.append("User: {query_text} | Bot: {response_text} | Sources: {', '.join(sources)}")
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

if __name__ == '__main__':
    app.run(debug=True)
