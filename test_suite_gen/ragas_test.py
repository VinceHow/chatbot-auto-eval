from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader
from ragas.testset.generator import TestsetGenerator
from ragas.testset.evolutions import simple, reasoning, multi_context
from test_suite_gen.conversation_evolution import conversation
from langchain.docstore.document import Document

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

load_dotenv()
path_to_doc = "test_suite_gen/test_docs/snack_52_docs_dumb.txt"
texts = turn_doc_into_chunks(path_to_doc)
documents = [Document(page_content=text, metadata={"source": "snack_52_docs_dumb.txt"}) for text in texts]

# generator with openai models
generator = TestsetGenerator.with_openai()
# generate testset
# testset = generator.generate_with_langchain_docs(documents, test_size=10, distributions={simple: 0.5, reasoning: 0.25, multi_context: 0.25})
testset = generator.generate_with_langchain_docs(documents, test_size=1, distributions={conversation: 1.0})
testset.to_pandas().to_csv("test_suite_gen/testset.csv", index=False)