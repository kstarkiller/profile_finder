import streamlit as st
import requests

from modules.docker_check import is_running_in_docker

venv = is_running_in_docker()


# Fonction pour s'enregistrer
def signup(name, email, password):
    """
    Permet à un utilisateur de s'inscrire à l'application.

    Args:
        name (str): Nom de l'utilisateur
        email (str): Email de l'utilisateur
        password (str): Mot de passe de l'utilisateur

    Returns:
        None
    """

    # Vérifier si le nom, l'email et le mot de passe sont fournis
    if name and email and password:
        user_check = requests.put(
            f"http://{venv['db_host']}:{venv['db_port']}/user",
            json={"name": name, "email": email, "password": password},
        ).json()

        if (
            type(user_check) == list
            and user_check[1] == email
            and user_check[0] == name
        ):
            st.session_state.update(
                user_name=user_check[0],
                username=user_check[1],
                user_already_exists=False,
            )
            st.success(f"Merci {user_check[0]}, vous êtes maintenant inscrit.")
        elif type(user_check) == str and user_check == email:
            st.session_state.update(
                user_id=None, user_name=None, user_already_exists=True
            )
            st.error("Cette adresse email est déjà utilisée.")
        else:
            st.session_state.update(
                user_id=None, user_name=None, user_already_exists=False
            )
            st.error(
                "Une erreur s'est produite lors de l'enregistrement de l'utilisateur. Veuillez réessayer."
            )

    elif not name or not email or not password:
        st.error("Merci de remplir tous les champs.")


# Fonction pour se connecter
def login(email, password):
    """
    Permet à un utilisateur de se connecter à l'application.

    Args:
        email (str): Email de l'utilisateur
        password (str): Mot de passe de l'utilisateur

    Returns:
        tuple: bool : statut de l'authentification
               tuple : utilisateur (nom, email) si l'authentification est réussie,
            ou str : "User not found" (si aucun user trouvé) ou "Invalid password" (si mot de passe incorrect)
    """
    try:
        user = requests.get(
            f"http://{venv['db_host']}:{venv['db_port']}/user",
            json={"email": email, "password": password},
        ).json()

        if user == "utilisateur non trouvé":
            status = None
        elif user == "Mot de passe incorrect":
            status = False
        else:
            status = True

        return status, user

    except UnicodeDecodeError as e:
        st.error(f"Erreur de décodage : {str(e)}")
        return None, None

    except Exception as e:
        st.error(str(e))
        return None, None


# Fonction pour se déconnecter
def logout():
    """
    Permet à un utilisateur de se déconnecter de l'application.

    Args:
        None

    Returns:
        None
    """
    try:
        if st.session_state["authentication_status"]:
            st.session_state.update(
                user_name=None, username=None, authentication_status=False
            )
            st.success("Vous êtes maintenant déconnecté.")
        else:
            st.error("Vous n'êtes pas connecté.")

    except Exception as e:
        st.error(str(e))
