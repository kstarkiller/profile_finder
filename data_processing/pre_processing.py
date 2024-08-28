import pandas as pd
from pprint import pprint
import os

# Paths according to the OS
if os.name == 'posix':
    fixture_coaff_path = 'data_processing/datas/fixtures/fixtures_coaff.csv'
    fixture_psarm_path = 'data_processing/datas/fixtures/fixtures_psarm.csv'
    fixtures_certs_path = 'data_processing/datas/fixtures/fixtures_certs.csv'
    combined_result_path = 'data_processing/datas/combined/combined_result.csv'
else:
    fixture_coaff_path = r'C:\Users\k.simon\Projet\avv-matcher\data_processing\datas\fixtures\fixtures_coaff.csv'
    fixture_psarm_path = r'C:\Users\k.simon\Projet\avv-matcher\data_processing\datas\fixtures\fixtures_psarm.csv'
    fixtures_certs_path = r'C:\Users\k.simon\Projet\avv-matcher\data_processing\datas\fixtures\fixtures_certs.csv'
    combined_result_path = r'C:\Users\k.simon\Projet\avv-matcher\data_processing\datas\combined\combined_result.csv'

coaff_df = pd.read_csv(fixture_coaff_path)
psarm_df = pd.read_csv(fixture_psarm_path)
certs_df = pd.read_csv(fixtures_certs_path)

# Joindre les trois dataframes avec la colonne 'Nom' comme clé
combined_df = pd.merge(coaff_df, psarm_df, on='Nom')
combined_df = pd.merge(combined_df, certs_df, on='Nom')

# Créer un dictionnaire pour stocker les résultats
resultat_dict = {}

# Grouper le dataframe combiné par les colonnes 'Nom', 'COEFF_F212', 'PROFIL', 'Localisation', 'Stream_BT', 'Code' et 'Supervisor Name'
grouped_df = combined_df.groupby(['Nom', 'COEFF_F212', 'PROFIL', 'Localisation', 'Stream_BT', 'Code', 'Supervisor Name'])

# Parcourir chaque groupe et extraire les informations nécessaires pour chaque membre
for (nom, coeff, profil, localisation, stream_bt, code, manager), group in grouped_df:
    availabilities = group.groupby(['Missions_en_cours', 'Competences', 'Date_Demarrage', 'Date_de_fin', 'Tx_occup'])
    competencies = group.groupby(['Description', 'Proficiency Description'])
    certifications = group.groupby(['Code_cert', 'Certification', 'Obtention', 'Expiration'])

    # Créer une clé principale pour chaque membre et vérifier si elle existe déjà dans le dictionnaire
    cle_principale = f"Nom: {nom}, Code: {code}, Coefficient: {coeff}, Profil: {profil}, Localisation: {localisation}, Equipe: {stream_bt}, Manager: {manager}"
    if cle_principale not in resultat_dict:
        resultat_dict[cle_principale] = {"Missions": [], "Compétences": [], "Certifications": []} 

    # Parcourir chaque groupe et extraire les informations d'occupation/disponibilité pour chaque membre
    for (mission, competences, demarrage, fin, tx), availabilities in availabilities:
        if mission == 'DISPO ICE':
            key_value = f"Disponible à {int((float(tx))*100)}% du {demarrage} au {fin}"
        elif mission == "congés":
            key_value = f"En congés à {int((float(tx))*100)}% du {demarrage} au {fin}"
        else:
            key_value = f"Mission {competences} à {int((float(tx))*100)}% d'occupation chez {mission} du {demarrage} au {fin}"
    
        resultat_dict[cle_principale]["Missions"].append(key_value)

    # Parcourir chaque groupe et extraire les informations de compétences de chaque membre
    for (description, proficiency), competencies in competencies:
        if proficiency == '1-Faible':
            key_value = f"Compétent en {description} à un niveau faible"
        elif proficiency == '2-Bon':
            key_value = f"Compétent en {description} à un niveau bon"
        elif proficiency == '3-Très bon':
            key_value = f"Compétent en {description} à un niveau très bon"
        elif proficiency == '4-Expert':
            key_value = f"Compétent en {description} à un niveau expert"

        resultat_dict[cle_principale]["Compétences"].append(key_value)

    # Parcourir chaque groupe et extraire les informations de certification de chaque membre
    for (code_cert, certification, obtention, expiration), certifications in certifications:
        key_value = f"Certifié {certification} ({code_cert}) depuis le {obtention} et jusqu'au {expiration}"

        resultat_dict[cle_principale]["Certifications"].append(key_value)

# Exporter le dictionnaire en csv
resultat_df = pd.DataFrame(resultat_dict).T

# Renommer la première colonne en 'Membre'
resultat_df = resultat_df.rename_axis('Membres').reset_index()

# Convertir chaque colonne en chaîne de caractères avant la concaténation
resultat_df['Combined'] = resultat_df['Membres'].astype(str) + resultat_df["Missions"].astype(str) + ", " + resultat_df["Compétences"].astype(str) + ", " + resultat_df["Certifications"].astype(str)

# Supprimer le caractère "\" de la colonne 'Combined'
resultat_df['Combined'] = resultat_df['Combined'].str.replace("\"", "")

# Exporter le résultat final en csv
resultat_df.to_csv(combined_result_path)
pprint(resultat_df['Combined'][0])

