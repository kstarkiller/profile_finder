import streamlit as st

st.set_page_config(initial_sidebar_state="expanded")

from styles import apply_custom_styles
from pages.chatbot import display_chatbot
from pages.users_manager import login, logout, authenticator
from pages.signup_form import show_signup_form

apply_custom_styles()

def initialize_session_state():
    default_values = {
        "user_name": None,
        "show_signup_form": False,
        "wrong_user": False,
        "user_already_exists": False,
        "authentication_status": None,
        "logout": True,
        "name": "start",
        "username": "start",
        "login_attempted": False,
    }
    for key, value in default_values.items():
        if key not in st.session_state:
            st.session_state[key] = value

def main():
    st.title("PROFILE FINDER")
    initialize_session_state()

    if not st.session_state["show_signup_form"] and st.session_state["user_name"] is None:
        login()
    elif st.session_state["show_signup_form"] and st.session_state["user_name"] is None:
        show_signup_form()
        if st.button(
            "Already have an account ? Login",
            key="login_button",
            on_click=lambda: st.session_state.update(show_signup_form=False),
            ):
            pass
    elif not st.session_state["show_signup_form"] and st.session_state["user_name"] is not None:
        st.sidebar.write(f"Welcome {st.session_state['user_name']} !")
        if st.session_state["authentication_status"] :
            logout()
        display_chatbot()

if __name__ == "__main__":
    main()
