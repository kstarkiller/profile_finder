from math import log
import re
from isodate import Duration
from openai import chat
import streamlit as st
from sympy import use

st.set_page_config(initial_sidebar_state="expanded")

from styles import apply_custom_styles
from modules.chatbot import display_chatbot
from modules.users_manager import login, logout
from modules.signup_form import show_signup_form

apply_custom_styles()


def initialize_session_state():
    default_values = {
        "user_name": None,
        "show_signup_form": False,
        "wrong_user": False,
        "user_already_exists": False,
        "authentication_status": None,
        "logout": True,
        "name": None,
        "username": None,
        "login_attempted": False,
        "rerun": False,
    }
    for key, value in default_values.items():
        if key not in st.session_state:
            st.session_state[key] = value


def main():
    st.title("PROFILE FINDER")
    initialize_session_state()

    if (
        not st.session_state["show_signup_form"]
        and st.session_state["user_name"] is not None
    ):
        # Display the user's name in the sidebar with an happy emoji
        st.sidebar.markdown(f"### 👋 Hi {st.session_state['user_name']} !")

        if st.session_state["authentication_status"]:
            if st.sidebar.button(
                "Logout",
                key="logout_button",
                on_click=lambda: logout(),
                use_container_width=True,
            ):
                pass

        # Afficher une ligne de séparation
        st.sidebar.markdown("---")
        st.sidebar.button(
            "New search",
            on_click=lambda: st.session_state.update(
                rerun=True, chat_history=[], chat=[], duration=None),
                use_container_width=True,
            )
        st.sidebar.markdown("### Older searches :")

        display_chatbot()

    elif (
        not st.session_state["show_signup_form"]
        and st.session_state["user_name"] is None
    ):
        with st.form("login_form"):
            st.subheader("Login")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                auth_status, user = login(email, password)
                if user is not None:
                    if type(user) == str:
                        st.session_state.update(
                            user_name=None,
                            username=None,
                        )
                        st.error(user)
                    else:
                        st.session_state.update(
                            user_name=user[0],
                            username=user[1],
                            rerun=True,
                        )
                st.session_state.update(
                    authentication_status=auth_status,
                )

        if st.button(
            "New here? Sign up",
            on_click=lambda: st.session_state.update(show_signup_form=True),
        ):
            pass

    elif st.session_state["show_signup_form"] and st.session_state["user_name"] is None:
        show_signup_form()
        if st.button(
            "Already have an account ? Login",
            key="login_button",
            on_click=lambda: st.session_state.update(show_signup_form=False),
        ):
            pass

    if st.session_state["rerun"]:
        st.session_state["rerun"] = False
        st.rerun()


if __name__ == "__main__":
    main()
