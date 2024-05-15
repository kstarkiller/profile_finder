import streamlit as st
from styles import apply_custom_styles
# from pages import accueil, chatbot

def main():
    apply_custom_styles()
    if 'page' not in st.session_state:
        st.session_state['page'] = 'Accueil'

    st.sidebar.title("AVV Matcher")
    st.sidebar.radio("Choisir une page :", ["Accueil", "Chatbot"], key='page')

    if st.session_state.page == 'Accueil':
        accueil()
    elif st.session_state.page == 'Chatbot':
        chatbot()

def accueil():
    st.title("Page d'Accueil")
    st.write("Bienvenue sur la page d'accueil.")

def chatbot():
    st.title("ChatBot")
    st.write("Interface du chatbot à développer.")

if __name__ == "__main__":
    main()