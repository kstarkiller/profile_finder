import streamlit as st
import requests
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class UserInput(BaseModel):
    message: str

@app.post("/question")
def process_question(user_input: UserInput):
    return {"user_input": user_input.message}

def display_accueil():

    st.title("Chatbot Interface")
    st.write("Interagissez avec le chatbot en utilisant l'interface ci-dessous.")

    # Champ de saisie pour l'utilisateur
    user_input = st.text_input("Vous : ", "")

    # Placeholder pour l'historique des conversations
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    # Si l'utilisateur saisit un message
    if user_input:
        # Envoyer l'input utilisateur à l'API
        response = requests.post("http://127.0.0.1:8000/question", json={"message": user_input})
        response_data = response.json()
        chatbot_response = response_data.get("user_input", "Erreur de réponse de l'API")

        # Ajouter la conversation à l'historique
        st.session_state['chat_history'].append(("Vous", user_input))
        st.session_state['chat_history'].append(("Chatbot", chatbot_response))

    # Afficher l'historique des conversations
    for sender, message in st.session_state['chat_history']:
        st.write(f"{sender} : {message}")
