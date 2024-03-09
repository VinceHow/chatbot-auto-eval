from pinecone import Pinecone
import voyageai
from dotenv import load_dotenv
import os
load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
VOYAGEAI_API_KEY = os.getenv("VOYAGEAI_API_KEY")

# create Pinecone object
pc = Pinecone(PINECONE_API_KEY)
vo = voyageai.Client()

# read in raw text data from ./snack_52/snack_52_docs_dumb.txt
with open('./snack_52/snack_52_docs_dumb.txt', 'r') as file:
    snack_52_docs_dumb = file.read()

# chunk the raw text data into paragraphs
snack_52_docs_dumb = snack_52_docs_dumb.split('\n\n')

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
    # create a new Pinecone index
    pc.create_index(
        name='snack_52', 
        dimension=1024, 
        metric="cosine", 
        spec=pc.PodSpec(environment="gcp-starter")
    )

    # add documents to the Pinecone index
    for i, doc in enumerate(snack_52_docs_dumb):
        pc.insert_items("snack_52", [doc], [i])

    # query the Pinecone index
    query = "What are the nutritional facts of each snack?"
    results = pc.query("snack_52", [query], top_k=3)
    print(results)

    # query the Voyage AI API
    response = vo.query(VOYAGEAI_API_KEY, query, "snack_52")
    print(response)