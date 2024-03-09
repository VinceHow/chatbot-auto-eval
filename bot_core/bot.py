import anthropic
import os
from dotenv import load_dotenv
import numpy as np
import uuid
import sys
import os
# Get the directory containing your current script
current_dir = os.path.dirname(os.path.abspath(__file__))
# Get the parent directory
parent_dir = os.path.dirname(current_dir)
# Add the parent directory to the Python path
sys.path.append(parent_dir)
import vector_db.pinecone_db as pinecone_db
import snack_52.sample_questions as sample_questions

load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

client = anthropic.Anthropic()

# open the doc and read content as string
path_to_dumb_system_prompt = "../bot_core/dumb_bot_system_prompt.txt"
with open(path_to_dumb_system_prompt, 'r') as file:
    dumb_system_prompt = file.read()

class InteractionEvaluation:
    # an interaction will be evaluated based on the following criteria:
    # Faithfulness - Measures the factual consistency of the answer to the context based on the question.
    # Context_precision - Measures how relevant the retrieved context is to the question, conveying the quality of the retrieval pipeline.
    # Answer_relevancy - Measures how relevant the answer is to the question.
    # Context_recall - Measures the retriever’s ability to retrieve all necessary information required to answer the question.
    def __init__(self, faithfulness: float, context_precision: float, answer_relevancy: float, context_recall: float):
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

class UserBotInteraction:
    # an interaction has 4 parts: user query, bot response, knowledge base used, and automated evaluation
    def __init__(self, interaction_turn: int, user_query: str, bot_response: str, knowledge_used: list, evaluation: InteractionEvaluation):
        self.interaction_turn = interaction_turn
        self.user_query = user_query
        self.bot_response = bot_response
        self.knowledge_used = knowledge_used
        self.evaluation = evaluation

    # export the interaction as a dictionary
    def to_dict(self):
        return {
            "interaction_turn": self.interaction_turn,
            "user_query": self.user_query,
            "bot_response": self.bot_response,
            "knowledge_used": self.knowledge_used,
            "evaluation": self.evaluation.to_dict()
        }

class ConversationSeed:
    # the see is the initial Job to be Done and the initial user query
    def __init__(self, job_to_be_done: str, user_query: str):
        self.job_to_be_done = job_to_be_done
        self.user_query = user_query
    # export the seed as a dictionary
    def to_dict(self):
        return {
            "job_to_be_done": self.job_to_be_done,
            "user_query": self.user_query
        }

class ConversationEvaluation:
    # a conversation will be evaluated based on the following criteria:
    # Helpfulness - Did the bot help the user achieve their JTBD?
    def __init__(self, helpfulness: float):
        self.helpfulness = helpfulness
    # export the evaluation as a dictionary
    def to_dict(self):
        return {
            "helpfulness": self.helpfulness
        }


class UserBotConversation:
    # a conversation is a list of interactions, plus some additional fields
    def __init__(self, interactions: list[UserBotInteraction], conversation_seed: ConversationSeed, conversation_evaluation: ConversationEvaluation = None):
        self.conversation_seed = conversation_seed
        self.interactions = interactions
        self.interaction_turns = len(interactions)
        self.evaluation = conversation_evaluation
    # export the conversation as a dictionary
    def to_dict(self):
        return {
            "conversation_seed": self.conversation_seed.to_dict(),
            "interactions": [interaction.to_dict() for interaction in self.interactions],
            "interaction_turns": self.interaction_turns,
            "evaluation": self.evaluation.to_dict() if self.evaluation else None
        }


def get_claude_response(query: str, system_prompt: str, convo_history: list = []):
    messages = convo_history
    messages.append({"role": "user", "content": query})
    response = client.messages.create(
        model="claude-3-sonnet-20240229",
        # model="claude-3-opus-20240229",
        max_tokens=200,
        temperature=0,
        system=system_prompt,
        messages=[
            {"role": "user", "content": query}
        ]
    )
    return response.content[0].text

if __name__ == "__main__":
    # seed some conversations
    job_to_be_done = sample_questions.sample_questions[0]['job-to-be-done']
    question = sample_questions.sample_questions[0]['initial-questions'][0]
    seed = ConversationSeed(job_to_be_done, question)
    # print out the seed, on 2 lines
    print(f"JTBD: {seed.job_to_be_done}\nQuestion: {seed.user_query}")
    # seed a conversation
    convo = UserBotConversation([], seed)
    # create the first interaction
    user_query = seed.user_query
    bot_response = get_claude_response(user_query, dumb_system_prompt)

    knowledge_used = []
    evaluation = InteractionEvaluation(0.0, 0.0, 0.0, 0.0)
    interaction = UserBotInteraction(1, user_query, bot_response, knowledge_used, evaluation)
    # add the interaction to the conversation
    convo.interactions.append(interaction)
    # print out the conversation
    print(f"Conversation Seed: {convo.conversation_seed.job_to_be_done}\n")
    for interaction in convo.interactions:
        print(f"User: {interaction.user_query}\nBot: {interaction.bot_response}\n")
    # store the conversation in a list and append to a py file
    # append the conversation to a py file
    with open("../bot_core/conversations.py", "a") as file:
        file.write(f"convo = {convo.to_dict()}\n")
