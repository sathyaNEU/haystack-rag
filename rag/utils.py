from haystack_integrations.document_stores.pinecone import PineconeDocumentStore
import os
from dotenv import load_dotenv

load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
HF_API_TOKEN = os.getenv("HF_TOKEN")
os.environ['PINECONE_API_KEY'] = PINECONE_API_KEY
os.environ['HF_API_TOKEN'] = HF_API_TOKEN

def pinecone_config():
    document_store = PineconeDocumentStore(
            index="haystack",
            namespace="default",
            dimension=768
        )
    return document_store