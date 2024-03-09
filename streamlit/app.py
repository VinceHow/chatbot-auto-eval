import os
import uuid
from datetime import datetime

# from openai import OpenAI
from streamlit_option_menu import option_menu

import streamlit as st


def get_running_environment():
    # Check for ECS environment variables
    if os.getenv("ECS_CONTAINER_METADATA_URI") or os.getenv("ECS_CLUSTER"):
        return "ECS"
    else:
        return "LOCAL"

# Initialise the context
# Set a default model
# if "openai_model" not in st.session_state:
#     st.session_state.openai_model = []
# if "logged_prompt" not in st.session_state:
#     st.session_state.logged_prompt = []
# if "feedback_key" not in st.session_state:
#     st.session_state.feedback_key = 0
# if "user_feedback" not in st.session_state:
#     st.session_state.user_feedback = []
# if "current_response" not in st.session_state:
#     st.session_state.current_response = []
# if "application" not in st.session_state:
#     st.session_state.application = []
# if "target_language" not in st.session_state:
#     st.session_state.target_language = []
# if "continue_to_chat" not in st.session_state:
#     st.session_state.continue_to_chat = False
# if "last_message" not in st.session_state:
#     st.session_state.last_message = None
# if "running_environment" not in st.session_state:
#     st.session_state.running_environment = get_running_environment()
# if "post_type" not in st.session_state:
#     st.session_state.post_type = "static"
# if "platform" not in st.session_state:
#     st.session_state.platform = None
# if "input_source" not in st.session_state:
#     st.session_state.input_source = None
# if "img_gen_feature" not in st.session_state:
#     st.session_state.img_gen_feature = False
# if "seed_idea" not in st.session_state:
#     st.session_state.seed_idea = None
# if "test_chat" not in st.session_state:
#     st.session_state.test_chat = False
# if "scraped_hashtag_videos" not in st.session_state:
#     st.session_state.scraped_hashtag_videos = False
# if "scraped_source_video" not in st.session_state:
#     st.session_state.scraped_source_video = False
# if "fail_to_download_tiktok_video" not in st.session_state:
#     st.session_state.fail_to_download_tiktok_video = False


# ===================== CHAT =====================
def chat_with_dummy_bot():
    pass


def chat_with_final_bot():
    pass


def auto_eval_flow():
    pass


def switch_fucntion(key):
    # clear some states depending on the set up later
    pass


def main():
    # Depending on the selected menu, show different sections
    menu_options = option_menu(
        menu_title=None,
        options=[
            "Draft bot",
            "Auto eval flow",
            "Final bot",
        ],
        icons=[
            "info-circle",
            "lightbulb-fill",
            "fire",
        ],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        on_change=switch_fucntion,
        key="menu",
    )
    match menu_options:
        case "Draft bot":
            st.title("📝 Draft bot")
            chat_with_dummy_bot()
        case "Auto eval flow":
            st.title("🔍 Auto eval flow")
            auto_eval_flow()
        case "Final bot":
            st.title("🚀 Final bot")
            chat_with_final_bot()


if __name__ == "__main__":
    main()
