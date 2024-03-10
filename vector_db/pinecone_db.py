from pinecone import Pinecone
import voyageai
from dotenv import load_dotenv
import os
import numpy as np
import uuid
load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY")

# create Pinecone object
pinecone = Pinecone(PINECONE_API_KEY)
voyageai = voyageai.Client()


def connect_pinecone_index(index_name: str = "snack-52"):
    index = pinecone.Index(name=index_name)
    return index


class VectorEmbedding:
    """
    A class to represent a list of floats representing the vector, must be of the length 1536.
    """

    def __init__(self, embedding_vector: list):
        if len(embedding_vector) != 1536:
            raise ValueError("The input vector must be a list of length 1536.")
        self.vector = embedding_vector

    def __str__(self):
        return f"VectorEmbeddings({self.vector})"

    def get_vector(self):
        return self.vector

def turn_doc_into_chunks(path_to_doc: str):
    """
    Turn a document into chunks using Pinecone
    """
    # open the doc and read content as string
    with open(path_to_doc, 'r') as file:
        doc = file.read()
    # turn string into chunks
    texts = doc.split('\n\n')
    return texts


def turn_chunks_into_embeddings(texts: list[str]):
    """
    Turn a document into embeddings using Pinecone
    """
    # open the doc and read content as string
    embeds = []
    # turn chunks into embeddings
    result = voyageai.embed(texts, model="voyage-large-2", input_type="document", truncation = False)
    for i in result.embeddings:
        embeds.append(i)
    print("Successfully embedded " + str(len(embeds)) + " to vector space!")
    return embeds

class VectorMetadata:
    """
    A class to represent a dictionary of metadata for the vector.
    """

    REQUIRED_KEYS = ["id", "text"]  # these keys are required
    ALLOWED_KEYS = REQUIRED_KEYS

    def __init__(self, metadata):
        if not isinstance(metadata, dict):
            raise ValueError("The input metadata must be a dictionary.")
        if not self._has_required_keys(metadata):
            raise ValueError(
                f"The metadata must contain the following keys: {', '.join(self.REQUIRED_KEYS)}"
            )
        if not self._has_allowed_keys(metadata):
            raise ValueError(
                f"The metadata can only contain the following keys: {', '.join(self.ALLOWED_KEYS)}"
            )
        self.metadata = metadata

    def __str__(self):
        return f"VectorMetadata({self.metadata})"

    def get_metadata(self):
        return self.metadata

    def insert_metadata(self, key, value):
        if key not in self.ALLOWED_KEYS:
            raise ValueError(f"The key {key} is not allowed in the metadata.")
        self.metadata[key] = value

    def _has_required_keys(self, metadata):
        return all(key in metadata for key in self.REQUIRED_KEYS)

    def _has_allowed_keys(self, metadata):
        return all(key in self.ALLOWED_KEYS for key in metadata)

class PineconeVector:
    """
    A class to represent a vector in Pinecone.
    """

    id: str
    vector: VectorEmbedding
    meta: VectorMetadata

    def __init__(self, vector: VectorEmbedding, metadata: VectorMetadata):
        """
        Initializes a PineconeVector object.
        Args:
            vector (VectorEmbedding): The vector embedding.
            metadata (VectorMetadata): The metadata for the vector.
        """
        self.id = metadata.get_metadata()["id"]
        self.vector = vector
        self.meta = {k: v for k, v in metadata.get_metadata().items() if k != "id"}

    def to_triple(self):
        """
        Returns the PineconeVector object as a triple.
        """
        return self.id, self.vector, self.meta


def enrich_bot_knowledge_with_meta_data_tags(
    knowledge_chunk: str,
):
    meta = {
        "id": str(uuid.uuid4()),
        "text": knowledge_chunk,
    }
    return VectorMetadata(meta)


def batch_upsert_to_pinecone_db(index, pinecone_vectors: list[PineconeVector], namespace="dumb-bot-knowledge"):
    vectors = [pinecone_vector.to_triple() for pinecone_vector in pinecone_vectors]
    index.upsert(vectors=vectors, namespace=namespace)
    print(f"Successfully upserted {str(len(pinecone_vectors))} vectors to Pinecone index's namespace: {namespace}!")
    return

def add_doc_into_pinecone(index, path_to_doc: str, namespace="dumb-bot-knowledge"):
    chunks = turn_doc_into_chunks(path_to_doc)
    embeds = turn_chunks_into_embeddings(chunks)
    chunk_metadata = [enrich_bot_knowledge_with_meta_data_tags(chunk) for chunk in chunks]
    # turn the chunks into PineconeVector objects
    pinecone_vectors = [PineconeVector(embed, meta) for embed, meta in zip(embeds, chunk_metadata)]
    # upsert the PineconeVector objects into the Pinecone index
    batch_upsert_to_pinecone_db(index, pinecone_vectors, namespace)
    return

def delete_knowledge_by_namespace(index, namespace: str):
    index.delete(namespace=namespace, delete_all=True)
    print(
        f"""⚠️ Deleted all knowledge from the index namspace: {namespace}."""
    )
    return

def turn_query_into_embeddings(query: str):
    """
    Turn a query into embeddings using Pinecone
    """
    # turn query into embeddings
    query_embedding = voyageai.embed(
        [query], model="voyage-large-2", input_type="query"
    ).embeddings[0]
    return query_embedding

def search_vector_db_for_similar_vectors(
    question: str,
    namespace: str,
    top_k: int = 5,
    include_values: bool = False,
    include_metadata: bool = True,
) -> list[dict]:
    index = pinecone_index_conn
    embedded_question = turn_query_into_embeddings(question)
    # query the index for relevant knowledge
    query_response = index.query(
        namespace=namespace,
        top_k=top_k,
        include_values=include_values,
        include_metadata=include_metadata,
        vector=embedded_question,
    )
    # print(query_response)
    return query_response["matches"]

pinecone_index_conn = connect_pinecone_index()

if __name__ == "__main__":
    delete_knowledge_by_namespace(pinecone_index_conn, "dumb-bot-knowledge")
    dumb_bot_knowledge = "../snack_52/snack_52_docs_dumb.txt"
    add_doc_into_pinecone(pinecone_index_conn, dumb_bot_knowledge, namespace="dumb-bot-knowledge")

    delete_knowledge_by_namespace(pinecone_index_conn, "smart-bot-knowledge")
    dumb_bot_knowledge = "../snack_52/snack_52_docs_smart.txt"
    add_doc_into_pinecone(pinecone_index_conn, dumb_bot_knowledge, namespace="smart-bot-knowledge")

    # question = "What is snack 52?"
    # matches = search_vector_db_for_similar_vectors(question, "dumb-bot-knowledge")
    # print(matches)
