import os
import uuid
from datetime import datetime

# from openai import OpenAI
from openai import OpenAI
from streamlit_extras.app_logo import add_logo
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from authenticator.authenticate import get_authenticator
from config import get_running_environment

if "bot_version" not in st.session_state:
    st.session_state.bot_version = "dumb"
if "running_environment" not in st.session_state:
    st.session_state.running_environment = get_running_environment()

add_logo("http://placekitten.com/120/120")
st.title('Welcome to the chatbot auto eval tool 🤖🔍🚀')

with open('./config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = get_authenticator()

authenticator.login()

if st.session_state["authentication_status"]:
    st.markdown('You are logged in and now naviagte to eval dashboard to see your bot performance')
    with st.sidebar:
        authenticator.logout()
        st.write(f'Welcome *{st.session_state["name"]}*')
elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')

# # Set up OpenAI API
# sync_client = OpenAI(api_key=str(st.secrets["OPENAI_API_KEY"]))

# def get_running_environment():
#     # Check for ECS environment variables
#     if os.getenv("ECS_CONTAINER_METADATA_URI") or os.getenv("ECS_CLUSTER"):
#         return "ECS"
#     else:
#         return "LOCAL"

# # Initialise the context
# if "messages" not in st.session_state:
#     st.session_state.messages = []
# if "openai_model" not in st.session_state:
#     st.session_state.openai_model = "gpt-3.5-turbo"

# # ===================== CHAT =====================
# def chat_with_dummy_bot():
#     st.subheader("Chat", divider=True)
#     number_of_messages = len(st.session_state.messages)
#     # Display chat messages from history on app rerun
#     message_counter = 0
#     for message in st.session_state.messages:
#         if message_counter == 0:
#             with st.chat_message(message["role"]):
#                 st.markdown(st.session_state.original_prompt)
#         else:
#             with st.chat_message(message["role"]):
#                 st.markdown(message["content"])
#         message_counter += 1
#     # Accept user input
#     if prompt := st.chat_input("What is up?"):
#         # Modify Prompt
#         if number_of_messages == 0:
#             st.session_state.original_prompt = prompt
#         # Add user message to chat history
#         st.session_state.messages.append({"role": "user", "content": prompt})
#         # Display user message in chat message container
#         with st.chat_message("user"):
#             # Modify Prompt
#             if number_of_messages == 0:
#                 st.markdown(st.session_state.original_prompt)
#             else:
#                 st.markdown(prompt)
#         # Display assistant response in chat message container
#         with st.chat_message("assistant"):
#             message_placeholder = st.empty()
#             full_response = ""
#             print("MODEL:", st.session_state.openai_model)
#             for response in sync_client.chat.completions.create(
#                 model=st.session_state.openai_model,
#                 messages=[
#                     {"role": m["role"], "content": m["content"]}
#                     for m in st.session_state.messages
#                 ],
#                 stream=True,
#             ):
#                 full_response += response.choices[0].delta.content or ""
#                 message_placeholder.markdown(full_response + "▌")
#             message_placeholder.markdown(full_response)
#         st.session_state.last_message = full_response
#         st.session_state.messages.append(
#             {"role": "assistant", "content": full_response}
#         )
#         if len(st.session_state.messages) != 0:
#             st.session_state.current_response = st.session_state.messages
       
# def chat_with_final_bot():
#     st.subheader("Chat", divider=True)
#     number_of_messages = len(st.session_state.messages)
#     # Display chat messages from history on app rerun
#     message_counter = 0
#     for message in st.session_state.messages:
#         if message_counter == 0:
#             with st.chat_message(message["role"]):
#                 st.markdown(st.session_state.original_prompt)
#         else:
#             with st.chat_message(message["role"]):
#                 st.markdown(message["content"])
#         message_counter += 1
#     # Accept user input
#     if prompt := st.chat_input("What is up?"):
#         # Modify Prompt
#         if number_of_messages == 0:
#             st.session_state.original_prompt = prompt
#         # Add user message to chat history
#         st.session_state.messages.append({"role": "user", "content": prompt})
#         # Display user message in chat message container
#         with st.chat_message("user"):
#             # Modify Prompt
#             if number_of_messages == 0:
#                 st.markdown(st.session_state.original_prompt)
#             else:
#                 st.markdown(prompt)
#         # Display assistant response in chat message container
#         with st.chat_message("assistant"):
#             message_placeholder = st.empty()
#             full_response = ""
#             print("MODEL:", st.session_state.openai_model)
#             for response in sync_client.chat.completions.create(
#                 model=st.session_state.openai_model,
#                 messages=[
#                     {"role": m["role"], "content": m["content"]}
#                     for m in st.session_state.messages
#                 ],
#                 stream=True,
#             ):
#                 full_response += response.choices[0].delta.content or ""
#                 message_placeholder.markdown(full_response + "▌")
#             message_placeholder.markdown(full_response)
#         st.session_state.last_message = full_response
#         st.session_state.messages.append(
#             {"role": "assistant", "content": full_response}
#         )
#         if len(st.session_state.messages) != 0:
#             st.session_state.current_response = st.session_state.messages


# def auto_eval_flow():
#     pass


# def switch_fucntion(key):
#     # clear some states depending on the set up later
#     st.session_state.messages = []


# def main():
#     # Depending on the selected menu, show different sections
#     menu_options = option_menu(
#         menu_title=None,
#         options=[
#             "Auto eval flow",
#             "Draft bot",
#             "Final bot",
#         ],
#         icons=[
#             "info-circle",
#             "lightbulb-fill",
#             "fire",
#         ],
#         menu_icon="cast",
#         default_index=0,
#         orientation="horizontal",
#         on_change=switch_fucntion,
#         key="menu",
#     )
#     match menu_options:
#         case "Auto eval flow":
#             st.title("🔍 Auto eval flow")
#             auto_eval_flow()
#         case "Draft bot":
#             st.title("📝 Draft bot")
#             chat_with_dummy_bot()
#         case "Final bot":
#             st.title("🚀 Final bot")
#             chat_with_final_bot()


# if __name__ == "__main__":
#     main()
