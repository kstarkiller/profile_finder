from datetime import date
import streamlit as st

from processing_request import process_input

# Contexte du chatbot
starting_context = f"""
You are a french chatbot assistant that helps users to find members of a team based on their skills, names, experiences or availability.
When the availabilities of a member are not indicated, it means that the member is available except if he is on a mission.
Keep the answer as concise as possible, do not summarize the data and don't hesitate to use list or table to present datas.
Today is {date.today()} : use this information to provide a better answer.
If you don't know the answer, just say that you don't know, don't try to make up an answer.
"""


def display_accueil():
    # Initialiser l'état de session pour l'historique des conversations s'il n'existe pas déjà
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = [
            {"role": "system", "content": starting_context}
        ]
        st.session_state["chat"] = []
        st.session_state["query_context"] = []

    # Fonction pour mettre à jour l'entrée de l'utilisateur et ajouter à l'historique
    def update_input():
        user_input = st.session_state["temp_input"]
        # st.session_state["temp_input"] = ""

        # Ajouter la question et la réponse à l'historique
        if user_input:
            st.session_state["query_context"].append({"query": user_input})
            chatbot_response, updated_chat_history = process_input(
                st.session_state["query_context"], st.session_state["chat_history"]
            )
            st.session_state["chat_history"] = updated_chat_history
            st.session_state["chat"].append(
                {"user": user_input, "assistant": chatbot_response}
            )
            st.session_state["query_context"].append({"context": chatbot_response})

    # Champ de saisie pour l'utilisateur
    st.chat_input(
        placeholder="Posez votre question...", key="temp_input", on_submit=update_input
    )

    # Afficher l'historique avec des bulles de chat
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


if __name__ == "__main__":
    display_accueil()
