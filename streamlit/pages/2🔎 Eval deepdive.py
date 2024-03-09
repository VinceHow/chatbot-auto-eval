import streamlit as st
from streamlit_extras.app_logo import add_logo
from authenticator.authenticate import get_authenticator
import pandas as pd

add_logo("http://placekitten.com/120/120")

TRADITIONAL_METRICS = ["faithfulness", "context_precision", "answer_relevancy", "context_recall"]

convo = {
    "id": "1",
    'conversation_seed': {'job_to_be_done': 'Discover new and unique snacks', 'user_query': 'What kind of snacks can I expect in each box?'}, 
    'interactions': [
        {'interaction_turn': 1, 'user_query': 'What kind of snacks can I expect in each box?', 'bot_response': "Each Snack 52 box contains a curated selection of premium, artisanal snacks from around the world. You'll discover unique flavors, healthy options, and indulgent treats tailored to your preferences. Our snack experts carefully source the finest snacks to delight your taste buds every month.", 'knowledge_used': [], 'evaluation': {'faithfulness': 0.0, 'context_precision': 0.0, 'answer_relevancy': 0.0, 'context_recall': 0.0}}
        ], 
    'interaction_turns': 3,
    'evaluation': "passed"
}

convos = [convo]


# extract metrics given convos
def extract_traditional_metrics(metric_name, convos):
    #construct a table sorting from value low to high
    traditional_metric_list = []
    for convo in convos:
        traditional_metric_dict = dict()
        traditional_metric_dict["conversation_id"] = convo["id"]
        interactions = convo["interactions"]
        sum_value = 0
        count_value = 0
        for interaction in interactions:
            sum_value += interaction["evaluation"][metric_name]
            count_value += 1
        traditional_metric_dict["value"] = sum_value/count_value
        traditional_metric_dict["convo_history"] = "/n".join([f"User query:{interaction['user_query']}, Bot response:{interaction['bot_response']}" for interaction in interactions])
        url = f"http://localhost:8501/Inspect_convo?convo_id={convo['id']}"
        traditional_metric_dict["convo_link"] = url
        traditional_metric_list.append(traditional_metric_dict)
    traditional_metric_df = pd.DataFrame(traditional_metric_list)
    traditional_metric_df = traditional_metric_df.sort_values(by="value")
    return traditional_metric_df



def extract_job_to_be_done_metrics(metric_name, convos):
    pass


def display_detail_eval(metric_name):
    st.markdown(f"### Detailed Eval for {metric_name}")
    if metric_name in TRADITIONAL_METRICS:
        metric_info = extract_traditional_metrics(metric_name, convos)
    else:
        metric_info = extract_job_to_be_done_metrics(metric_name, convos)
    avg_value = metric_info["value"].mean()
    st.metric(metric_name, avg_value)
    st.dataframe(metric_info, 
                 column_config={
                    "conversation_id": "Conversation ID",
                    "value": st.column_config.NumberColumn(
                        "Metric value",
                        help="Avg result of the metric for the conversation",
                        # format="%d ⭐",
                    ),
                    "convo_link": st.column_config.LinkColumn("Conversation URL", display_text="Open conversation"),
                    "convo_history": "Conversation history"
                    },
                hide_index=True)


authenticator = get_authenticator()
authenticator._check_cookie()

if st.session_state["authentication_status"]:
    with st.sidebar:
        authenticator.logout()
        st.write(f'Welcome *{st.session_state["name"]}*')
    if "metric_name" in st.query_params:
        display_detail_eval(st.query_params["metric_name"])
    else:
        st.error('Please select a metric to see the detailed eval')
        if st.button("Go back to dashboard"):
            st.switch_page("pages/1🕹️ Evaluation Dashboard.py")
else:
    st.error('Please login to see the detailed eval')
    if st.button("Go back to login"):
        st.switch_page("👋_Welcome.py")
