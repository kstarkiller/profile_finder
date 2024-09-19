import streamlit as st
from processing import process_input

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
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    # Fonction pour mettre à jour l'entrée de l'utilisateur et ajouter à l'historique
    def update_input():
        """
        Traite l'entrée de l'utilisateur et met à jour l'historique des conversations.

        Args:
            None

        Returns:
            None
        """
        user_input = st.session_state['temp_input']
        st.session_state['temp_input'] = ""

        # Ajouter la question et la réponse à l'historique
        if user_input:
            chatbot_response, updated_chat_history = process_input(user_input, st.session_state['chat_history'])
            st.session_state['chat_history'] = updated_chat_history
            print(f"Chatbot response: {chatbot_response}")

    # Champ de saisie pour l'utilisateur
    st.text_input("Vous : ", key='temp_input', on_change=update_input)

    # Afficher l'historique des conversations en ordre inverse
    for i in range(len(st.session_state['chat_history']) - 1, -1, -2):
        bot_message = st.session_state['chat_history'][i]
        user_message = st.session_state['chat_history'][i - 1]

        # Afficher le message de l'utilisateur
        st.write(f"Vous : {user_message['content']}")
        
        # Afficher la réponse du chatbot
        st.write(f"Chatbot : {bot_message['content']}")

if __name__ == "__main__":
    display_accueil()
