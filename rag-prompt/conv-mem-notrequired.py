from flask import Flask, render_template, request
from langchain.vectorstores.chroma import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from flask import jsonify

app = Flask(__name__)

CHROMA_PATH = "chroma"

PROMPT_TEMPLATE = """
Answer the question based only on the following context:
also ask the user for the title before generating a response

{context}

---

Answer the question based on the above context: {question}
"""

class ConversationalMemory:
    def __init__(self):
        self.memory = []

    def add_to_memory(self, user_input, bot_response):
        self.memory.append({"user": user_input, "bot": bot_response})

    def get_memory(self):
        return self.memory

# Initialize the conversational memory
conversational_memory = ConversationalMemory()

@app.route('/')
def index():
    return render_template('index.html')

# Add a variable to store chat history globally
chat_history = []

@app.route('/query', methods=['POST'])
def query():
    query_text = request.form['query_text']

    # Store the user's query in conversational memory
    conversational_memory.add_to_memory(query_text, "")

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

        # Use the embedding_function directly
        query_embedding = embedding_function.embed(query_text)

        # Use conversational memory to provide context
        past_conversations = conversational_memory.get_memory()
        for past_convo in past_conversations:
            prompt += f"\nUser: {past_convo['user']}\nBot: {past_convo['bot']}"

        model = ChatOpenAI(embedding_function=embedding_function)
        response_text = model.predict(prompt, query_embedding)

        sources = [doc.metadata.get("source", None) for doc, _score in results]
        # Append the current conversation to the chat history
        chat_history.append(f"User: {query_text} | Bot: {response_text} | Sources: {', '.join(sources)}")

        # Store the bot's response in conversational memory
        conversational_memory.add_to_memory("", response_text)

    return jsonify({
        'query_text': query_text,
        'response_text': response_text,
        'sources': sources,
        'chat_history': chat_history  # Include chat history in the response
    })

if __name__ == '__main__':
    app.run(debug=True)
