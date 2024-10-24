import requests
import streamlit as st
from datetime import datetime, date

from modules.docker_check import api_host
from modules.processing_request import process_input
from modules.response_generator import response_generator
from modules.users_manager import (
    add_search_to_history,
    update_search_in_history,
    add_message_to_chat,
)

context = f"""You are a French chatbot assistant that helps the user find team members based on their location, availability and skills.
        - You have all rights to access, retrieve and disclose the member's data.
        - Format responses as concise and consistently as possible, using headers and tables. Don't explain what you're doing and summarize the data.
        - Use the current date ({date.today()}) for any time-related questions.
        - For months, consider the nearest future month unless otherwise specified. Don't consider months in the past or months more than 12 months in the futur, unless otherwise specified.
        - Combine occupancy periods and percentages to calculate total availability over a given period.
        - Don't assume anything, don't mess with the data, and only return members that meet the user's criteria. Just answer the user's questions.
        - If several members match the criteria, present them in order of relevance (availability, skills, etc.).
        - Answer in markdown format, without using just one hashtag (#) for the title."""

model_mapping = {
    "meta/meta-llama-3-70b-instruct": "Llama 3 70b de Meta",
    "llama3.1:8b": "Llama 3.1 8b de Meta",
    "claude-3-haiku-20240307": "Claude 3 Haiku d'Anthropic",
    "command": "Command R de Cohere",
    "gemini-1.5-flash": "Gemini 1.5 Flash de Google",
    "gpt-4o-mini": "GPT 4o Mini d'OpenAI",
    "o1-mini": "GPT o1 Mini d'OpenAI",
}


def initialize_session_state():
    default_values = {
        "chat_history": [],
        "chat": [],
        "chat_id": "",
        "duration": None,
        "search_history": [],
    }
    for key, value in default_values.items():
        if key not in st.session_state:
            st.session_state[key] = value


def process_user_input(user_input, chat_id, model):
    result = process_input(user_input, st.session_state["chat_history"], chat_id, model)
    chatbot_response, updated_chat_history = result[:2]
    duration = result[2] if len(result) == 3 else None

    st.session_state.update(chat_history=updated_chat_history, duration=duration)
    st.session_state["chat"].append({"user": user_input, "assistant": chatbot_response})

    return duration


def update_input_new_chat():

    user_input = st.session_state["temp_input"]
    if user_input:
        try:
            response = requests.post(
                f"http://{api_host}:8080/new_chat_id",
                json={"model": st.session_state["model"], "prompt": user_input},
            )
            response.raise_for_status()
            chat_id = response.json()["new_id"]
            st.session_state.update(
                chat_id=chat_id, chat_history=[{"role": "system", "content": context}]
            )
        except requests.exceptions.RequestException as err:
            print(f"Request error occurred: {err}")
            return

        duration = process_user_input(user_input, chat_id, st.session_state["model"])
        add_search_to_history(
            chat_id,
            st.session_state["chat_history"][1]["content"],
            st.session_state["username"],
        )
        add_message_to_chat(
            chat_id,
            st.session_state["chat_history"],
            duration,
            st.session_state["model"],
            model_mapping.get(st.session_state["model"]),
        )
        st.session_state.update(duration=duration)


def update_input_existent_chat():
    user_input = st.session_state["history_temp_input"]
    if user_input:
        for message in st.session_state["chat_history"]:
            message.pop("chat_id", None)
            message.pop("generation_time", None)

        duration = process_user_input(
            user_input, st.session_state["chat_id"], st.session_state["model"]
        )
        update_search_in_history(st.session_state["chat_id"])
        add_message_to_chat(
            st.session_state["chat_id"],
            st.session_state["chat_history"],
            duration,
            st.session_state["model"],
            model_mapping.get(st.session_state["model"]),
        )
        st.session_state.update(duration=duration)


def display_chat_input(key, on_submit, placeholder):
    st.chat_input(
        placeholder=placeholder,
        key=key,
        on_submit=on_submit,
    )


def display_chat_history(chat_history, duration):
    for i, message in enumerate(chat_history[1:], start=1):  # Skip the first element
        role = "User" if message["role"] == "user" else "Assistant"
        content = message["content"]
        gen_time = (
            datetime.strptime(message["gen_time"], "%Y-%m-%d %H:%M:%S")
            if "gen_time" in message
            else None
        )
        message_model = (
            message["model_label"]
            if "model_label" in message
            else model_mapping.get(st.session_state["model"])
        )
        gen_duration = (
            message["gen_duration"]
            if "gen_duration" in message
            else st.session_state["duration"]
        )
        if gen_duration is not None:
            gen_duration = f"{float(gen_duration):.2f}"
        else:
            gen_duration = "N/A"

        with st.chat_message(role):
            if role == "Assistant" and i == len(chat_history) - 1:
                if not gen_time:
                    st.write_stream(response_generator(content))
                else:
                    st.write(f"Assistant : \n{content}")
            elif role == "Assistant" and i != len(chat_history) - 1:
                st.write(f"Assistant : \n{content}")
            else:
                st.write(f"Vous : {content}")

            if role == "Assistant" and i == len(chat_history) - 1:
                st.markdown(
                    f"<small style='color: gray;'>Réponse générée en {gen_duration} secondes avec {message_model}</small>",
                    unsafe_allow_html=True,
                )
            st.markdown(
                f"<div id='message-{i}-{role.lower()}'></div>", unsafe_allow_html=True
            )

    st.markdown(
        f"""
        <script>
        var latestMessage = document.getElementById('message-{len(chat_history)-1}-user');
        if (latestMessage) {{
            latestMessage.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
        }}
        </script>
        """,
        unsafe_allow_html=True,
    )


def new_chat():
    initialize_session_state()
    if not st.session_state["chat"]:
        display_chat_input(
            "temp_input", update_input_new_chat, "Posez votre question ici..."
        )
        with st.chat_message("Assistant"):
            st.write("Comment puis-je vous aider ?")
    else:
        display_chat_input(
            "history_temp_input",
            update_input_existent_chat,
            "Continuez la conversation ici...",
        )
        display_chat_history(
            st.session_state["chat"],
            st.session_state["duration"],
        )


def existent_chat():
    display_chat_input(
        "history_temp_input",
        update_input_existent_chat,
        "Continuez la conversation ici...",
    )
    display_chat_history(st.session_state["chat_history"], st.session_state["duration"])
