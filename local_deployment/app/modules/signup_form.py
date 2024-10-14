import streamlit as st

from modules.users_manager import signup


def show_signup_form():
    with st.form(key="signup_form"):
        st.subheader("Création de compte")
        name = st.text_input("Nom")
        email = st.text_input("Email")
        password = st.text_input("Mot de passe", type="password")
        submit_button = st.form_submit_button("S'enregistrer")

        if submit_button:
            signup(name, email, password)
