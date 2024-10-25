import pandas as pd
import requests
import os

from docker_check import is_running_in_docker

# Paths
base_path = os.path.dirname(__file__)
fixtures_coaff_path = os.path.join(base_path, "fixtures", "fixtures_coaff.csv")
fixtures_psarm_path = os.path.join(base_path, "fixtures", "fixtures_psarm.csv")
fixtures_certs_path = os.path.join(base_path, "fixtures", "fixtures_certs.csv")

coaff_df = pd.read_csv(fixtures_coaff_path)
psarm_df = pd.read_csv(fixtures_psarm_path)
certs_df = pd.read_csv(fixtures_certs_path)

# Join the three dataframes with the 'Nom' column as key
combined_df = pd.merge(coaff_df, psarm_df, on="Nom")
combined_df = pd.merge(combined_df, certs_df, on="Nom")

# Add a "Métier" column for each member and indicate "Développeur, Programmeur" whenever the words "développements" or "programmation" appear in the 'Description' column
combined_df["Métier"] = combined_df["Description"].apply(
    lambda x: (
        "Développeur, Programmeur"
        if "développements" in x or "programmation" in x
        else "Autre"
    )
)

# Create a dictionary to store the results
resultat_dict = {}

# Group the combined dataframe by the columns 'Nom', 'COEFF_F212', 'PROFIL', 'Localisation', 'Stream_BT', 'Code' and 'Supervisor Name'
grouped_df = combined_df.groupby(
    [
        "Nom",
        "COEFF_F212",
        "PROFIL",
        "Localisation",
        "Stream_BT",
        "Code",
        "Supervisor Name",
        "Métier",
    ]
)

# Iterate through each group and extract the necessary information for each member
for (
    nom,
    coeff,
    profil,
    localisation,
    stream_bt,
    code,
    manager,
    métier,
), group in grouped_df:
    availabilities = group.groupby(
        [
            "Missions_en_cours",
            "Competences",
            "Date_Demarrage",
            "Date_de_fin",
            "Tx_occup",
        ]
    )
    competencies = group.groupby(["Description", "Proficiency Description"])
    certifications = group.groupby(
        ["Code_cert", "Certification", "Obtention", "Expiration"]
    )

    # Create a primary key for each member and check if it already exists in the dictionary
    cle_principale = f"Nom: {nom}, Code: {code}, Coefficient: {coeff}, Profil: {profil}, Localisation: {localisation}, Equipe: {stream_bt}, Manager: {manager}, "
    cle_principale += (
        f"Métier: {métier}, " if métier == "Développeur, Programmeur" else ""
    )
    if cle_principale not in resultat_dict:
        resultat_dict[cle_principale] = {
            "Missions": [],
            "Compétences": [],
            "Certifications": [],
        }

    # Iterate through each group and extract the occupation/availability information for each member
    for (mission, competences, demarrage, fin, tx), availabilities in availabilities:
        if mission == "DISPO ICE":
            key_value = (
                f"Available at {int((float(tx))*100)}% from {demarrage} to {fin}"
            )
        elif mission == "congés":
            key_value = f"On leave at {int((float(tx))*100)}% from {demarrage} to {fin}"
        else:
            key_value = f"Mission {competences} at {int((float(tx))*100)}% occupation at {mission} from {demarrage} to {fin}"

        resultat_dict[cle_principale]["Missions"].append(key_value)

    # Iterate through each group and extract the competency information for each member
    for (description, proficiency), competencies in competencies:
        if proficiency == "1-Faible":
            key_value = f"Competent in {description} at a low level"
        elif proficiency == "2-Bon":
            key_value = f"Competent in {description} at a good level"
        elif proficiency == "3-Très bon":
            key_value = f"Competent in {description} at a very good level"
        elif proficiency == "4-Expert":
            key_value = f"Competent in {description} at an expert level"

        resultat_dict[cle_principale]["Compétences"].append(key_value)

    # Iterate through each group and extract the certification information for each member
    for (
        code_cert,
        certification,
        obtention,
        expiration,
    ), certifications in certifications:
        key_value = f"Certified {certification} ({code_cert}) since {obtention} and until {expiration}"

        resultat_dict[cle_principale]["Certifications"].append(key_value)

# Export the dictionary to csv
resultat_df = pd.DataFrame(resultat_dict).T

# Rename the first column to 'Membre'
resultat_df = resultat_df.rename_axis("Membres").reset_index()

# Convert each column to string before concatenation
resultat_df["Combined"] = (
    resultat_df["Membres"].astype(str)
    + resultat_df["Missions"].astype(str)
    + ", "
    + resultat_df["Compétences"].astype(str)
    + ", "
    + resultat_df["Certifications"].astype(str)
)

# Remove the character "\" from the 'Combined' column
resultat_df["Combined"] = resultat_df["Combined"].str.replace('"', "")

db_host, db_port = is_running_in_docker()

# Vider la table raw_profiles avant d'insérer les nouveaux profils
try:
    response = requests.post(f"http://{db_host}:{db_port}/truncate_profiles")
    response.raise_for_status()

    # Insérer le résultat final dans la base de données grâce à une réquète à l'api bdd
    for index, row in resultat_df.iterrows():
        payload = {
            "membre": row["Membres"],
            "mission": row["Missions"],
            "competence": row["Compétences"],
            "certification": row["Certifications"],
            "combined": row["Combined"]
        }

        try:
            response = requests.post(f"http://{db_host}:{db_port}/insert_profile", json=payload)
            response.raise_for_status()
    
        except requests.exceptions.HTTPError as err:
            print("HTTP error occurred:", err)
            print("Response content:", response.content)

except requests.exceptions.HTTPError as err:
    print("HTTP error occurred:", err)
    print("Response content:", response.content)
