from flask import Flask, render_template, request, jsonify
from langchain.vectorstores.chroma import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import ConversationChain
#from langchain.memory import ConversationBufferMemory
from langchain.chains.conversation.memory import ConversationBufferMemory
from flask_cors import CORS  # Add this import for handling cross-origin requests

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

CHROMA_PATH = "chroma"
PROMPT_TEMPLATE = """
Answer the question based only on the following context:
also ask user for title before generating response

{context}

---

Answer the question based on the above context: {question}
"""

# Add a variable to store chat history globally
chat_history = []

# Initialize the conversation chain
llm = ChatOpenAI()
conversation = ConversationChain(llm=llm, verbose=True, memory=ConversationBufferMemory())

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query():
    global chat_history  # Access the global variable

    query_text = request.form['query_text']

    # Prepare the DB.
    embedding_function = OpenAIEmbeddings()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Search the DB.
    results = db.similarity_search_with_relevance_scores(query_text, k=3)
    if len(results) == 0 or results[0][1] < 0.7:
        response_text = "Unable to find matching results."
        sources = []
    else:
        context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        prompt = prompt_template.format(context=context_text, question=query_text)

        # Use the conversation chain to predict the response
        response_text = conversation.predict(input=prompt)

        sources = [doc.metadata.get("source", None) for doc, _score in results]

        # Append the current conversation to the chat history
        chat_history.append(f"User: {query_text} | Bot: {response_text} | Sources: {', '.join(sources)}")
        print(conversation.memory.buffer)

    return jsonify({
        'query_text': query_text,
        'response_text': response_text,
        'sources': sources,
        'chat_history': chat_history  # Include chat history in the response
    })

if __name__ == '__main__':
    app.run(debug=True)
