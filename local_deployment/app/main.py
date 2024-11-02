import streamlit as st
import os
import platform
import requests
from datetime import datetime

st.set_page_config(initial_sidebar_state="expanded")

from styles import apply_custom_styles
from modules.chatbot import new_chat, existent_chat
from modules.connexion_manager import (
    login,
    logout,
    db_api_host,
    db_api_port,
)
from modules.signup_form import show_signup_form

apply_custom_styles()

# Détecter le système d'exploitation
is_windows = platform.system() == "Windows"
is_unix = platform.system() in ["Linux", "Darwin"]


# Vérifier si le code s'exécute dans un conteneur Docker
def is_docker():
    path = "/proc/self/cgroup"
    return (
        os.path.exists("/.dockerenv")
        or os.path.isfile(path)
        and any("docker" in line for line in open(path))
    )


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


def main():
    initialize_session_state()

    if (
        not st.session_state["show_signup_form"]
        and st.session_state["user_name"] is not None
        and st.session_state["settings"] is False
    ):
        st.title("PROFILE FINDER")
        # Display the user's name in the sidebar with a happy emoji
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
                    if st.button(
                        "Paramètres",
                        key="settings_button",
                        use_container_width=True,
                    ):
                        st.session_state.update(settings=True)
                        st.rerun()

        # Display a separation line
        st.sidebar.markdown(
            "<div style='border-bottom: 1px solid white; margin: 20px 0;'></div>",
            unsafe_allow_html=True,
        )

        # Model selection
        st.sidebar.markdown("## Modèles disponibles :")
        model_mapping = {
            ("[LOCAL] Llama 3.1 - Meta" if is_windows else "Llama 3 70b - Meta"): (
                "llama3.1:8b" if is_windows else "meta/meta-llama-3-70b-instruct"
            ),
            "Claude 3 Haiku - Anthropic": "claude-3-haiku-20240307",
            "Gemini 1.5 Flash - Google": "gemini-1.5-flash",
            "GPT 4o Mini - OpenAI": "gpt-4o-mini",
            "GPT o1 Mini - OpenAI": "o1-mini",
        }

        model = st.sidebar.selectbox(
            "Avec quel modèle souhaitez-vous interagir ?",
            options=[
                "[LOCAL] Llama 3.1 - Meta" if is_windows else "Llama 3 70b - Meta",
                "Claude 3 Haiku - Anthropic",
                "Command R - Cohere",
                "Gemini 1.5 Flash - Google",
                "GPT 4o Mini - OpenAI",
                "GPT o1 Mini - OpenAI",
            ],
            index=None,
            placeholder="Choisissez un modèle...",
            label_visibility="collapsed",
        )

        st.session_state.update(
            model=model_mapping.get(model, st.session_state["model"])
        )

        # Display a separation line
        st.sidebar.markdown(
            "<div style='border-bottom: 1px solid white;margin: 20px 0;'></div>",
            unsafe_allow_html=True,
        )
        st.sidebar.markdown("")
        st.sidebar.button(
            "Nouvelle recherche",
            on_click=lambda: st.session_state.update(
                chat_history=[], chat=[], chat_id="", duration=None
            ),
            use_container_width=True,
        )
        st.sidebar.markdown("### Historique de recherche :")
        if "search_history" in st.session_state:

            st.session_state["search_history"] = requests.get(
                f"http://{db_api_host}:{db_api_port}/get_search_history",
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
                    date = search["last_update_date"][:10]

                    date = datetime.strptime(date, "%Y-%m-%d").strftime("%d/%m")
                    with st.sidebar.container():
                        col1_search, col2_search = st.sidebar.columns([8, 1])
                        if isinstance(chat_title, str):
                            with col1_search:
                                # Chat button
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
                                        f"http://{db_api_host}:{db_api_port}/get_search_by_chat_id",
                                        params={"chat_id": str(search["chat_id"])},
                                    ).json()
                                    st.session_state.update(
                                        chat_history=search_data["chat_history"],
                                        chat_id=search_data["chat_id"],
                                        model=search_data["chat_history"][-1]["model"],
                                    )
                            with col2_search:
                                # Delete button
                                if st.button(
                                    "❌",
                                    key=f"delete_{search['chat_id']}",
                                    use_container_width=True,
                                ):
                                    requests.post(
                                        f"http://{db_api_host}:{db_api_port}/delete_search_from_history",
                                        json={"chat_id": str(search["chat_id"])},
                                    )
                                    st.session_state.update(chat_id="")
                                    st.rerun()
                        else:
                            st.sidebar.markdown(
                                "Aucun historique de chat valide trouvé."
                            )
            else:
                st.sidebar.markdown("Pas encore d'historique de recherche.")
        else:
            st.sidebar.markdown("Pas encore d'historique de recherche.")

        if st.session_state["chat_id"] == "":
            new_chat()
        elif st.session_state["chat_id"] != "":
            existent_chat()

    elif (
        not st.session_state["show_signup_form"]
        and st.session_state["user_name"] is not None
        and st.session_state["settings"] is True
    ):
        st.title("PARAMETRES")

        # Display the user's name in the sidebar with a happy emoji
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
                    if st.button(
                        "Chatbot",
                        key="settings_button",
                        use_container_width=True,
                    ):
                        st.session_state.update(settings=False)
                        st.rerun()
        # Display a separation line
        st.sidebar.markdown(
            "<div style='border-bottom: 1px solid white; margin: 20px 0;'></div>",
            unsafe_allow_html=True,
        )

# Display a separation line
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
                    requests.post(
                        f"http://{db_api_host}:{db_api_port}/delete_user_data",
                        json={"user_email": st.session_state["username"]},
                    )
                    st.container.write("Données effacées avec succès.")

        with st.container():
            col1, col2, col3 = st.columns(3, gap="small", vertical_alignment="center")
            with col1:
                st.write("###### Supprimer mon compte", use_container_width=True)
            with col2:
                st.write("............................................")
            with col3:
                if st.button("Supprimer", key="delete_account", use_container_width=True):
                    requests.post(
                        f"http://{db_api_host}:{db_api_port}/delete_user_account",
                        json={"user_email": st.session_state["username"]},
                    )
                    st.container.write("Compte supprimé avec succès.")

        # Display a separation line
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
        
        # Display a separation line
        st.markdown(
            "<div style='border-bottom: 1px solid white; margin: 3% 0 1% 0;'></div>",
            unsafe_allow_html=True,
        )

        st.write("## Documents pour le RAG")

        with st.container():
            col1, col2, col3 = st.columns(3, gap="small", vertical_alignment="center")
            with col1:
                st.write("###### Ajouter un document")
            with col2:
                st.selectbox("File",
                        options=["Coaff", "PSA RM", "Certs"],
                        index=None,
                        placeholder="Quel fichier envoyer ?",
                        label_visibility="collapsed"
                    )
            with col3:
                if st.button("Envoyer", key="send_doc", use_container_width=True):
                    pass


        
    elif (
        not st.session_state["show_signup_form"]
        and st.session_state["user_name"] is None
    ):
        st.title("PROFILE FINDER")
        with st.form("login_form"):
            st.subheader("Connexion")
            email = st.text_input("Email")
            password = st.text_input("Mot de passe", type="password")
            if st.form_submit_button("Se connecter"):
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
            "Nouveau sur Profile Finder ? Inscrivez-vous",
            on_click=lambda: st.session_state.update(show_signup_form=True),
        ):
            pass

    elif st.session_state["show_signup_form"] and st.session_state["user_name"] is None:
        show_signup_form()
        if st.button(
            "Vous avez déjà un compte ? Connectez-vous",
            key="login_button",
            on_click=lambda: st.session_state.update(
                show_signup_form=False, user_name=None
            ),
        ):
            pass

    if st.session_state["rerun"]:
        st.session_state["rerun"] = False
        st.rerun()


if __name__ == "__main__":
    main()
