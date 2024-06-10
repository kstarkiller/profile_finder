import streamlit as st
from processing import process_input

def display_accueil():
    st.title("Chatbot Interface")
    st.write("Interagissez avec le chatbot en utilisant l'interface ci-dessous.")

    # Initialiser l'état de session pour user_input s'il n'existe pas déjà
    if 'user_input' not in st.session_state:
        st.session_state['user_input'] = ""

    # Fonction pour mettre à jour l'entrée de l'utilisateur
    def update_input():
        st.session_state['user_input'] = st.session_state['temp_input']
        st.session_state['temp_input'] = ""

    # Champ de saisie pour l'utilisateur
    st.text_input("Vous : ", key='temp_input', on_change=update_input)

    # Si l'utilisateur saisit un message
    if st.session_state['user_input']:
        chatbot_response = process_input(st.session_state['user_input'])

        # Afficher la réponse du chatbot
        st.write(f"Chatbot : {chatbot_response}")

        # Réinitialiser l'entrée de l'utilisateur
        st.session_state['user_input'] = ""

if __name__ == "__main__":
    display_accueil()
