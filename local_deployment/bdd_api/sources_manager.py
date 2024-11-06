import os
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker

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


# Définir le modèle de la table raw_profiles
class Profile(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True, index=True)
    membres = Column(String, nullable=False)
    missions = Column(String, nullable=False)
    competences = Column(String, nullable=False)
    certifications = Column(String, nullable=False)
    combined = Column(String, nullable=False)


class TempProfile(Base):
    __tablename__ = "temp_profiles"
    id = Column(Integer, primary_key=True)
    membres = Column(String)
    missions = Column(String)
    competences = Column(String)
    certifications = Column(String)
    combined = Column(String)
    type = Column(String)


# Créer les tables dans la base de données
Base.metadata.create_all(engine)

# Créer une session pour interagir avec la base de données
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_profiles(params: dict):
    """
    Get all profiles from the database.

    Returns:
        dict: A dictionary containing the profiles.
    """
    try:
        session = SessionLocal()
        profiles = TempProfile if params["type"] == "temp" else Profile
        profiles = session.query(profiles).all()
        if not profiles:
            session.close()
            return {"profiles": []}
        else:
            session.close()
            return {"profiles": profiles}
    except Exception as e:
        raise f"Erreur lors de la récupération des profils: {str(e)}"


def delete_profile(profile: dict):
    """
    Delete a profile from the database.

    Args:
        profile (dict): A dictionary containing the profile information with the following keys:
            - id: The ID of the profile to delete.

    Returns:
        dict: A dictionary with a success message.
    """
    session = SessionLocal()
    session.query(Profile).filter(Profile.id == profile["id"]).delete()
    session.commit()
    session.close()
    return {"message": "Profil supprimé avec succès"}


def truncate_table(params):
    """
    Truncate the raw_profiles table in the database.

    Returns:
        dict: A dictionary with a success message.
    """
    session = SessionLocal()
    (
        session.query(TempProfile).delete()
        if params["type"] == "temp"
        else session.query(Profile).delete()
    )
    session.commit()
    session.close()
    return {"message": "Table vidée avec succès"}


def insert_profile(payload: dict):
    """
    Insert a new profile into the database.

    Args:
        payload (dict): A dictionary containing profile information with the following keys:
            - membre: Information about the member.
            - mission: Information about the mission.
            - competence: Information about the competence.
            - certification: Information about the certification.
            - combined: Combined information.

    Returns:
        dict: A dictionary with a success message.
    """
    try:
        session = SessionLocal()
        profile = (
            TempProfile(
                membres=payload["membre"],
                missions=payload["mission"],
                competences=payload["competence"],
                certifications=payload["certification"],
                combined=payload["combined"],
                type=payload["type"],
            )
            if payload["type"] == "temp"
            else Profile(
                membres=payload["membre"],
                missions=payload["mission"],
                competences=payload["competence"],
                certifications=payload["certification"],
                combined=payload["combined"],
            )
        )

        session.add(profile)
        session.commit()
        session.close()
        return {"message": "Profil ajouté avec succès"}
    except Exception as e:
        raise Exception(f"Erreur lors de l'ajout du profil: {str(e)}")
