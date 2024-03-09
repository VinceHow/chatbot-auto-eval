from ragas.metrics import (
    answer_relevancy,
    faithfulness,
    context_recall,
    context_precision,
)
from ragas import evaluate
from dotenv import load_dotenv
from datasets import Dataset
import os
import sys
from conversations_dumb import *


# Get the directory containing your current script
current_dir = os.path.dirname(os.path.abspath(__file__))
# Get the parent directory
parent_dir = os.path.dirname(current_dir)
# Add the parent directory to the Python path
sys.path.append(parent_dir)
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
"""
Faithfulness - Measures the factual consistency of the answer to the context based on the question.
Context_precision - Measures how relevant the retrieved context is to the question, conveying the quality of the retrieval pipeline.
Answer_relevancy - Measures how relevant the answer is to the question.
Context_recall - Measures the retriever's ability to retrieve all necessary information required to answer the question.
"""
conversations = [conversation_1]
                #  , conversation_2, conversation_3, conversation_4, conversation_5]
data_samples = {
    "question": [],
    "answer": [],
    "contexts": [],
    "ground_truth": [],
}
for conversation in conversations:
    for turn in conversation["interactions"]:
        data_samples["question"].append(turn["user_query"])
        data_samples["answer"].append(turn["bot_response"])
        knowledge_used = [knowledge["metadata"]["text"] for knowledge in turn["knowledge_used"]]
        data_samples["contexts"].append(knowledge_used)
        data_samples["ground_truth"].append(knowledge_used[0])

# process the data into Dataset format
data_samples = Dataset.from_dict(data_samples)



result = evaluate(
    data_samples,
    metrics=[
        context_precision,
        faithfulness,
        answer_relevancy,
        context_recall,
    ],
)

# result
if __name__ == "__main__":
    # print(os.environ["OPENAI_API_KEY"])
    print(result)
