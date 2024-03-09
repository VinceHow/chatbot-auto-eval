from pinecone import Pinecone
import voyageai
from dotenv import load_dotenv
import os
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY")
print(PINECONE_API_KEY)

# create Pinecone object
pinecone = Pinecone(PINECONE_API_KEY)
voyageai = voyageai.Client()


def k_nearest_neighbors(query_embedding, documents_embeddings, k=5):
    query_embedding = np.array(query_embedding) # convert to numpy array
    documents_embeddings = np.array(documents_embeddings) # convert to numpy array
        
    # Reshape the query vector embedding to a matrix of shape (1, n) to make it compatible with cosine_similarity
    query_embedding = query_embedding.reshape(1, -1)
    
    # Calculate the similarity for each item in data
    cosine_sim = cosine_similarity(query_embedding, documents_embeddings)

    # Sort the data by similarity in descending order and take the top k items
    sorted_indices = np.argsort(cosine_sim[0])[::-1]

    # Take the top k related embeddings
    top_k_related_indices = sorted_indices[:k]
    top_k_related_embeddings = documents_embeddings[sorted_indices[:k]]
    top_k_related_embeddings = [list(row[:]) for row in top_k_related_embeddings] # convert to list

    return top_k_related_embeddings, top_k_related_indices

def create_or_connect_pinecone_index(index_name: str = "snack-52"):
    """
    Creates a new Pinecone index with the given name if it does not already exist, or connects to an existing index with
    the same name. The index has a fixed dimension of 1536, which is the number of dimensions returned by the voyage-large-2  
    model, and uses the consine metric for similarity search.
    """

    # # check if index already exists (it shouldn't if this is first time)
    # if index_name not in pinecone.list_indexes():
    #     # if does not exist, create index
    #     pinecone.create_index(
    #         index_name,
    #         dimension=1536,  # dimensions returned by voyage-large-2
    #         metric="cosine",
    #         spec = [{"PodSpec":"starter"}]
    #     )
    # connect to index
    index = pinecone.Index(name=index_name)
    return index


def turn_doc_into_embeddings(path_to_doc: str):
    """
    Turn a document into embeddings using Pinecone
    """
    # open the doc and read content as string
    with open(path_to_doc, 'r') as file:
        doc = file.read()
    # turn string into chunks
    texts = doc.split('\n\n')
    # turn chunks into embeddings
    result = voyageai.embed(texts, model="voyage-large-2", input_type="document", truncation = False)
    print(result.embeddings)

    return

def query_pinecone_index(index, query, top_k=5):
    """
    Query the Pinecone index with the given query and return the top_k most similar items.
    """
    # Get the embedding of the query
    query_embedding = voyageai.embed(
        [query], model="voyage-large-2", input_type="query"
    ).embeddings[0]
    # query the index
    results = index.query(queries=query, top_k=top_k)
    return results



# # attempt to connect to an exising Pinecone index, if it doesn't exist, create a new one
# try:
#     index = pc.Index("snack_52")
# except:
#     pc.create_index(
#         name='example-index', 
#         dimension=1024, 
#         metric="cosine", 
#         spec=PodSpec(environment="us-west1-gcp")
#     )

if __name__ == "__main__":
    pinecone_index_conn = create_or_connect_pinecone_index()
    print(pinecone_index_conn)
    dumb_bot_knowledge = "../snack_52/snack_52_docs_dumb.txt"
    turn_doc_into_embeddings(dumb_bot_knowledge)