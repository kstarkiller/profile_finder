import streamlit as st
from datetime import date

from processing_request import process_input
from response_generator import response_generator

context = f"""
        You are a French chatbot assistant that helps the user find team members based on their location, availability and skills.
        - Format responses as concise and consistently as possible, using headers and tables when necessary. Don't explain what you're doing and summarize the data.
        - Use the current date ({date.today()}) for any time-related questions.
        - For months, consider the nearest future month unless otherwise specified. Don't consider months in the past or months more than 12 months in the futur, unless otherwise specified.
        - Combine occupancy periods and percentages to calculate total availability over a given period.
        - Don't assume anything, don't mess with the data, and only return members that meet the user's criteria.
        - If several members match the criteria, present them in order of relevance (availability, skills, etc.).
        """


# Fonction pour mettre à jour l'entrée de l'utilisateur et ajouter à l'historique
def update_input():
    """
    Traite l'entrée de l'utilisateur et met à jour l'historique des conversations.

    Args:
        None

    Returns:
        None
    """
    user_input = st.session_state["temp_input"]

    # Ajouter la question et la réponse à l'historique
    if user_input:
        chatbot_response, updated_chat_history = process_input(
            user_input, st.session_state["chat_history"]
        )
        st.session_state["chat_history"] = updated_chat_history
        st.session_state["chat"].append(
            {"user": user_input, "assistant": chatbot_response}
        )


def display_accueil():
    """
    Affiche l'interface d'accueil du chatbot.

    Cette fonction initialise l'état de session pour l'historique des conversations si nécessaire,
    définit une fonction pour mettre à jour l'entrée de l'utilisateur et l'ajouter à l'historique,
    et affiche l'historique des conversations dans l'ordre inverse.

    - Initialise l'état de session 'chat_history' s'il n'existe pas déjà.
    - Définit la fonction `update_input` pour traiter l'entrée de l'utilisateur et mettre à jour l'historique.
    - Affiche un champ de saisie pour l'utilisateur.
    - Affiche l'historique des conversations en ordre inverse, en alternant les messages de l'utilisateur et du chatbot.

    Args:
        None

    Returns:
        None
    """

    # Initialiser l'état de session pour l'historique des conversations s'il n'existe pas déjà
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
        st.session_state["chat_history"].append({"role": "system", "content": context})
        st.session_state["chat"] = []

    # Champ de saisie pour l'utilisateur
    st.chat_input(
        placeholder="Posez votre question...", key="temp_input", on_submit=update_input
    )

    # Afficher le message d'accueil si l'historique est vide
    if len(st.session_state["chat"]) == 0:
        with st.chat_message("Assistant"):
            st.write("Bonjour, comment puis-je vous aider ?")

    # Afficher l'historique des conversations
    else:
        for i in range(len(st.session_state["chat"])):
            bot_message = st.session_state["chat"][i]["assistant"]
            user_message = st.session_state["chat"][i]["user"]

            with st.chat_message("User"):
                st.write(f"Vous : {user_message}")
                # Ajouter un identifiant unique au message de l'utilisateur
                st.markdown(
                    f"<div id='message-{i}-user'></div>", unsafe_allow_html=True
                )

            with st.chat_message("Assistant"):
                st.write_stream(response_generator(bot_message))
                # Ajouter un identifiant unique au message de l'assistant
                st.markdown(
                    f"<div id='message-{i}-assistant'></div>", unsafe_allow_html=True
                )

        # Ajouter un script JavaScript pour faire défiler jusqu'au début du message le plus récent
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
    display_accueil()
