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
import json

# Get the directory containing your current script
current_dir = os.path.dirname(os.path.abspath(__file__))
# Get the parent directory
parent_dir = os.path.dirname(current_dir)
# Add the parent directory to the Python path
sys.path.append(parent_dir)
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class InteractionEvaluation:
    # an interaction will be evaluated based on the following criteria:
    # Faithfulness - Measures the factual consistency of the answer to the context based on the question.
    # Context_precision - Measures how relevant the retrieved context is to the question, conveying the quality of the retrieval pipeline.
    # Answer_relevancy - Measures how relevant the answer is to the question.
    # Context_recall - Measures the retriever’s ability to retrieve all necessary information required to answer the question.
    def __init__(self, faithfulness: float = 0, context_precision: float = 0, answer_relevancy: float = 0, context_recall: float = 0):
        self.faithfulness = faithfulness
        self.context_precision = context_precision
        self.answer_relevancy = answer_relevancy
        self.context_recall = context_recall
    # export the evaluation as a dictionary
    def to_dict(self):
        return {
            "faithfulness": self.faithfulness,
            "context_precision": self.context_precision,
            "answer_relevancy": self.answer_relevancy,
            "context_recall": self.context_recall
        }

def evaluate_single_interaction(interaction:dict) -> InteractionEvaluation:
    knowledge_used = [knowledge["metadata"]["text"] for knowledge in interaction["knowledge_used"]]

    interaction = Dataset.from_dict({
        "question": [interaction["user_query"]],
        "answer": [interaction["bot_response"]],
        "contexts": [knowledge_used],
        # TODO: add the synthetic ground truth
        "ground_truth": [knowledge_used[0]],
    })

    eval_result = evaluate(
        interaction,
        metrics=[
            context_precision,
            faithfulness,
            answer_relevancy,
            context_recall,
        ],
    )

    interaction_evaluation = InteractionEvaluation(
        faithfulness=eval_result["faithfulness"],
        context_precision=eval_result["context_precision"],
        answer_relevancy=eval_result["answer_relevancy"],
        context_recall=eval_result["context_recall"],
    )

    return interaction_evaluation

def pretty_print_stored_conversation(conversation: dict, ignore_knowledge: bool = True):
    if ignore_knowledge:
        # show the conversation without the knowledge vectors, keeping the evaluation
        convo = conversation.copy()
        for interaction in convo["interactions"]:
            interaction.pop("knowledge_used")
        print(json.dumps(convo, indent=4))
    else:
        print(json.dumps(conversation, indent=4))

if __name__ == "__main__":
    conversations = [conversation_1]
                    #  , conversation_2, conversation_3, conversation_4, conversation_5]
    interaction_evals = []
    for conversation in conversations:
        for interaction in conversation["interactions"]:
            interaction_eval = evaluate_single_interaction(interaction)
            interaction_evals.append(interaction_eval)
            # make the update to the hard copy of the interaction in the source file in code
            interaction["evaluation"] = interaction_eval.to_dict()
    pretty_print_stored_conversation(conversations[0])
