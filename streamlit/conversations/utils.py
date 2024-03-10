import pandas as pd
import streamlit as st
from collections import defaultdict

# extract metrics given convos
@st.cache_data(show_spinner=False)
def extract_traditional_metrics_from_convos(metric_name, convos, base_url, bot_type):
    #construct a table sorting from value low to high
    traditional_metric_list = []
    for convo in convos:
        traditional_metric_dict = dict()
        traditional_metric_dict["conversation_id"] = convo["convo_id"]
        interactions = convo["interactions"]
        sum_value = 0
        count_value = 0
        for interaction in interactions:
            sum_value += interaction["evaluation"][metric_name]
            count_value += 1
        traditional_metric_dict["name"] = metric_name
        traditional_metric_dict["value"] = sum_value/count_value
        traditional_metric_dict["convo_history"] = "/n".join([f"User query:{interaction['user_query']}, Bot response:{interaction['bot_response']}" for interaction in interactions])
        url = f"{base_url}/Inspect_convo?convo_id={convo['convo_id']}&bot_type={bot_type}"
        traditional_metric_dict["convo_link"] = url
        traditional_metric_list.append(traditional_metric_dict)
    traditional_metric_df = pd.DataFrame(traditional_metric_list)
    traditional_metric_df = traditional_metric_df.sort_values(by="value")
    return traditional_metric_df


def summarise_traditional_metrics(traditional_metric_df):
    summary_metric = dict()
    summary_metric["name"] = traditional_metric_df["name"].iloc[0]
    summary_metric["value"] = traditional_metric_df["value"].mean()
    summary_metric["status"] = "pass" if summary_metric["value"] > 0.5 else "fail"
    return summary_metric


@st.cache_data(show_spinner=False)
def extract_job_to_be_done_metrics(metric_name, convos, base_url, bot_type):
    # filter the convo to find the job to be done convos
    filtred_convos = []
    for convo in convos:
        if convo["conversation_seed"]["job_to_be_done"] == metric_name:
            filtred_convos.append(convo)
    jtd_metric_list = []
    for convo in filtred_convos:
        jtd_metric_dict = dict()
        jtd_metric_dict["conversation_id"] = convo["convo_id"]
        interactions = convo["interactions"]
        jtd_metric_dict["name"] = metric_name
        jtd_metric_dict["quality_score"] = convo["evaluation"]["quality_score"]
        jtd_metric_dict["reasoning"] = convo["evaluation"]["reasoning"]
        jtd_metric_dict["convo_start"] = interactions[0]["user_query"]
        jtd_metric_dict["convo_history"] = "/n".join([f"User query:{interaction['user_query']}, Bot response:{interaction['bot_response']}" for interaction in interactions])
        url = f"{base_url}/Inspect_convo?convo_id={convo['convo_id']}&bot_type={bot_type}"
        jtd_metric_dict["convo_link"] = url
        jtd_metric_list.append(jtd_metric_dict)
    jtd_metric_df = pd.DataFrame(jtd_metric_list)
    jtd_metric_df = jtd_metric_df.sort_values(by="quality_score")
    return jtd_metric_df


def summarise_jtd_metrics(jtd_metric_df):
    job_to_be_done_metric_dict = dict()
    print(jtd_metric_df.head())
    job_to_be_done_metric_dict["name"] = jtd_metric_df["name"].iloc[0]
    job_to_be_done_metric_dict["number_of_convo"] = len(jtd_metric_df)
    job_to_be_done_metric_dict["quality_score"] = jtd_metric_df["quality_score"].mean()
    job_to_be_done_metric_dict["status"] = "pass" if job_to_be_done_metric_dict["quality_score"] > 0.5 else "fail"
    return job_to_be_done_metric_dict

    
def retrieve_convo_by_id(convo_id, convo_list):
    for convo in convo_list:
        if convo["convo_id"] == convo_id:
            return convo
