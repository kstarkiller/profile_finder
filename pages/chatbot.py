import streamlit as st
from processing import process_input

def display_accueil():
    st.title("Chatbot Interface")
    st.write("Interagissez avec le chatbot en utilisant l'interface ci-dessous.")

    # Champ de saisie pour l'utilisateur
    user_input = st.text_input("Vous : ", "")

    # Si l'utilisateur saisit un message
    if user_input:
        chatbot_response = process_input(user_input)

        # Afficher la réponse du chatbot
        st.write(f"Chatbot : {chatbot_response}")

if __name__ == "__main__":
    display_accueil()