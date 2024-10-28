import requests
import pandas as pd
import sqlite3
from bs4 import BeautifulSoup
import pyarrow.parquet as pq

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

def extract_db_data(db_file, query):
    try:
        conn = sqlite3.connect(db_file)
        data = pd.read_sql_query(query, conn)
        conn.close()
        return data
    except Exception as e:
        print(f"Erreur lors de l'extraction des données depuis la base de données : {e}")
        return None

def extract_big_data(big_data_file):
    try:
        table = pq.read_table(big_data_file)
        return table.to_pandas()  # Conversion en DataFrame pandas
    except Exception as e:
        print(f"Erreur lors de l'extraction des données depuis le système big data : {e}")
        return None

def create_db_from_file(db_file, csv_file):
    # Chargement des données du fichier CSV dans un DataFrame
    data = pd.read_csv(csv_file)

    conn = sqlite3.connect(db_file)

    # Enregistrement du DataFrame dans la base de données
    data.to_sql('certifications', conn, if_exists='replace', index=False)

    # Fermeture de la connexion à la base de données
    conn.close()

    print(f"La base de données '{db_file}' a été créée et les données ont été importées dans la table 'certifications'.")

def csv_to_parquet(csv_file, parquet_file):
    # Lire le fichier CSV dans un DataFrame
    data = pd.read_csv(csv_file)

    # Enregistrer le DataFrame au format Parquet
    data.to_parquet(parquet_file, index=False)

    print(f"Le fichier Parquet '{parquet_file}' a été créé à partir du fichier CSV.")


def main():
    # Sources de données
    api_url = "https://intranet.cgi.com/annuaire/api/v1/membres"
    api_data_csv = r"C:\Users\musti\Projets\donnees_extraites\api_data.csv"
    coaff_file = r"C:\Users\musti\Projets\profile-finder\local_deployment\rag_api\data\fixtures\fixtures_coaff.csv"
    certs_file = r"C:\Users\musti\Projets\profile-finder\local_deployment\rag_api\data\fixtures\fixtures_certs.csv"
    psarm_file = r"C:\Users\musti\Projets\profile-finder\local_deployment\rag_api\data\fixtures\fixtures_psarm.csv"
    csv_data_csv = r"C:\Users\musti\Projets\donnees_extraites\csv_data.csv"
    scraping_url = "http://www.cgi.com/"
    scrapping_data_csv = r"C:\Users\musti\Projets\donnees_extraites\scraping_data.csv"
    db_file = r"C:\Users\musti\Projets\donnees_sources\membres.db"
    db_data_csv = r"C:\Users\musti\Projets\donnees_extraites\db_data.csv"
    big_data_file = r"C:\Users\musti\Projets\donnees_sources\membres.parquet"
    bigdata_data_csv = r"C:\Users\musti\Projets\donnees_extraites\bigdata_data.csv"

    # Extraction des données
    api_data = extract_api_data(api_url)
    csv_data = extract_csv_data(coaff_file)
    scraped_data = extract_scraped_data(scraping_url, "article a")
    create_db_from_file(db_file, certs_file)
    db_data = extract_db_data(db_file, "SELECT * FROM certifications")
    csv_to_parquet(psarm_file, big_data_file)
    big_data = extract_big_data(big_data_file)

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
