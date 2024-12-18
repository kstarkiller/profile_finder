import os
from datetime import datetime
import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker
import bcrypt

from docker_check import is_running_in_docker

venv = is_running_in_docker()

# Récupérer les informations de connexion à la base de données
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")
port = os.getenv("PORT")

# Vérifier si les variables d'environnement sont définies
if not db_user or not db_password:
    raise ValueError(
        "Les variables d'environnement DB_USER et DB_PASSWORD doivent être définies"
    )

# Créer une connexion à la base de données
engine = create_engine(
    f"postgresql://{venv['db_user']}:{venv['db_pwd']}@{venv['db_host']}:{venv['db_port']}/{venv['db_name']}"
)
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
    model = Column(String)
    model_label = Column(String)
    gen_duration = Column(String)
    gen_time = Column(String)

    def to_dict(self):
        return {
            "chat_id": self.chat_id,
            "role": self.role,
            "content": self.content,
            "model": self.model,
            "model_label": self.model_label,
            "gen_duration": self.gen_duration,
            "gen_time": self.gen_time,
        }


# Créer les tables dans la base de données
Base.metadata.create_all(engine)

# Créer une session pour interagir avec la base de données
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def check_user(email):
    """
    Vérifie si l'utilisateur existe dans la base de données.

    Args:
        email (str): Email de l'utilisateur

    Returns:
        User: Objet utilisateur si l'utilisateur est trouvé, sinon None
    """
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    db.close()

    if user:
        return user.email
    else:
        return None


# Fonction pour récupérer un utilisateur par son username + password
def get_user(email, password):
    """
    Récupère un utilisateur par son email et vérifie le mot de passe puis retourne le nom de l'utilisateur et son id.
    Sinon, retourne None.

    Args:
        email (str): Email de l'utilisateur
        password (str): Mot de passe de l'utilisateur crypté

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
        password (str): Mot de passe de l'utilisateur crypté

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


# Fonction pour supprimer un compte utilisateur
def delete_user(email, password):
    """
    Supprime un utilisateur de la base de données.

    Args:
        email (str): Email de l'utilisateur
        password (str): Mot de passe de l'utilisateur crypté

    Returns:
        str: "Invalid password" si le mot de passe est incorrect,
        str: "User deleted" si l'utilisateur est supprimé avec succès
    """
    try:
        db = SessionLocal()

        # Vérifier si l'utilisateur existe
        user = db.query(User).filter(User.email == email).first()
        if not user:
            db.close()
            return "User not found"

        # Vérifier si le mot de passe est correct
        valid_password = bcrypt.checkpw(
            password.encode("utf-8"), user.password.encode("utf-8")
        )
        if not valid_password:
            db.close()
            return "Invalid password"

        # Supprimer l'utilisateur et ses données
        searches = get_search_history(email)
        for search in searches:
            db.query(ChatHistory).filter(
                ChatHistory.chat_id == search["chat_id"]
            ).delete()
            db.query(SearchHistory).filter(
                SearchHistory.chat_id == search["chat_id"]
            ).delete()
        db.delete(user)
        db.commit()
        db.close()
        return "User deleted"
    except Exception as e:
        return f"Erreur lors de la suppression de l'utilisateur : {str(e)}"


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
    try:
        db = SessionLocal()
        search_history = (
            db.query(SearchHistory).filter(SearchHistory.user_email == user_email).all()
        )
        db.close()

        return [search.to_dict() for search in search_history]
    except Exception as e:
        return str(e)


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
def add_message_to_chat(chat_id, chat_history, duration, model, model_label):
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
                model=model,
                model_label=model_label,
                gen_duration=duration,
                gen_time=str(datetime.now().replace(microsecond=0)),
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
        search = (
            db.query(SearchHistory).filter(SearchHistory.chat_id == chat_id).first()
        )
        db.delete(search)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def delete_all_searches_from_history(user_email):
    """
    Supprime toutes les recherches de l'historique des recherches de l'utilisateur.

    Args:
        user_email (str): Email de l'utilisateur

    Returns:
        None
    """
    db = SessionLocal()
    try:
        # Récupérer tous les chat_id de l'utilisateur dans la table search_histories
        searches = get_search_history(user_email)
        # Supprimer les entrées correspondantes dans la table conversations
        for search in searches:
            db.query(ChatHistory).filter(
                ChatHistory.chat_id == search["chat_id"]
            ).delete()
            db.query(SearchHistory).filter(
                SearchHistory.chat_id == search["chat_id"]
            ).delete()

        db.commit()
    except Exception as e:
        db.rollback()
        raise f"Erreur lors de la suppression des recherches de l'utilisateur : {str(e)}"
    finally:
        db.close()
