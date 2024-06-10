import streamlit as st
from processing import process_input

def display_accueil():
    st.title("Chatbot Interface")
    st.write("Interagissez avec le chatbot en utilisant l'interface ci-dessous.")

    # Initialiser l'état de session pour l'historique des conversations s'il n'existe pas déjà
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    # Initialiser le compteur pour les réponses du chatbot s'il n'existe pas déjà
    if 'response_counter' not in st.session_state:
        st.session_state['response_counter'] = 1

    # Fonction pour mettre à jour l'entrée de l'utilisateur et ajouter à l'historique
    def update_input():
        user_input = st.session_state['temp_input']
        st.session_state['temp_input'] = ""

        # Ajouter la question et la réponse à l'historique
        if user_input:
            chatbot_response = process_input(user_input, st.session_state['response_counter'])
            st.session_state['chat_history'].append({"role": "user", "content": user_input})
            st.session_state['chat_history'].append({"role": "bot", "content": chatbot_response})

            # Incrémenter le compteur de réponse
            st.session_state['response_counter'] += 1

            # Conserver uniquement les cinq dernières paires (utilisateur-chatbot)
            if len(st.session_state['chat_history']) > 10:
                st.session_state['chat_history'] = st.session_state['chat_history'][-10:]

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
