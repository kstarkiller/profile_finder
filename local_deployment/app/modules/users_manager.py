import streamlit as st
import bcrypt
import requests

from modules.docker_check import is_running_in_docker

db_api_host, db_api_port, rag_api_host, rag_api_port = is_running_in_docker()

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
        encrypted_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        user_check = requests.post(f"http://{db_api_host}:{db_api_port}/create_user",
                                   json={"name": name, "email": email, "password": encrypted_password}).json()
        if (
            type(user_check) == tuple
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
        encrypted_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        user = requests.get(f"http://{db_api_host}:{db_api_port}/get_user",
                            json={"email": email, "password": encrypted_password}).json()

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
