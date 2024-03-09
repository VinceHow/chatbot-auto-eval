import anthropic
import os
from dotenv import load_dotenv
import json
import sys
import os
import json
import tqdm
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
path_to_dumb_system_prompt = "../bot_core/bot_system_prompt_dumb.txt"
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
    def __init__(self, interactions: list[UserBotInteraction], conversation_seed: ConversationSeed = None, conversation_evaluation: ConversationEvaluation = None):
        self.conversation_seed = conversation_seed
        self.interactions = interactions
        self.interaction_turns = len(interactions)
        self.evaluation = conversation_evaluation
    # export the conversation as a dictionary
    def to_dict(self):
        return {
            "interaction_turns": self.interaction_turns,
            "conversation_seed": self.conversation_seed.to_dict(),
            "interactions": [interaction.to_dict() for interaction in self.interactions],
            "evaluation": self.evaluation.to_dict() if self.evaluation else None
        }

def fetch_knowledge_from_pinecone_db(query: str, namespace: str, top_k: int = 5):
    knowledge_vectors = pinecone_db.search_vector_db_for_similar_vectors(
        query,
        namespace,
        top_k
    )
    knowledge_string = ""
    for i in knowledge_vectors:
        knowledge_string = knowledge_string + i["metadata"]["text"] + "\n"    
    return knowledge_string, knowledge_vectors

def create_conversation_history(conversation: UserBotConversation):
    convo_history = []
    for interaction in conversation.interactions:
        user_message = {"role": "user","content": [{"type": "text", "text": interaction.user_query}]}
        bot_message = {"role": "assistant","content": [{"type": "text", "text": interaction.bot_response}]}
        convo_history.append(user_message)
        convo_history.append(bot_message)
    return convo_history

def get_claude_response(query: str, 
                        system_prompt: str, 
                        conversation: UserBotConversation,
                        temperature: float = 0.0,):
    convo_history = create_conversation_history(conversation)
    convo_history.append({"role": "user", "content": query})
    knowledge_string, knowledge_vectors = fetch_knowledge_from_pinecone_db(query, "dumb-bot-knowledge")
    # replace {KNOWLEDGE_FROM_PINECONE} with the knowledge string
    system_prompt = system_prompt.replace("{KNOWLEDGE_FROM_PINECONE}", knowledge_string)
    # print(system_prompt)
    response = client.messages.create(
        model="claude-3-sonnet-20240229",
        # model="claude-3-opus-20240229",
        max_tokens=200,
        temperature=temperature,
        system=system_prompt,
        messages= convo_history
    )
    reponse_text = response.content[0].text
    return reponse_text, knowledge_vectors

def complete_single_user_bot_interaction(conversation: UserBotConversation, user_query: str, system_prompt: str):
    bot_response, knowledge_vectors = get_claude_response(user_query, system_prompt, conversation)
    evaluation = InteractionEvaluation(0.0, 0.0, 0.0, 0.0)
    interaction = UserBotInteraction(conversation.interaction_turns + 1, user_query, bot_response, knowledge_vectors, evaluation)
    # add the interaction to the conversation
    conversation.interactions.append(interaction)
    # update the conversation's interaction turns
    conversation.interaction_turns = len(conversation.interactions)
    return conversation

def simulate_user_follow_up_question(conversation: UserBotConversation):
    # init a temp conversation object
    convo = UserBotConversation([])
    system_prompt = f"""Imagine you are the user who started the below conversation, with the goal of completing the taks of: {conversation.conversation_seed.job_to_be_done}. 
You have a follow-up question, what would you ask the assistant? Reply with the follow-up question only."""
    print(system_prompt)
    # convo to-this-point
    user_query = ""
    past_convo = create_conversation_history(conversation)
    # turn the past_convo into a single string
    for interaction in past_convo:
        if interaction["role"] == "user":
            user_query = user_query + "User: "+ interaction["content"][0]["text"] + "\n"
        else:
            user_query = user_query + "Assistant: "+ interaction["content"][0]["text"] + "\n"
    
    print(user_query)
    convo = complete_single_user_bot_interaction(convo, user_query, system_prompt)
    # return the last interaction
    return convo.interactions[-1].bot_response

def simulate_user_bot_conversation(conversation_seed: ConversationSeed, system_prompt: str, max_interactions: int = 1):
    convo = UserBotConversation([], conversation_seed)
    # start the conversation
    convo = complete_single_user_bot_interaction(convo, convo.conversation_seed.user_query, system_prompt)
    interaction_count = 1
    # continue the conversation with a few more interactions
    while interaction_count < max_interactions:
        # simulate a user follow-up question
        follow_up_q = simulate_user_follow_up_question(convo)
        convo = complete_single_user_bot_interaction(convo, follow_up_q, system_prompt)
        interaction_count += 1
    return convo

def store_simulated_conversation(conversation: UserBotConversation, id: str = None):
    with open("../bot_core/conversations_dumb.py", "a") as file:
        file.write(f"conversation_{id} = {conversation.to_dict()}\n")
    return

if __name__ == "__main__":
    # seed some conversations
    job_to_be_done = sample_questions.sample_questions[2]['job-to-be-done']
    questions = sample_questions.sample_questions[2]['initial-questions']
    print(f"JTBD: {job_to_be_done}\nQuestion: {questions}")
    id = 1
    # using TQDM to show a progress bar
    for question in tqdm.tqdm(questions):
        # create a conversation seed
        seed = ConversationSeed(job_to_be_done, question)
        convo = simulate_user_bot_conversation(seed, dumb_system_prompt, 2)
        convo.evaluation = ConversationEvaluation(0.8)
        store_simulated_conversation(convo, id=id)
        id += 1
