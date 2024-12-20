import streamlit as st
import requests
import json

# Title of the application
st.title("RAG Chatbot Interface")
st.markdown("Ask your questions and get responses from the RAG system.")

# Expander for Indexing
with st.expander("**Indexing**"):
    st.markdown("""
    - **Documents** are converted from source formats (e.g., PDFs) into structured content.
    - **Chunking** is performed using a sentence-based splitter to divide documents into smaller manageable parts.
    - **Embedding**: Each chunk is embedded using the `SentenceTransformersDocumentEmbedder` to generate vector representations.
    - **Storage**: The embeddings are stored in a **Pinecone Vector Database**, enabling fast and efficient similarity searches.
    """)

# Expander for Retrieval
with st.expander("**Retrieval**"):
    st.markdown("""
    - **Query Embedding**: The input query is embedded using `SentenceTransformersTextEmbedder`.
    - **Retriever**: The `PineconeEmbeddingRetriever` retrieves the most relevant document chunks by comparing query embeddings with document embeddings stored in Pinecone.
    - **Output**: A set of top-matching documents is retrieved to provide relevant context for the query.
    """)

# Expander for Generation
with st.expander("**Generation**"):
    st.markdown("""
    - **Prompt Builder**: A custom prompt template structures the retrieved documents along with the query to form a meaningful input.
    - **LLM Generation**: The structured prompt is passed to an open-source **LLM (Meta-Llama3.1-8B-Instruct)**, integrated using Hugging Face's Serverless Inference API.
    - **Output**: The model generates a contextually aware and concise answer based on the prompt and retrieved documents.
    """)

# PDF Upload and Indexing
uploaded_pdf = st.file_uploader("Upload a PDF for indexing", type=["pdf"])

if st.button("Index PDF"):
    if uploaded_pdf is not None:
        try:
            # Send the PDF to the backend API as multipart form data
            files = {"file": uploaded_pdf}  # Get the content of the uploaded file
            index_response = requests.post("http://127.0.0.1:8000/index_pdf", files=files)

            if index_response.status_code == 200:
                response_data = index_response.json()
                st.success(response_data)  # Assuming the message is in the response
            else:
                st.error(f"Error: {index_response.status_code} - {index_response.text}")
        except Exception as e:
            st.error(f"An error occurred during indexing: {e}")
    else:
        st.warning("Please upload a PDF before clicking 'Index PDF'.")


# Input box for the user to ask questions
user_query = st.text_input("Type your question:")

# Define your FastAPI endpoint
api_url = "http://127.0.0.1:8000/get_result"  # Replace with your FastAPI endpoint

if st.button("Submit"):
    if user_query.strip():
        try:
            # Send POST request to the FastAPI endpoint
            response = requests.post(api_url, json.dumps({"query": user_query}))
            
            if response.status_code == 200:
                # Display the chatbot response
                answer = response.json().get("answer", "No answer found.")
                if "i don't know" in answer.lower():
                    st.error(f"Chatbot Response: {answer}")
                else:
                    st.success(f"Chatbot Response: {answer}")
            else:
                st.error(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a question before submitting.")

st.markdown("## Why Haystack instead of LangChain?")

# Informational content
st.markdown("""
Haystack offers a more comprehensive approach to building LLM pipelines compared to LangChain. Here’s why:

- **Better Documentation**: Haystack’s documentation is more detailed and user-friendly, making it easier to set up and customize.
- **End-to-End RAG Capabilities**: Haystack integrates retrieval, generation, semantic search, and feedback loops seamlessly into one framework.
- **Ease of Use**: With lower barriers to entry, it simplifies the process of building custom GPTs or chatbots.
- **Performance**: Based on benchmarking experiments, Haystack demonstrates higher average accuracy, lower deviation in responses, and more consistent results in comparison to LangChain.
- **Production-Ready**: For straightforward RAG setups like chatbots, Haystack is more suited for production workloads due to its simplicity and reliability.

However, for more complex scenarios involving orchestration across multiple agents or services, LangChain might still be preferable due to its flexibility in such setups.
""")