import streamlit as st

from pages.users_manager import signup

def show_signup_form():
    with st.form(key="signup_form"):
        st.subheader("Register")
        name = st.text_input("Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Sign up")

        if submit_button:
            signup(name, email, password)