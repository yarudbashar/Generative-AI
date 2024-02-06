from openai import OpenAI
from flask import Flask, render_template, request, jsonify
from langchain.vectorstores.chroma import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferMemory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

CHROMA_PATH = "chroma_doc"

PROMPT_TEMPLATE = """
Answer the question based only on the following context:
{history}

{context}

---

Answer the question based on the above context: {question}
"""
chat_history = []
client = OpenAI()
memory=ConversationBufferMemory(llm=OpenAI(),max_token_limit=1000)
stream = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "write 300 in words"}],
    stream=True,
)

for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="")

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/query', methods=['POST'])
def query():
    global chat_history
    global CHROMA_PATH  # Access the global variable

    # query_text = request.form['query_text']

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

        # Use the conversation chain to predict the response
        stream = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": {query_text}}],
            stream=True,
            )

        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                print(chunk.choices[0].delta.content, end="")

    else:
        context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        prompt = prompt_template.format(context=context_text,history=chat_history ,question=query_text)

        # Use the conversation chain to predict the response
        stream = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": {prompt}}],
            stream=True,
            )

        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                print(chunk.choices[0].delta.content, end="")

        sources = [doc.metadata.get("source", None) for doc, _score in results]
        response_text ="Hello"
        # Append the current conversation to the chat history
        chat_history.append("User: {query_text} | Bot: {response_text} | Sources: {', '.join(sources)}")
        

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
