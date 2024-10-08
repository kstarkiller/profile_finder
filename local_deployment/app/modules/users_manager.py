import os
import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
import bcrypt

# Récupérer les informations de connexion à la base de données
db_user = os.getenv("DB_USER").encode("utf-8")
db_password = os.getenv("DB_PASSWORD").encode("utf-8")

# Remplacer par vos propres informations de connexion
engine = create_engine(
    f"postgresql://{db_user.decode('utf-8')}:{db_password.decode('utf-8')}@localhost:5432/st_users"
)
Base = declarative_base()


class User(Base):
    __tablename__ = "users_credentials"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)


Base.metadata.create_all(engine)

# Créer une session pour interagir avec la base de données
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Fonction pour récupérer un utilisateur par son username + password
def get_user(email, password):
    """
    Récupère un utilisateur par son email et vérifie le mot de passe puis retourne le nom de l'utilisateur et son id.
    Sinon, retourne None.

    Args:
        email (str): Email de l'utilisateur
        password (str): Mot de passe de l'utilisateur

    Returns:
        tuple: Nom de l'utilisateur et son email si l'utilisateur est trouvé,
               sinon str: "User not found" (si aucun user trouvé) ou "Invalid password" (si mot de passe incorrect)
    """

    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    db.close()

    if user:
        valid_password = bcrypt.checkpw(
            password.encode("utf-8"), user.password.encode("utf-8")
        )
        if valid_password:
            return user.name, user.email
        else:
            return "Invalid password"
    else:
        return "User not found"


# Fonction pour créer un nouvel utilisateur
def create_user(name, email, password):
    """
    Crée un nouvel utilisateur dans la base de données.

    Args:
        name (str): Nom de l'utilisateur
        email (str): Email de l'utilisateur
        password (str): Mot de passe de l'utilisateur

    Returns:
        str: Nom de l'utilisateur si l'utilisateur est créé avec succès,
        str: Email de l'utilisateur si l'utilisateur existe déjà,
        str: "User not found" si aucun utilisateur n'est trouvé
    """

    # Hasher le mot de passe avec le salt
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    db = SessionLocal()

    # Vérifier si l'utilisateur existe déjà
    already_known_user = db.query(User).filter(User.email == email).first()
    if already_known_user:
        db.close()
        return already_known_user.email

    else:
        # Stocker l'utilisateur avec le mot de passe hashé
        new_user = User(
            name=name,
            email=email,
            password=hashed_password,
        )
        db.add(new_user)
        db.commit()

        # Récupérer le nom de l'utilisateur créé
        registered_user = get_user(email, password)
        db.close()
        return registered_user


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
        user_check = create_user(name, email, password)

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
            st.success(f"Thank you {user_check[0]}, you're now registered!")
        elif type(user_check) == str and user_check == email:
            st.session_state.update(
                user_id=None, user_name=None, user_already_exists=True
            )
            st.error("This email is already registered. Please use another one.")
        else:
            st.session_state.update(
                user_id=None, user_name=None, user_already_exists=False
            )
            st.error(
                "Sorry, an error occurred while registering you. Please try again."
            )

    elif not name or not email or not password:
        st.error("Please provide a name, an email and a password")


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
        user = get_user(email, password)

        if user == "User not found":
            status = None
        elif user == "Invalid password":
            status = False
        else:
            status = True

        return status, user

    except Exception as e:
        st.error(str(e))
        return None, None


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
            st.success("You have been successfully logged out.")
        else:
            st.error("You are not logged in.")

    except Exception as e:
        st.error(str(e))
