import requests
import streamlit as st
from datetime import date

from modules.processing_request import process_input
from modules.response_generator import response_generator
from modules.users_manager import add_search_to_history, update_search_in_history

context = f"""You are a French chatbot assistant that helps the user find team members based on their location, availability and skills.
        - Format responses as concise and consistently as possible, using headers and tables when necessary. Don't explain what you're doing and summarize the data.
        - Use the current date ({date.today()}) for any time-related questions.
        - For months, consider the nearest future month unless otherwise specified. Don't consider months in the past or months more than 12 months in the futur, unless otherwise specified.
        - Combine occupancy periods and percentages to calculate total availability over a given period.
        - Don't assume anything, don't mess with the data, and only return members that meet the user's criteria.
        - If several members match the criteria, present them in order of relevance (availability, skills, etc.)."""


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


# This function is used to display the chatbot interface and process the user input.
def update_input():
    """
    Processes the user's input and updates the conversation history.

    Args:
        None

    Returns:
        None
    """
    user_input = st.session_state["temp_input"]

    # Add the question and answer to the history
    if user_input:
        if st.session_state["chat_id"] == "":
            # Generate a Conversation ID via the RAG API endpoint "/new_chat_id"
            try:
                url = "http://localhost:8080/new_chat_id"
                payload = {
                    "model": "gpt-4o-mini",
                    "prompt": user_input,
                }
                response = requests.post(url, json=payload)
                response.raise_for_status()  # Raise an error for bad status codes
                st.session_state["chat_id"] = response.json()["new_id"]

            except requests.exceptions.HTTPError as http_err:
                print(f"HTTP error occurred: {http_err}")
            except Exception as err:
                print(f"An error occurred: {err}")

    result = process_input(
        user_input, st.session_state["chat_history"], st.session_state["chat_id"]
    )
    if len(result) == 3:
        chatbot_response, updated_chat_history, duration = result
    else:
        chatbot_response, updated_chat_history = result
        duration = None
    st.session_state["chat_history"] = updated_chat_history
    st.session_state["chat"].append({"user": user_input, "assistant": chatbot_response})
    st.session_state["duration"] = duration

    if len(updated_chat_history) <= 2:
        add_search_to_history(
            st.session_state["chat_id"],
            st.session_state["chat_history"],
            st.session_state["username"],
        )
    else:
        update_search_in_history(
            st.session_state["chat_id"], st.session_state["chat_history"]
        )


def new_chat():
    """
    Displays the chatbot's welcome interface.

    This function initializes the session state for the conversation history if necessary,
    defines a function to update the user's input and add it to the history,
    and displays the conversation history in reverse order.

    - Initializes the 'chat_history' session state if it does not already exist.
    - Defines the `update_input` function to process the user's input and update the history.
    - Displays an input field for the user.
    - Displays the conversation history in reverse order, alternating between user and chatbot messages.

    Args:
        None

    Returns:
        None
    """
    # Initialize the session state if necessary
    initialize_session_state()

    # Input field for the user
    st.chat_input(
        placeholder="Ask your question here...",
        key="temp_input",
        on_submit=update_input,
    )

    # Display the welcome message if the history is empty
    if len(st.session_state["chat"]) == 0:
        with st.chat_message("Assistant"):
            st.write("How can I help you ?")

    # Display the conversation history
    else:
        for i in range(len(st.session_state["chat"])):
            bot_message = st.session_state["chat"][i]["assistant"]
            user_message = st.session_state["chat"][i]["user"]

            with st.chat_message("User"):
                st.write(f"Vous : {user_message}")
                # Add a unique identifier to the user message
                st.markdown(
                    f"<div id='message-{i}-user'></div>", unsafe_allow_html=True
                )

            with st.chat_message("Assistant"):
                # Check if i is the last message in the conversation
                if i == len(st.session_state["chat"]) - 1:
                    st.write_stream(response_generator(bot_message))
                    st.markdown(
                        f"<small style='color: gray;'>Réponse générée en {st.session_state['duration']} secondes</small>",
                        unsafe_allow_html=True,
                    )
                else:
                    st.write(bot_message)
                # Add a unique identifier to the assistant message
                st.markdown(
                    f"<div id='message-{i}-assistant'></div>", unsafe_allow_html=True
                )

        # JavaScript to automatically scroll to the latest message
        st.markdown(
            f"""
            <script>
            var latestMessage = document.getElementById('message-{len(st.session_state["chat"])-1}-user');
            if (latestMessage) {{
                latestMessage.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
            }}
            </script>
            """,
            unsafe_allow_html=True,
        )


def existent_chat():
    """
    Displays existant chat form the user's search history.

    This function displays the conversation history in reverse order.

    Args:
        None

    Returns:
        None
    """
    st.chat_input(
        placeholder="Continue conversation here...",
        key="history_temp_input",
        on_submit=update_input,
    )

    # Display the conversation history
    print(st.session_state["chat_history"])

    


# def display_chatbot():
#     """
#     Displays the chatbot interface according to the chat history.

#     This function checks if the chat ID is empty and displays the chatbot interface accordingly.

#     Args:
#         None

#     Returns:
#         None
#     """
#     if st.session_state["chat_id"] == "":
#         new_chat()
#     else:
#         existent_chat()


# if __name__ == "__main__":
#     display_chatbot()
