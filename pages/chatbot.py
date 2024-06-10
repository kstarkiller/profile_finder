import streamlit as st
from processing import process_input

def display_accueil():

    # Initialiser l'état de session pour l'historique des conversations s'il n'existe pas déjà
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    # Fonction pour mettre à jour l'entrée de l'utilisateur et ajouter à l'historique
    def update_input():
        user_input = st.session_state['temp_input']
        st.session_state['temp_input'] = ""

        # Ajouter la question et la réponse à l'historique
        if user_input:
            chatbot_response, updated_chat_history = process_input(user_input, st.session_state['chat_history'])
            st.session_state['chat_history'] = updated_chat_history

            # Utiliser chatbot_response ici
            st.write(f"Chatbot : {chatbot_response}")

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
