import streamlit as st
import random
import os
import platform
import requests
import time
from datetime import datetime

st.set_page_config(initial_sidebar_state="expanded")

from styles import apply_custom_styles
from modules.chatbot import new_chat, existent_chat, get_token
from modules.connexion_manager import login, logout
from modules.signup_form import show_signup_form
from modules.docker_check import is_running_in_docker

venv = is_running_in_docker()

apply_custom_styles()

# Détecter le système d'exploitation
is_windows = platform.system() == "Windows"
is_unix = platform.system() in ["Linux", "Darwin"]


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
        "search_history": [],
        "chat_history": [],
        "chat": [],
        "chat_id": "",
        "themebutton": "light",
        "theme": "light",
        "model": None,
        "settings": False,
    }
    for key, value in default_values.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_sidebar():
    st.sidebar.markdown(f"# 👋 Bonjour {st.session_state['user_name']} ! ")
    if st.session_state["authentication_status"]:
        with st.sidebar.container():
            col1, col2 = st.sidebar.columns(2)
            with col1:
                if st.button(
                    "Déconnexion",
                    key="logout_button",
                    on_click=lambda: logout(),
                    use_container_width=True,
                ):
                    pass
            with col2:
                button_label = (
                    "Paramètres" if not st.session_state["settings"] else "Chatbot"
                )
                if st.button(
                    button_label, key="toggle_button", use_container_width=True
                ):
                    st.session_state["settings"] = not st.session_state["settings"]
                    st.rerun()
    st.sidebar.markdown(
        "<div style='border-bottom: 1px solid white; margin: 20px 0;'></div>",
        unsafe_allow_html=True,
    )


def render_model_selection():
    model_mapping = {
        "[LOCAL] Llama 3.1 - Meta": "llama3.1:8b",
        "Llama 3 70b - Meta": "meta/meta-llama-3-70b-instruct",
        "Claude 3 Haiku - Anthropic": "claude-3-haiku-20240307",
        "Gemini 1.5 Flash - Google": "gemini-1.5-flash",
        "GPT 4o Mini - OpenAI": "gpt-4o-mini",
        "GPT o1 Mini - OpenAI": "o1-mini",
    }
    model = st.sidebar.selectbox(
        "Avec quel modèle souhaitez-vous interagir ?",
        options=[
            "[LOCAL] Llama 3.1 - Meta",
            "Llama 3 70b - Meta",
            "Claude 3 Haiku - Anthropic",
            "Gemini 1.5 Flash - Google",
            "GPT 4o Mini - OpenAI",
            "GPT o1 Mini - OpenAI",
        ],
        index=None,
        placeholder="Choisissez un modèle...",
        label_visibility="collapsed",
    )
    st.session_state.update(model=model_mapping.get(model, st.session_state["model"]))
    st.sidebar.markdown(
        "<div style='border-bottom: 1px solid white;margin: 20px 0;'></div>",
        unsafe_allow_html=True,
    )


def render_search_history():
    st.sidebar.markdown("### Historique de recherche :")
    if "search_history" in st.session_state:
        st.session_state["search_history"] = requests.get(
            f"http://{venv['db_host']}:{venv['db_port']}/searches",
            params={"user_email": st.session_state["username"]},
        ).json()
        displayed_chat_ids = set()
        if len(st.session_state["search_history"]) > 0:
            for search in st.session_state["search_history"]:
                chat_id = search["chat_id"]
                if chat_id in displayed_chat_ids:
                    continue
                displayed_chat_ids.add(chat_id)
                chat_title = search["chat_title"]
                date = datetime.strptime(
                    search["last_update_date"][:10], "%Y-%m-%d"
                ).strftime("%d/%m")
                with st.sidebar.container():
                    col1_search, col2_search = st.sidebar.columns([8, 1])
                    if isinstance(chat_title, str):
                        with col1_search:
                            if st.button(
                                label=(
                                    f"{date} - {chat_title[:20]}..."
                                    if len(chat_title) >= 15
                                    else f"{date} - {chat_title}"
                                    + "\u00A0\u00A0" * (25 - len(chat_title))
                                ),
                                key=f"{search['chat_id']}",
                                use_container_width=True,
                            ):
                                search_data = requests.get(
                                    f"http://{venv['db_host']}:{venv['db_port']}/search",
                                    params={"chat_id": str(search["chat_id"])},
                                ).json()
                                st.session_state.update(
                                    chat_history=search_data["chat_history"],
                                    chat_id=search_data["chat_id"],
                                    model=search_data["chat_history"][-1]["model"],
                                )
                        with col2_search:
                            if st.button(
                                "❌",
                                key=f"delete_{search['chat_id']}",
                                use_container_width=True,
                            ):
                                requests.delete(
                                    f"http://{venv['db_host']}:{venv['db_port']}/search",
                                    json={"chat_id": str(search["chat_id"])},
                                )
                                st.session_state.update(chat_id="",
                                                        chat=[],
                                                        chat_history=[])
                                st.rerun()
                    else:
                        st.sidebar.markdown("Aucun historique de chat valide trouvé.")
        else:
            st.sidebar.markdown("Pas encore d'historique de recherche.")
    else:
        st.sidebar.markdown("Pas encore d'historique de recherche.")


def render_main_content():
    if st.session_state["chat_id"] == "":
        new_chat()
    elif st.session_state["chat_id"] != "":
        existent_chat()


def render_settings():
    st.title("PARAMETRES")
    render_sidebar()
    st.markdown(
        "<div style='border-bottom: 1px solid white; margin: 3% 0 1% 0;'></div>",
        unsafe_allow_html=True,
    )
    st.write("## Paramètres du compte")
    with st.container():
        col1, col2, col3 = st.columns(3, gap="small", vertical_alignment="center")
        with col1:
            st.write("###### Effacer mes données")
        with col2:
            st.write("............................................")
        with col3:
            if st.button("Effacer", key="delete_data", use_container_width=True):
                print(st.session_state["username"])
                requests.delete(
                    f"http://{venv['db_host']}:{venv['db_port']}/searches",
                    json={"email": st.session_state["username"]},
                )
                st.markdown(
                    "<span style='color: green;'>Données effacées avec succès.</span>",
                    unsafe_allow_html=True,
                )
                st.session_state.update(search_history=[], chat_id="", chat=[])
                time.sleep(2.0)
                st.rerun()
    with st.container():
        col1, col2, col3 = st.columns(3, gap="small", vertical_alignment="center")
        with col1:
            st.write("###### Supprimer mon compte")
        with col2:
            st.write("............................................")
        with col3:
            with st.popover("Supprimer", use_container_width=True):
                st.markdown(
                    "<span style='color: red;'>Attention, cette action est irréversible.</span>",
                    unsafe_allow_html=True,
                )
                st.write(
                    "Veuillez confirmer votre mot de passe pour supprimer votre compte."
                )
                password = st.text_input(
                    "Mot de passe", type="password", key="delete_password"
                )
                col_confirm, col_cancel = st.columns(2)
                with col_confirm:
                    if st.button(
                        "Confirmer",
                        key="confirm_delete_button",
                        use_container_width=True,
                    ):
                        response = requests.delete(
                            f"http://{venv['db_host']}:{venv['db_port']}/user",
                            json={
                                "email": st.session_state["username"],
                                "password": password,
                            },
                        )
                        if response.text == '"Invalid password"':
                            st.error(f"Erreur : Le mot de passe est incorrect.")
                        elif response.text == '"User not found"':
                            st.error(
                                f"Une erreur s'est produite, reconnectez-vous et réessayez."
                            )
                        else:
                            st.toast("Compte supprimé avec succès")
                            time.sleep(2.0)
                            st.session_state.update(
                                user_name=None,
                                username=None,
                                authentication_status=False,
                            )
                            st.rerun()
                with col_cancel:
                    if st.button(
                        "Annuler", key="cancel_delete_button", use_container_width=True
                    ):
                        st.session_state["confirm_delete"] = False
                        st.rerun()
    st.markdown(
        "<div style='border-bottom: 1px solid white; margin: 3% 0 1% 0;'></div>",
        unsafe_allow_html=True,
    )
    st.write("## Paramètres de l'application")
    with st.container():
        col1, col2, col3 = st.columns(3, gap="small", vertical_alignment="center")
        with col1:
            st.write("###### Changer de thème")
        with col2:
            st.write("............................................")
        with col3:
            column1, column2 = st.columns(2, gap="small", vertical_alignment="center")
            with column1:
                if st.button("Clair", key="light_theme", use_container_width=True):
                    st.session_state.update(theme="light")
            with column2:
                if st.button("Sombre", key="dark_theme", use_container_width=True):
                    st.session_state.update(theme="dark")
    st.markdown(
        "<div style='border-bottom: 1px solid white; margin: 3% 0 1% 0;'></div>",
        unsafe_allow_html=True,
    )
    st.write("## Documents pour le RAG")
    with st.container():
        st.write("###### Ajouter un document")
        file = st.file_uploader(
            "Ajouter un document",
            type=["xlsx"],
            key="file_uploader",
            label_visibility="collapsed",
        )
        col1, col2, col3 = st.columns(3, gap="small", vertical_alignment="center")
        with col3:
            if st.button(
                "Envoyer",
                key="send_doc",
                use_container_width=True,
            ):
                messages = [
                    "Envoi du document...",
                    "Traitement en cours...",
                    "Veuillez patienter...",
                    "Presque terminé...",
                ]
                with st.spinner("Envoi du document..."):
                    for _ in range(4):
                        time.sleep(4)
                        st.spinner(random.choice(messages))
                    result = requests.post(
                        f"http://{venv['rag_host']}:{venv['rag_port']}/file",
                        files={"file": file},
                        headers={
                            "Authorization": f"Bearer {get_token()}",
                        },
                    )

                st.success("Terminé !")


def render_login():
    st.title("PROFILE FINDER")
    with st.form("login_form"):
        st.subheader("Connexion")
        email = st.text_input("Email")
        password = st.text_input("Mot de passe", type="password")
        if st.form_submit_button("Se connecter"):
            auth_status, user = login(email, password)
            if user is not None:
                if type(user) == str:
                    st.session_state.update(user_name=None, username=None)
                    st.error(user)
                else:
                    st.session_state.update(
                        user_name=user[0], username=user[1], rerun=True
                    )
            st.session_state.update(authentication_status=auth_status)
    if st.button(
        "Nouveau sur Profile Finder ? Inscrivez-vous",
        on_click=lambda: st.session_state.update(show_signup_form=True),
    ):
        pass


def render_signup():
    show_signup_form()
    if st.button(
        "Vous avez déjà un compte ? Connectez-vous",
        key="login_button",
        on_click=lambda: st.session_state.update(
            show_signup_form=False, user_name=None
        ),
    ):
        pass


def main():
    initialize_session_state()
    if (
        not st.session_state["show_signup_form"]
        and st.session_state["user_name"] is not None
    ):
        if st.session_state["settings"]:
            render_settings()
        else:
            st.title("PROFILE FINDER")
            render_sidebar()
            render_model_selection()
            st.sidebar.button(
                "Nouvelle recherche",
                on_click=lambda: st.session_state.update(
                    chat_history=[], chat=[], chat_id="", duration=None
                ),
                use_container_width=True,
            )
            render_search_history()
            render_main_content()
    elif (
        not st.session_state["show_signup_form"]
        and st.session_state["user_name"] is None
    ):
        render_login()
    elif st.session_state["show_signup_form"] and st.session_state["user_name"] is None:
        render_signup()
    if st.session_state["rerun"]:
        st.session_state["rerun"] = False
        st.rerun()


if __name__ == "__main__":
    main()
