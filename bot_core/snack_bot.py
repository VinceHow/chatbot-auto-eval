import anthropic
import os
from dotenv import load_dotenv
import json
import sys
import os
import json
import tqdm
import uuid
# Get the directory containing your current script
current_dir = os.path.dirname(os.path.abspath(__file__))
# Get the parent directory
parent_dir = os.path.dirname(current_dir)
# Add the parent directory to the Python path
sys.path.append(parent_dir)
import vector_db.pinecone_db as pinecone_db
from snack_52.sample_questions import sample_questions
from snack_52.jobs_to_be_done import jobs_to_be_done
from bot_eval import (
    evaluate_single_interaction, 
    InteractionEvaluation, 
    ConversationEvaluation
)

load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

client = anthropic.Anthropic()

# open the doc and read content as string
path_to_dumb_system_prompt = "../bot_core/bot_system_prompt_dumb.txt"
with open(path_to_dumb_system_prompt, 'r') as file:
    dumb_system_prompt = file.read()

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
            # allow the evaluation to be exported as None dictionary
            "evaluation": self.evaluation.to_dict() if self.evaluation else {0.0}
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

class UserBotConversation:
    # a conversation is a list of interactions, plus some additional fields
    def __init__(self, convo_id: str, interactions: list[UserBotInteraction], conversation_seed: ConversationSeed = None, conversation_evaluation: ConversationEvaluation = 0.0):
        self.convo_id = convo_id
        self.conversation_seed = conversation_seed
        self.interactions = interactions
        self.interaction_turns = len(interactions)
        self.evaluation = conversation_evaluation
    # export the conversation as a dictionary
    def to_dict(self):
        return {
            "convo_id": self.convo_id,
            "interaction_turns": self.interaction_turns,
            "conversation_seed": self.conversation_seed.to_dict(),
            "interactions": [interaction.to_dict() for interaction in self.interactions],
            "evaluation": self.evaluation.to_dict() if self.evaluation else 0.0
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

def create_conversation_history(conversation: UserBotConversation) -> list[dict]:
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
                        namespace:str,
                        pull_knowledge: bool = True,
                        temperature: float = 0.0,
                        max_tokens: int = 75,):
    convo_history = create_conversation_history(conversation)
    convo_history.append({"role": "user", "content": query})
    if pull_knowledge:
        knowledge_string, knowledge_vectors = fetch_knowledge_from_pinecone_db(query, namespace, top_k=5)
        # replace {KNOWLEDGE_FROM_PINECONE} with the knowledge string
        system_prompt = system_prompt.replace("{KNOWLEDGE_FROM_PINECONE}", knowledge_string)
    else:
        knowledge_vectors = []
    response = client.messages.create(
        # model="claude-3-sonnet-20240229",
        model="claude-3-opus-20240229",
        max_tokens=max_tokens,
        temperature=temperature,
        system=system_prompt,
        messages= convo_history
    )
    reponse_text = response.content[0].text
    return reponse_text, knowledge_vectors

def create_convo_string(conversation: UserBotConversation):
    convo_string = ""
    past_convo = create_conversation_history(conversation)
    # turn the past_convo into a single string
    for interaction in past_convo:
        if interaction["role"] == "user":
            convo_string = convo_string + "User: "+ interaction["content"][0]["text"] + "\n"
        else:
            convo_string = convo_string + "Assistant: "+ interaction["content"][0]["text"] + "\n"
    return convo_string

def complete_single_user_bot_interaction(
        conversation: UserBotConversation, 
        user_query: str, 
        system_prompt: str,
        namespace: str,
        pull_knowledge: bool = True,
        run_evaluation: bool = True):
    bot_response, knowledge_vectors = get_claude_response(
        user_query, 
        system_prompt,
        conversation,
        namespace,
        pull_knowledge=pull_knowledge,
        )
    interaction = UserBotInteraction(conversation.interaction_turns + 1, user_query, bot_response, knowledge_vectors, InteractionEvaluation())
    if run_evaluation:
        interaction.evaluation =evaluate_single_interaction(interaction.to_dict())
    else:
        interaction.evaluation = InteractionEvaluation(0.0, 0.0, 0.0, 0.0)
    # add the interaction to the conversation
    conversation.interactions.append(interaction)
    # update the conversation's interaction turns
    conversation.interaction_turns = len(conversation.interactions)
    return conversation

def simulate_user_follow_up_question(conversation: UserBotConversation):
    # init a temp conversation object
    convo = UserBotConversation(convo_id="", interactions=[])
    system_prompt = f"""Imagine you are the user who started the below conversation, with the goal of completing the taks of: {conversation.conversation_seed.job_to_be_done}.
You have a follow-up question, what would you ask the assistant? 
Reply with the follow-up question only and nothing else."""
    # convo to-this-point
    user_query = create_convo_string(conversation)
    convo = complete_single_user_bot_interaction(
        convo, 
        user_query, 
        system_prompt,
        namespace= "", # not needed
        pull_knowledge=False, # not needed
        run_evaluation=False # not needed
        )
    # return the last interaction
    return convo.interactions[-1].bot_response

def simulate_user_bot_conversation(conversation_seed: ConversationSeed, 
                                   system_prompt: str,
                                   namespace: str, 
                                   max_interactions: int = 1):
    # init a temp conversation object, with a unique id
    convo = UserBotConversation(convo_id= str(uuid.uuid4()), interactions=[], conversation_seed= conversation_seed)
    # start the conversation
    convo = complete_single_user_bot_interaction(
        convo, 
        convo.conversation_seed.user_query, 
        system_prompt,
        namespace= namespace, # use this to swap between different knowledge bases
        pull_knowledge=True, # pull knowledge from Pinecone
        run_evaluation=True # run the evaluation
        )
    interaction_count = 1
    # continue the conversation with a few more interactions
    while interaction_count < max_interactions:
        # simulate a user follow-up question
        follow_up_q = simulate_user_follow_up_question(convo)
        convo = complete_single_user_bot_interaction(
            convo, 
            follow_up_q, 
            system_prompt,
            namespace= namespace, # use this to swap between different knowledge bases
            pull_knowledge=True, # pull knowledge from Pinecone
            run_evaluation=True # run the evaluation
            )
        interaction_count += 1
    convo.evaluation = evaluate_whole_conversation(convo)
    return convo

def store_simulated_conversations(conversations: list[UserBotConversation], file_path: str = "../bot_core/conversations_dumb.py", delete_first: bool = False):
    if delete_first:
        # delete the contents of the file
        open(file_path, "w").close()
    with open(file_path, "a") as file:
        file.write(f"conversations = [\n")
        for convo in conversations:
            file.write(f"{convo.to_dict()},\n")
        file.write(f"]\n")
    return

def pretty_print_stored_conversation(conversation: dict, ignore_knowledge: bool = True):
    if ignore_knowledge:
        # show the conversation without the knowledge vectors, keeping the evaluation
        convo = conversation.copy()
        for interaction in convo["interactions"]:
            interaction.pop("knowledge_used")
        print(json.dumps(convo, indent=4))
        return
    else:
        print(json.dumps(conversation, indent=4))
        return

def evaluate_whole_conversation(conversation: UserBotConversation):
#  -> ConversationEvaluation:
    # for all interactions in the conversation, find the interaction evaluations
    # across the 4 dimensions of interaction evaluation, take the min value for each dimension
    # summarise the interaction evaluations into a conversation evaluation
    interaction_evaluations = []
    for interaction in conversation.interactions:
        interaction_evaluations.append(interaction.evaluation.to_dict())
    
    interaction_evaluation = {
        "faithfulness": min([interaction_eval["faithfulness"] for interaction_eval in interaction_evaluations]),
        "context_precision": min([interaction_eval["context_precision"] for interaction_eval in interaction_evaluations]),
        "answer_relevancy": min([interaction_eval["answer_relevancy"] for interaction_eval in interaction_evaluations]),
        "context_recall": min([interaction_eval["context_recall"] for interaction_eval in interaction_evaluations]),
    }
    # convert the interaction_evaluation to a string, so that it can be injected into the prompt
    interaction_evaluation = str(interaction_evaluation).replace("{", "").replace("}", "").replace(",", "\n")

    system_prompt = f"""Consider the following metrics:
Faithfulness: factual consistency of the answer to the context (0-1)
Context_precision: relevance of the retrieved context to the question (0-1)
Answer_relevancy: relevance of the answer to the question (0-1)
Context_recall: retriever's ability to retrieve necessary information (0-1)

Bot scores:
{interaction_evaluation}

Provide an overall quality score (0-1) for the entire conversation based on whether the bot helped the user to achieve their original Job to be Done, needs, and motivations, and whether the bot answered the user's questions Faithfulness, precisely, and was relevant."""
    system_prompt = system_prompt + """
Return only the JSON result with keys, and nothing else:
{
"quality_score": float,
"reasoning": str (within 30 words)
}

Start your response with:
{
"quality_score":
"""
    user_query = create_convo_string(conversation)    
    convo = UserBotConversation(convo_id = "temp", interactions=[])
    convo = complete_single_user_bot_interaction(
        convo, 
        user_query,
        system_prompt,
        namespace= "", # not needed 
        pull_knowledge=False, # not needed
        run_evaluation=False # not needed
        )

    response_raw = convo.interactions[-1].bot_response
    try:
        # turn the bot response into a dictionary
        response = json.loads(response_raw)
    except:
        print(f"Failed to process the response as dict: {response_raw}")
        response = {"quality_score": 0.0, "reasoning": response_raw}
    # turn the response into a ConversationEvaluation object
    response = ConversationEvaluation(response["quality_score"], response["reasoning"])
    return response

def get_questions_for_job_to_be_done(job_to_be_done: str):
    # get the questions for the job to be done by filtering the sample_questions
    # each item in sample_questions looks like this: {'job-to-be-done': 'Support small and artisanal snack brands', 'initial-questions': ['Do you feature snacks from small or local businesses?', 'Do you feature snacks from businesses from other countries?', 'What are examples of brands that you support in your bundles?', 'Are there any exclusive or limited-edition snacks from these artisanal brands?']}
    questions = [job["initial-questions"] for job in sample_questions if job["job-to-be-done"] == job_to_be_done][0]
    return questions

def run_end_to_end_eval_for_bot(
    job_to_be_done: str,
    system_prompt: str,
    namespace: str,
    max_interactions: int = 3,
    file_path: str = "../bot_core/conversations_dumb.py",
    delete_first: bool = False
    ):
    # get the initial questions for the job to be done
    questions = get_questions_for_job_to_be_done(job_to_be_done)
    convos = []
    for q in tqdm.tqdm(questions):
        conversation_seed = ConversationSeed(job_to_be_done, q)
        # simulate the conversation
        convo = simulate_user_bot_conversation(
            conversation_seed, 
            system_prompt,
            namespace,
            max_interactions
            )
        convos.append(convo)
    # store the conversation
    store_simulated_conversations(convos, file_path, delete_first)
    return

if __name__ == "__main__":
    # seed some conversations
    jobs = [job["job-to-be-done"] for job in jobs_to_be_done]
    for job in jobs:
        run_end_to_end_eval_for_bot(
            job_to_be_done=job,
            system_prompt=dumb_system_prompt,
            namespace="dumb-bot-knowledge",
            max_interactions=3,
            file_path="../bot_core/conversations_dumb.py",
            delete_first=False
        )
    for job in jobs:
        run_end_to_end_eval_for_bot(
            job_to_be_done=job,
            system_prompt=dumb_system_prompt,
            namespace="smart-bot-knowledge",
            max_interactions=3,
            file_path="../bot_core/conversations_smart.py",
            delete_first=False
        )
