import os
from datetime import datetime
import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker
import bcrypt

# Récupérer les informations de connexion à la base de données
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")
host = os.getenv("HOST")
port = os.getenv("PORT")

# Vérifier si les variables d'environnement sont définies
if not db_user or not db_password:
    raise ValueError(
        "Les variables d'environnement DB_USER et DB_PASSWORD doivent être définies"
    )

# Remplacer par vos propres informations de connexion
engine = create_engine(f"postgresql://{db_user}:{db_password}@{host}:{port}/{db_name}")
Base = declarative_base()


class User(Base):
    __tablename__ = "users_credentials"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)


class SearchHistory(Base):
    __tablename__ = "search_histories"
    chat_id = Column(String, unique=True, index=True, primary_key=True)
    chat_title = Column(String)
    user_email = Column(String, ForeignKey("users_credentials.email"))
    creation_date = Column(String)
    last_update_date = Column(String)

    def to_dict(self):
        return {
            "chat_id": self.chat_id,
            "chat_title": self.chat_title,
            "user_email": self.user_email,
            "creation_date": self.creation_date,
            "last_update_date": self.last_update_date,
        }


class ChatHistory(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True)
    chat_id = Column(String, ForeignKey("search_histories.chat_id"))
    role = Column(String)
    content = Column(String)
    generation_time = Column(String)

    def to_dict(self):
        return {
            "chat_id": self.chat_id,
            "role": self.role,
            "content": self.content,
            "generation_time": self.generation_time,
        }


# Créer les tables dans la base de données
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
        try:
            valid_password = bcrypt.checkpw(
                password.encode("utf-8"), user.password.encode("utf-8")
            )
        except UnicodeDecodeError as e:
            return f"Erreur de décodage : {str(e)}"

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
        user = get_user(email, password)

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


# Fonction pour ajouter une recherche à la base de données des recherches de l'utilisateur
def add_search_to_history(chat_id, first_message, user_email):
    """
    Ajoute une recherche à l'historique des recherches de l'utilisateur.

    Args:
        chat_id (str): Identifiant de la recherche
        first_message (str): Premier message de la recherche
        user_email (str): Email de l'utilisateur

    Returns:
        None
    """
    db = SessionLocal()
    new_search = SearchHistory(
        chat_id=chat_id,
        chat_title=first_message,
        user_email=user_email,
        creation_date=str(datetime.today()),
        last_update_date=str(datetime.today()),
    )
    db.add(new_search)
    db.commit()
    db.close()


# Fonction pour mettre à jour une recherche dans la base de données des recherches de l'utilisateur
def update_search_in_history(chat_id):
    """
    Met à jour une recherche dans l'historique des recherches de l'utilisateur.

    Args:
        chat_id (str): Identifiant de la recherche

    Returns:
        None
    """
    db = SessionLocal()
    search = db.query(SearchHistory).filter(SearchHistory.chat_id == chat_id).first()
    search.last_update_date = str(datetime.today())
    db.commit()
    db.close()


# Fonction pour récuperer la liste des recherches de l'utilisateur
def get_search_history(user_email):
    """
    Récupère la liste des recherches de l'utilisateur.

    Args:
        user_email (str): Email de l'utilisateur

    Returns:
        list: Liste des recherches de l'utilisateur
    """
    db = SessionLocal()
    search_history = (
        db.query(SearchHistory).filter(SearchHistory.user_email == user_email).all()
    )
    db.close()

    return [search.to_dict() for search in search_history]


# Fonction pour récuperer une recherche par son chat_id
def get_search_by_chat_id(chat_id):
    """
    Récupère une recherche par son identifiant.

    Args:
        chat_id (str): Identifiant de la recherche

    Returns:
        dict: Détails de la recherche
    """
    db = SessionLocal()
    search = db.query(SearchHistory).filter(SearchHistory.chat_id == chat_id).first()
    chat_history = db.query(ChatHistory).filter(ChatHistory.chat_id == chat_id).all()
    db.close()

    return {
        "chat_id": search.chat_id,
        "chat_history": [chat.to_dict() for chat in chat_history],
    }


# Fonction pour ajouter un message à la conversation en fonction du nombre de messages
def add_message_to_chat(chat_id, chat_history, duration):
    """
    Ajoute un message à la conversation en fonction du nombre de messages.

    Args:
        chat_id (str): Identifiant de la conversation
        chat_history (list): Historique de la conversation

    Returns:
        None
    """
    db = SessionLocal()
    search = db.query(ChatHistory).filter(ChatHistory.chat_id == chat_id).all()
    # Compter le nombre de messages dans la conversation
    message_count = len(search)
    # Ajouter les nouveaux messages à la conversation
    for i, message in enumerate(chat_history):
        if i < message_count:
            continue
        else:
            new_message = ChatHistory(
                chat_id=chat_id,
                role=message["role"],
                content=message["content"],
                generation_time=duration,
            )
            db.add(new_message)
    db.commit()
    db.close()

def delete_search_from_history(chat_id):
    """
    Supprime une recherche de l'historique des recherches de l'utilisateur.

    Args:
        chat_id (str): Identifiant de la recherche

    Returns:
        None
    """
    db = SessionLocal()
    try:
        # Supprimer les entrées correspondantes dans la table conversations
        db.query(ChatHistory).filter(ChatHistory.chat_id == chat_id).delete()
        # Supprimer l'entrée dans la table search_histories
        search = db.query(SearchHistory).filter(SearchHistory.chat_id == chat_id).first()
        db.delete(search)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()