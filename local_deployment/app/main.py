import os
import streamlit as st
import streamlit_authenticator as stauth
import bcrypt

# Set page configuration
st.set_page_config(layout="wide")

from styles import apply_custom_styles
from pages.chatbot import display_chatbot
from pages.users_manager import create_user

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
    
    # État initial : le formulaire d'inscription est caché
    if 'show_signup_form' not in st.session_state:
        st.session_state['show_signup_form'] = False

    if st.session_state['show_signup_form']:
        # Render signup widget
        with st.form(key="signup_form", clear_on_submit=True, border=True):
            st.subheader("Inscription")
            name = st.text_input("Nom")
            email = st.text_input("Email")
            password = st.text_input("Mot de passe", type="password")

            submitted = st.form_submit_button("Register")
  
        if submitted:
            # Hasher le mot de passe ici avant de l'enregistrer
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            create_user(name, email, hashed_password)
            st.success("Utilisateur créé avec succès !")
            # Revenir au login après l'inscription après 3 secondes
            st.session_state.update(show_signup_form=False)
            
        if st.button("Already have an account? Log In",
                     on_click=lambda: st.session_state.update(show_signup_form=False)):
                pass
    else:
        # Render login widget
        name, authentication_status, username = authenticator.login(
            "main", None, 3, None, False, False, "Login"
        )

        if authentication_status:
            st.sidebar.write(f"Welcome *{name}*")
            authenticator.logout("Logout", "sidebar")

            display_chatbot()

        elif authentication_status == False:
            st.error("Username/password is incorrect")

            if st.button("New here? Sign up",
                         on_click=lambda: st.session_state.update(show_signup_form=True)):
                pass

        elif authentication_status == None:
            if st.button("New here? Sign up",
                         on_click=lambda: st.session_state.update(show_signup_form=True)):
                pass

if __name__ == "__main__":
    main()