import os
import streamlit as st
import streamlit_authenticator as stauth
from styles import apply_custom_styles
from pages import chatbot

def main():
    
    st.title("Avv Matcher")
    chatbot.display_accueil()
    apply_custom_styles()

if __name__ == "__main__":
    main()
