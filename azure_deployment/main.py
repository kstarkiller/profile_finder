import os
# from tkinter.font import names
import streamlit as st
import streamlit_authenticator as stauth
from styles import apply_custom_styles
from pages.chatbot import display_accueil

# Set page configuration
st.set_page_config(layout="wide")
apply_custom_styles()

def main():
    names = ["Kevin"]
    usernames = [os.getenv("RAG_LOCAL_USERNAME")]
    passwords = [os.getenv("RAG_LOCAL_PASSWORD")]
    hashed_passwords = stauth.Hasher(passwords).generate()

    # Create credentials dictionary
    credentials = {
        "usernames": {
            usernames[i]: {"name": names[i], "password": hashed_passwords[i]}
            for i in range(len(usernames))
        }
    }

    # Create an authenticator object
    authenticator = stauth.Authenticate(
        credentials, "some_cookie_name", "some_signature_key", cookie_expiry_days=10
    )

    st.title("PROFILE FINDER")
    # Render login widget
    name, authentication_status, username = authenticator.login(
        "main", None, 3, None, False, False, "Login"
    )

    if authentication_status:
        st.sidebar.write(f"Bienvenue *{name}*")
        authenticator.logout("Logout", "sidebar")

        display_accueil()

    elif authentication_status == False:
        st.error("Username/password is incorrect")
    elif authentication_status == None:
        st.warning("Please enter your username and password")


if __name__ == "__main__":
    main()

