import streamlit as st
from datetime import date

from modules.processing_request import process_input
from modules.response_generator import response_generator

context = f"""
        You are a French chatbot assistant that helps the user find team members based on their location, availability and skills.
        - Format responses as concise and consistently as possible, using headers and tables when necessary. Don't explain what you're doing and summarize the data.
        - Use the current date ({date.today()}) for any time-related questions.
        - For months, consider the nearest future month unless otherwise specified. Don't consider months in the past or months more than 12 months in the futur, unless otherwise specified.
        - Combine occupancy periods and percentages to calculate total availability over a given period.
        - Don't assume anything, don't mess with the data, and only return members that meet the user's criteria.
        - If several members match the criteria, present them in order of relevance (availability, skills, etc.).
        """


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
        result = process_input(user_input, st.session_state["chat_history"])
        if len(result) == 3:
            chatbot_response, updated_chat_history, duration = result
        else:
            chatbot_response, updated_chat_history = result
            duration = None  # or any default value you prefer
        st.session_state["chat_history"] = updated_chat_history
        st.session_state["chat"].append(
            {"user": user_input, "assistant": chatbot_response}
        )
        st.session_state["duration"] = duration


def display_chatbot():
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

    # Init the session state for the conversation history if it doesn't already exist
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
        st.session_state["chat_history"].append({"role": "system", "content": context})
        st.session_state["chat"] = []
    if "duration" not in st.session_state:
        st.session_state["duration"] = None

    # Input field for the user
    st.chat_input(
        placeholder="Ask your question here...", key="temp_input", on_submit=update_input
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
                    st.write(f"Durée de la réponse : {st.session_state['duration']} secondes")
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


if __name__ == "__main__":
    display_chatbot()
