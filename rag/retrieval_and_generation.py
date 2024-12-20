# from haystack.components.embedders import HuggingFaceAPITextEmbedder
from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack.components.builders import PromptBuilder
from haystack_integrations.components.retrievers.pinecone import PineconeEmbeddingRetriever
from haystack.components.generators import HuggingFaceAPIGenerator
from haystack import Pipeline
from rag.utils import pinecone_config
import os
from dotenv import load_dotenv
 
prompt_template = """Answer the following query based on the provided context. If the context does
                     not include an answer, reply with 'I don't know'.\n
                     Query: {{query}}
                     Documents:
                     {% for doc in documents %}
                        {{ doc.content }}
                     {% endfor %}
                     Answer: 
                  """
def get_result(query):                   
    query_pipeline = Pipeline()
    
    query_pipeline.add_component("text_embedder", SentenceTransformersTextEmbedder())
    query_pipeline.add_component("retriever", PineconeEmbeddingRetriever(document_store=pinecone_config()))
    query_pipeline.add_component("prompt_builder", PromptBuilder(template=prompt_template))
    query_pipeline.add_component("llm", HuggingFaceAPIGenerator(api_type="serverless_inference_api",api_params={"model":"meta-llama/Llama-3.2-3B-Instruct"}))  #mistralai/Mistral-7B-v0.1
 
    query_pipeline.connect("text_embedder.embedding", "retriever.query_embedding")
    query_pipeline.connect("retriever.documents", "prompt_builder.documents")
    query_pipeline.connect("prompt_builder", "llm")

    results = query_pipeline.run(
        {
            "text_embedder": {"text": query},
            "prompt_builder": {"query": query},
        }
    )
    return results['llm']['replies'][0]
 
if __name__ == '__main__':
    load_dotenv()
    result=get_result("what is jeopardy question generation in short terms with an example ?")
    print(result)