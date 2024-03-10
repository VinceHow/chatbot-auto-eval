from snack_bot import (
    get_claude_response, 
    ConversationSeed, 
    ConversationEvaluation, 
    UserBotConversation
)
from conversations_dumb import (
    conversations_job_1 as dumb_conversations_job_1,
    conversations_job_2 as dumb_conversations_job_2,
    conversations_job_3 as dumb_conversations_job_3,
    conversations_job_4 as dumb_conversations_job_4,
    conversations_job_5 as dumb_conversations_job_5,
)
from conversations_smart import (
    conversations_job_1 as smart_conversations_job_1,
    conversations_job_2 as smart_conversations_job_2,
    conversations_job_3 as smart_conversations_job_3,
    conversations_job_4 as smart_conversations_job_4,
    conversations_job_5 as smart_conversations_job_5,
)
import pandas as pd
import tqdm
import os
import sys
# Get the directory containing your current script
current_dir = os.path.dirname(os.path.abspath(__file__))
# Get the parent directory
parent_dir = os.path.dirname(current_dir)
# Add the parent directory to the Python path
sys.path.append(parent_dir)

class SeedConvoEval:
    def __init__(self, seed: ConversationSeed, eval: ConversationEvaluation):
        self.seed = seed
        self.eval = eval
    def to_dict(self):
        return {
            "seed": self.seed.to_dict(),
            "evaluation": self.eval.to_dict()
        }

def get_convo_evaluations(conversations: list[dict]):
    evals = []
    for conversation in conversations:
        eval = conversation["evaluation"]
        evals.append(eval)
    return evals

def get_convo_seeds(conversations: list[dict]):
    seeds = []
    for conversation in conversations:
        seed = conversation["conversation_seed"]
        seeds.append(seed)
    return seeds

def get_eval_df_from_single_collection(conversations: list[dict]):
    # Get the seeds and evaluations
    seeds = get_convo_seeds(conversations)
    evals = get_convo_evaluations(conversations)
    # Convert dictionaries to DataFrames
    df1 = pd.DataFrame(seeds)
    df2 = pd.DataFrame(evals)

    # Zip the two DataFrames together
    combined_df = pd.concat([df1, df2], axis=1)
    return combined_df

def get_eval_df_from_multiple_collections(conversations: list[list[dict]]):
    # Get the seeds and evaluations
    seeds = []
    evals = []
    for collection in conversations:
        seeds.extend(get_convo_seeds(collection))
        evals.extend(get_convo_evaluations(collection))
    # Convert dictionaries to DataFrames
    df1 = pd.DataFrame(seeds)
    df2 = pd.DataFrame(evals)

    # Zip the two DataFrames together
    combined_df = pd.concat([df1, df2], axis=1)
    return combined_df

class JobImprovmentSuggestion:
    def __init__(self, bot_name: str, job_to_be_done: str, suggestion: str):
        self.bot_name = bot_name
        self.job_to_be_done = job_to_be_done
        self.suggestion = suggestion
    def to_dict(self):
        return {
            "bot_name": self.bot_name,
            "job_to_be_done": self.job_to_be_done,
            "suggestion": self.suggestion
        }

def get_suggestion_on_how_to_improve_conversation(eval_df: pd.DataFrame, 
                                                  job_to_be_done: str,
                                                  bot_name: str) -> JobImprovmentSuggestion:
    # Get the rows that match the job to be done
    matching_rows = eval_df[eval_df["job_to_be_done"] == job_to_be_done]
    # turn the matching rows into a list of dictionaries, and then as a string
    matching_rows_dict = matching_rows.to_dict(orient="records")
    matching_rows_str = str(matching_rows_dict)

    system_prompt = """You will be provided with a list of conversations and evaluations that occurred between a bot and a user. You will be asked to provide some suggestions on how to improve the conversation. Use markdown to format your response.
Breakdown your feedback into the following secions:
### What was good about the conversations?
### What could be improved about the conversations?
### Specific actions that the bot maker could take to improve the conversations. (e.g. The bot should be supplied with additional knowledge about allergens in snacks.)
"""
    improve_suggest, _ = get_claude_response(
                        query = matching_rows_str, 
                        system_prompt = system_prompt, 
                        conversation = UserBotConversation(convo_id="", interactions=[]),
                        namespace = "",
                        pull_knowledge = False,
                        max_tokens = 500,)
    
    # turn into an JobImprovmentSuggestion object
    job_suggestion = JobImprovmentSuggestion(bot_name=bot_name, job_to_be_done=job_to_be_done, suggestion=improve_suggest)

    return job_suggestion

def write_suggestion_to_file(
        bot_name: str,
        suggestion: JobImprovmentSuggestion, 
        file_path: str= "../bot_core/suggsted_improvements.py"):
    suggestion_as_dict = suggestion.to_dict()
    suggestion_as_str = str(suggestion_as_dict)
    print(f"Writing suggestions to {file_path}: {suggestion_as_str}")
    # append the suggestion to the file
    with open(file_path, "a") as file:
        file.write(f"suggestion_for_{bot_name} = ")
        file.write(suggestion_as_str + "\n")
    return

def loop_through_jobs_and_store_suggestions(conversation_dfs: list[pd.DataFrame], bot_name: str, file_path: str= "../bot_core/suggsted_improvements.py"):
    eval_df = get_eval_df_from_multiple_collections(conversation_dfs)
    unique_job_to_be_done = eval_df['job_to_be_done'].unique()
    suggestions = []
    for job in tqdm.tqdm(unique_job_to_be_done):
        suggest = get_suggestion_on_how_to_improve_conversation(eval_df, job, bot_name)
        write_suggestion_to_file(bot_name, suggest, file_path)
        print(suggest.suggestion)
        suggestions.append(suggest)
    return suggestions

if __name__ == "__main__":
    dumb_convos = [
        dumb_conversations_job_1,
        dumb_conversations_job_2,
        dumb_conversations_job_3,
        dumb_conversations_job_4,
        dumb_conversations_job_5,
    ]
    suggestions = loop_through_jobs_and_store_suggestions(dumb_convos, "dumb")

    smart_convos = [
        smart_conversations_job_1,
        smart_conversations_job_2,
        smart_conversations_job_3,
        smart_conversations_job_4,
        smart_conversations_job_5,
    ]
    suggestions = loop_through_jobs_and_store_suggestions(smart_convos, "smart")