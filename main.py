import streamlit as st
from styles import apply_custom_styles
from pages import chatbot


def main():
    st.title("Profiles Finder")
    chatbot.display_accueil()
    apply_custom_styles()


if __name__ == "__main__":
    main()
