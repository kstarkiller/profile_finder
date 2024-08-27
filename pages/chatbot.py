from datetime import date
import streamlit as st

from processing_request import process_input
from ImproveModelPrecision import process_query  # Import de la fonction process_query

# Contexte du chatbot
starting_context = f"""
Today it's {date.today()} and you're a French chatbot assistant that helps users find team members based on the data provided.
Keep the answer concise and don't hesitate to use a table to present the data.
If you don't know the answer, just say you don't know, don't try to make up an answer.
"""

def display_accueil():
    try:
        if "chat_history" not in st.session_state:
            st.session_state["chat_history"] = [
                {"role": "system", "content": starting_context}
            ]
            st.session_state["chat"] = []
            st.session_state["query_context"] = []

        def update_input():
            user_input = st.session_state["temp_input"]

            if user_input:
                query_context = process_query(user_input)  # Appel de process_query
                st.session_state["query_context"].append({"query": user_input, "context": query_context})
                chatbot_response, updated_chat_history = process_input(
                    st.session_state["query_context"], st.session_state["chat_history"]
                )

                st.session_state["chat_history"] = updated_chat_history
                st.session_state["chat"].append(
                    {"user": user_input, "assistant": chatbot_response}
                )
                st.session_state["query_context"].append({"context": chatbot_response})

        st.chat_input(
            placeholder="Posez votre question...", key="temp_input", on_submit=update_input
        )

        if len(st.session_state["chat"]) == 0:
            with st.chat_message("Assistant"):
                st.write("Bonjour, comment puis-je vous aider ?")
        else:
            for i in range(len(st.session_state["chat"])):
                bot_message = st.session_state["chat"][i]["assistant"]
                user_message = st.session_state["chat"][i]["user"]

                with st.chat_message("User"):
                    st.write(f"Vous : {user_message}")

                with st.chat_message("Assistant"):
                    st.write(f"Assistant : {bot_message}")

    except Exception as e:
        st.error(f"An error occurred in display_accueil: {e}")

if __name__ == "__main__":
    display_accueil()
