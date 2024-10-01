import os
import streamlit as st
import streamlit_authenticator as stauth
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
import bcrypt

# Récupérer les informations de connexion à la base de données
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")

# Remplacer par vos propres informations de connexion
engine = create_engine(f"postgresql://{db_user}:{db_password}@localhost:5432/st_users")
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)


Base.metadata.create_all(engine)

# Créer une session pour interagir avec la base de données
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Get users credentials with a database query
def get_credentials_from_database():
    db = SessionLocal()
    users = db.query(User).all()
    db.close()

    usernames = [user.email for user in users]
    names = [user.name for user in users]
    passwords = [user.password for user in users]

    return {
        "usernames": {
            usernames[i]: {
                "name": names[i],
                "email": usernames[i],
                "password": passwords[i],
            }
            for i in range(len(usernames))
        }
    }


credentials = get_credentials_from_database()

# Create an authenticator object
authenticator = stauth.Authenticate(
    credentials, "some_cookie_name", "some_signature_key", cookie_expiry_days=10
)


# Fonction pour récupérer un utilisateur par son username + password
def get_user(email, password):
    """
    Récupère un utilisateur par son email et vérifie le mot de passe puis retourne le nom de l'utilisateur et son id.
    Sinon, retourne None.

    Args:
        email (str): Email de l'utilisateur
        password (str): Mot de passe de l'utilisateur

    Returns:
        tuple: (id, name) de l'utilisateur si l'utilisateur existe, sinon None
    """

    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    db.close()

    if user and bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
        return user.name

    return None


# Fonction pour créer un nouvel utilisateur
def create_user(name, email, password):
    """
    Crée un nouvel utilisateur dans la base de données.

    Args:
        name (str): Nom de l'utilisateur
        email (str): Email de l'utilisateur
        password (str): Mot de passe de l'utilisateur

    Returns:
        str: Nom de l'utilisateur si l'utilisateur est créé, sinon l'email de l'utilisateur si l'utilisateur existe déjà
    """

    # Générer un salt
    salt = bcrypt.gensalt()
    # Hasher le mot de passe avec le salt
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)

    db = SessionLocal()

    # Vérifier si l'utilisateur existe déjà
    already_known_user = db.query(User).filter(User.email == email).first()
    if already_known_user:
        db.close()
        return already_known_user.email

    else:
        # Stocker l'utilisateur avec le mot de passe hashé
        new_user = User(
            name=name, email=email, password=hashed_password.decode("utf-8")
        )
        db.add(new_user)
        db.commit()

        # Récupérer le nom de l'utilisateur créé
        registered_user_name = get_user(email, password)
        db.close()
        return registered_user_name


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

        if user_check == name:
            st.session_state.update(
                user_id=None, user_name=None, user_already_exists=False
            )
            st.success(f"Thank you {user_check}, you're now registered!")
        elif user_check == email:
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


def login():
    """
    Permet à un utilisateur de se connecter à l'application.

    Args:
        None

    Returns:
        None
    """
    try:
        # Render login widget
        name, authentication_status, username = authenticator.login(
            "main",
            None,
            3,
            {
                "Form name": "Connexion",
                "Username": "Email",
                "Password": "Password",
                "Login": "Login",
            },
            False,
            True,
        )

    except Exception as e:
        st.error(str(e))

    st.session_state.update(name=name,
                            username=username,
                            authentication_status=authentication_status)

    if authentication_status:
        st.session_state.update(user_name=name, logout=False)

    elif authentication_status == False:
        st.error("Username/password is incorrect")

        if st.button(
            "New here? Sign up",
            on_click=lambda: st.session_state.update(show_signup_form=True),
        ):
            pass

    elif authentication_status == None :
        if st.button(
            "New here? Sign up",
            on_click=lambda: st.session_state.update(show_signup_form=True),
        ):
            pass

def logout():
    """
    Permet à un utilisateur de se déconnecter de l'application.

    Args:
        None

    Returns:
        None
    """

    authenticator.logout("Logout", "sidebar")
    st.session_state.update(user_name=None, logout=True, authentication_status=None)