import streamlit as st 
from styles import apply_custom_styles
from pages import chatbot


def main():
    st.title("Profiles Finder")
    try:
        chatbot.display_accueil()
        apply_custom_styles()
    except Exception as e:
        st.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
