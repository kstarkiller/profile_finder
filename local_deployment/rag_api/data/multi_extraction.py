import requests
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from bs4 import BeautifulSoup
from pymongo import MongoClient
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from docker_check import is_running_in_docker

db_host, db_port, db_user, db_pwd, db_name, mongo_host, mongo_port, mongo_user, mongo_pwd, mongo_db = is_running_in_docker()

def extract_api_data(api_url):
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Erreur lors de l'extraction des données depuis l'API : {e}")
        return None

def extract_csv_data(csv_file):
    try:
        data = pd.read_csv(csv_file)
        return data
    except Exception as e:
        print(f"Erreur lors de l'extraction des données depuis le fichier CSV : {e}")
        return None

def extract_scraped_data(url, selector):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        data = [element.text for element in soup.select(selector)]
        return data
    except Exception as e:
        print(f"Erreur lors du scraping des données depuis la page web : {e}")
        return None

def extract_db_data(db_host, db_port, db_name, db_user, db_pwd):
    # Créer une connexion à la base de données
    engine = create_engine(
        f"postgresql://{db_user}:{db_pwd}@{db_host}:{db_port}/{db_name}"
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

    try:
        session = SessionLocal()
        profiles = session.query(Profile).all()
        if not profiles:
            session.close()
            return {"profiles": []}
        else:
            session.close()
            return {"profiles": profiles}
    except Exception as e:
        raise f"Erreur lors de la récupération des profils: {str(e)}"

def extract_big_data(mongo_host, mongo_port, mongo_user, mongo_pwd, mongo_db, collection_name):
    try:
        client = MongoClient(f"mongodb://{mongo_user}:{mongo_pwd}@{mongo_host}:{mongo_port}")
        db = client[mongo_db]
        collection = db[collection_name]
        
        for doc in collection.find():
            data = [doc for doc in collection.find()]
            
        return pd.DataFrame(data)  # Conversion en DataFrame pandas
    except Exception as e:
        print(f"Erreur lors de l'extraction des données depuis MongoDB : {e}")
        return None

def main():
    # Sources de données
    api_data_csv = r"C:\Users\musti\Projets\donnees_extraites\api_data.csv"
    csv_data_csv = r"C:\Users\musti\Projets\donnees_extraites\csv_data.csv"
    scrapping_data_csv = r"C:\Users\musti\Projets\donnees_extraites\scraping_data.csv"
    db_data_csv = r"C:\Users\musti\Projets\donnees_extraites\db_data.csv"
    bigdata_data_csv = r"C:\Users\musti\Projets\donnees_extraites\bigdata_data.csv"

    # Extraction des données
    api_data = extract_api_data("https://intranet.cgi.com/annuaire/api/v1/membres")
    csv_data = extract_csv_data(r"C:\Users\musti\Projets\profile-finder\local_deployment\rag_api\data\fixtures\fixtures_coaff.csv")
    scraped_data = extract_scraped_data("http://www.cgi.com/", "article a")
    db_data = extract_db_data(db_host, db_port, db_name, db_user, db_pwd)
    big_data = extract_big_data(mongo_host, mongo_port, mongo_user, mongo_pwd, mongo_db, "files")

    if api_data:
        print("Données extraites de l'API:", api_data)
        # Stocker les données dans un fichier CSV
        pd.DataFrame(api_data).to_csv(api_data_csv, index=False)
    if csv_data is not None:
        print("Données extraites du CSV:", csv_data)
        # Stocker les données dans un fichier CSV
        pd.DataFrame(csv_data).to_csv(csv_data_csv, index=False)
    if scraped_data:
        print("Données extraites du scraping:", scraped_data)
        # Stocker les données dans un fichier CSV
        pd.DataFrame(scraped_data, columns=["Titres"]).to_csv(scrapping_data_csv, index=False)
    if db_data is not None:
        print("Données extraites de la base de données:", db_data)
        # Stocker les données dans un fichier CSV
        db_data.to_csv(db_data_csv, index=False)
    if big_data is not None:
        print("Données extraites du système big data:", big_data)
        # Stocker les données dans un fichier CSV
        big_data.to_csv(bigdata_data_csv, index=False)


if __name__ == "__main__":
    main()
