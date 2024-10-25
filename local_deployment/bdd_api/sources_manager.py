import os
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker

from docker_check import is_running_in_docker

db_host, api_host = is_running_in_docker()

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
    f"postgresql://{db_user}:{db_password}@{db_host}:{port}/{db_name}"
)
Base = declarative_base()

# Définir le modèle de la table raw_profiles
class Profile(Base):
    __tablename__ = "raw_profiles"
    id = Column(Integer, primary_key=True, index=True)
    membres = Column(String, nullable=False)
    missions = Column(String, nullable=False)
    competences = Column(String, nullable=False)
    certifications = Column(String, nullable=False)
    combined = Column(String, nullable=False)


# Créer les tables dans la base de données
Base.metadata.create_all(engine)

# Créer une session pour interagir avec la base de données
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_profiles():
    session = SessionLocal()
    profiles = session.query(Profile).all()
    session.close()
    return {"profiles": profiles}

def truncate_table():
    session = SessionLocal()
    session.query(Profile).delete()
    session.commit()
    session.close()
    return {"message": "Table vidée avec succès"}

def insert_profile(payload: dict):
    session = SessionLocal()
    profile = Profile(
        membres=payload["membre"],
        missions=payload["mission"],
        competences=payload["competence"],
        certifications=payload["certification"],
        combined=payload["combined"]
    )
    session.add(profile)
    session.commit()
    session.close()
    return {"message": "Profil ajouté avec succès"}