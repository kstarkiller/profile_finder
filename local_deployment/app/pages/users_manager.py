import os
import streamlit as st
import streamlit_authenticator as stauth
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import bcrypt

# Récupérer les informations de connexion à la base de données
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')

# Remplacer par vos propres informations de connexion
engine = create_engine(f'postgresql://{db_user}:{db_password}@localhost:5432/st_users')
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String,
                   unique=True,
                   index=True)
    password = Column(String)

Base.metadata.create_all(engine)

# Créer une session pour interagir avec la base de données
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_user(name, email, password):
    db = SessionLocal()
    new_user = User(name=name, email=email, password=password)
    db.add(new_user)
    db.commit()
    db.close()

st.title("Inscription")

name = st.text_input("Nom")
email = st.text_input("Email")
password = st.text_input("Mot de passe", type="password")

if st.button("New here? Sign up"):
    # Hasher le mot de passe ici avant de l'enregistrer
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    create_user(name, email, hashed_password)
    st.success("Utilisateur créé avec succès !")