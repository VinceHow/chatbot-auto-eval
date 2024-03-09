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
from snack_bot import InteractionEvaluation, pretty_print_stored_conversation

# Get the directory containing your current script
current_dir = os.path.dirname(os.path.abspath(__file__))
# Get the parent directory
parent_dir = os.path.dirname(current_dir)
# Add the parent directory to the Python path
sys.path.append(parent_dir)
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def evaluate_single_interaction(interaction) -> InteractionEvaluation:
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
