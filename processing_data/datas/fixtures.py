import pandas as pd
from faker import Faker
import random

fake = Faker()

# Récupération des données
psa_rm_path = r"processing_data/datas/UC_RS_LP_RES_SKILLS_DETLS_22_1440892995.xlsx"
psa_rm_df = pd.read_excel(psa_rm_path)

# Lire les données existantes à partir du fichier COAFF
coaff_df = pd.read_csv(
    r"C:\Users\k.simon\Projet\avv-matcher\processing_data\datas\Coaff_V1_cleaned.csv"
)

# Renommer la colonne 'Membres' en 'Nom'
if "Membres" in coaff_df.columns:
    coaff_df.rename(columns={"Membres": "Nom"}, inplace=True)

# Récupérer le noms des colonnes PSA RM sous formes de liste
columns = psa_rm_df.columns.tolist()

# Créer un dictionnaire pour stocker les valeurs uniques de chaque colonne PSA RM
unique_values = {}
for column in psa_rm_df.columns:
    # Ajouter la clé/valeur dans le dictionnaire
    unique_values[column] = psa_rm_df[column].unique().tolist()

# Remplacer les valeurs de la clé 'Nom' et 'Supervisor Name' par des fausses valeurs grâce à faker
unique_values['Nom'] = [fake.name() for _ in range(len(unique_values['Nom']))]
unique_values['Supervisor Name'] = [fake.name() for _ in range(len(unique_values['Supervisor Name']))]

# Liste des compétences IT spécifiques
fonctions = [
    "DevOps",
    "Direction de projet",
    "SAS",
    "SSIS",
    "Cybersecurity",
    "MsBI/BO",
    "Pilotage BT",
    "Talend, Talend BD",
    "Talend BD",
    "Power BI, Azure, BO, Qlik",
    "Data Ing + Data S.",
    "Informatica stambia, talend, datastage",
    "Datastage",
    "Azure",
    "UX",
]

# Liste des nom des membres
names = unique_values["Nom"]
supervisors = unique_values["Supervisor Name"]

# Liste des missions en cours
company_names = [
    "Orange",
    "Bouygues",
    "Enedis",
    "Engie",
    "LVMH",
    "Fraikin",
    "Dalkia",
    "Club Med",
    "BPCE",
    "Société Générale",
    "COVEA",
    "La Poste",
    "DISPO ICE",
    "congés",
]

# Générer de nouvelles données de faux COAFF
def generate_fake_coaff(names):
    fake_data = []
    coaff_rows = 0

    for name in names:
        localisation = random.choice(["Mtp", "Tours", "Paris"])
        coeff = random.choice([100, 105, 115, 150, 170])
        profil = random.choice(["Junior", "Sénior", "Confirmé", "Expert"])
        stream = random.choice(["DSIA", "MSBI", "TALEND", "ODI", "DataViz", "Cloud Azure", "Data Integration", "Data Management",])
        competency = random.choice(fonctions)
        num_missions = random.randint(3, 8)
        start_date = fake.date_between(start_date="-1y", end_date="today")
        occupancy_rate = random.choice([0.2, 0.5, 0.8])

        # Générer des données pour chaque mission
        for i in range(num_missions):
            missions_en_cours = random.choice(company_names)

            # Si la mission actuelle est "congés", sa date de début est la date de fin de la mission précédente plus 1 jour
            date_demarrage = (
                date_fin + pd.Timedelta(days=1) 
                if missions_en_cours == "congés"
                else start_date
            )

            # Si la mission actuelle est "congés", sa date de fin est la date de début plus 2 semaines
            date_fin = (
                date_demarrage + pd.Timedelta(weeks=2)
                if missions_en_cours == "congés"
                else fake.date_between(
                    start_date=date_demarrage,
                    end_date=date_demarrage + pd.Timedelta(weeks=52),
                )
            )
            row = {
                "Localisation": localisation,
                "COEFF_F212": coeff,
                "PROFIL": profil,
                "Nom": name,
                "Missions_en_cours": missions_en_cours,
                "Competences": competency,
                "Date_Demarrage": date_demarrage,
                "Date_de_fin": date_fin,
                "Tx_occup": 1.0 if missions_en_cours == "congés" else occupancy_rate,
                "Stream_BT": stream,
            }
            fake_data.append(row)

            # Mettre à jour la date de début pour la prochaine mission
            start_date = (
                date_fin + pd.Timedelta(days=1)
                if missions_en_cours == "congés"
                else fake.date_between(
                    start_date=date_fin - pd.Timedelta(weeks=12),
                    end_date=date_fin - pd.Timedelta(weeks=2),
                )
            )

            # Mettre à jour le taux d'occupation pour la prochaine mission
            if missions_en_cours == "congés":
                occupancy_rate = random.choice([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
            else:
                occupancy_rate = round((1 - row["Tx_occup"]), 1)

            coaff_rows += 1
    return pd.DataFrame(fake_data), coaff_rows

def generate_fake_psarm(names):
    fake_data = []
    psarm_rows = 0

    for name in names:
        code = random.choice(unique_values["Code"])
        nom = name
        stat_pers = random.choice(unique_values["Stat. pers."])
        type = random.choice(unique_values["Type"])
        hr_bu = random.choice(unique_values["HR Business Unit"])
        dept_descr = random.choice(unique_values["Dept Descr."])
        exe_bu = random.choice(unique_values["Executive BU"])
        cgi_ga = random.choice(unique_values["CGI Groupe d'affaire"])
        cgi_bu = random.choice(unique_values["CGI BU"])
        stat_employe = random.choice(unique_values["Statut employé"])
        emploi = random.choice(unique_values["Emploi"])
        location = random.choice(unique_values["Location (CGI Office)"])
        classe = random.choice(unique_values["Classe"])
        step = random.choice(unique_values["Étape"])
        gl_type = random.choice(unique_values["Type pmt GL"])
        perm_temp = random.choice(unique_values["Perm./temp."])
        emploi_cat = random.choice(unique_values["Catégorie empl."])
        project_role = random.choice(unique_values["Proj Role"])
        home_country = random.choice(unique_values["Home Country"])
        home_city = random.choice(unique_values["Home City"])
        home_state = random.choice(unique_values["Home State/Prov"])
        tenure = random.choice(unique_values["CGI Tenure"])
        pro_xp_date = random.choice(unique_values["Professional Experience Date"])
        location_type = random.choice(unique_values["Location Type"])
        work_place = random.choice(unique_values["Lieu Travail"])
        fcp_code = random.choice(unique_values["Code FCP"])
        pool_descr = random.choice(unique_values["Pool Descr"])
        supervisor = random.choice(supervisors)
        competency_interest = random.choice(unique_values["Interest Level of Competencies"])
        num_competency = random.randint(3, 7)

        # Générer des données pour chaque compétence
        for i in range(num_competency):
            competency = random.choice(unique_values["Competency"])
            description = random.choice(unique_values["Description"])
            capacity = random.choice(unique_values["Capacité"])
            proficiency_descr = random.choice(unique_values["Proficiency Description"])
            obtention_year = random.choice(unique_values["Année obtention"])
            last_year_util = random.choice(unique_values["Dernière année util."])
            xp_years = random.choice(unique_values["Années expérience"])

            row = {
                "Code": code,
                "Nom": nom,
                "Stat. Pers.": stat_pers,
                "Type": type,
                "HR Business Unit": hr_bu,
                "Dept Descr": dept_descr,
                "Executive BU": exe_bu,
                "CGI Groupe d'affaire": cgi_ga,
                "CGI BU": cgi_bu,
                "Statut employé": stat_employe,
                "Emploi": emploi,
                "Location (CGI Office)": location,
                "Classe": classe,
                "Étape": step,
                "Type pmt GL": gl_type,
                "Perm./temp.": perm_temp,
                "Catégorie empl.": emploi_cat,
                "Proj Role": project_role,
                "Home Country": home_country,
                "Home City": home_city,
                "Home State/Prov": home_state,
                "CGI Tenure": tenure,
                "Professional Experience Date": pro_xp_date,
                "Location Type": location_type,
                "Lieu Travail": work_place,
                "Code FCP": fcp_code,
                "Pool Descr": pool_descr,
                "Competency": competency,
                "Description": description,
                "Capacité": capacity,
                "Proficiency Description": proficiency_descr,
                "Année obtention": obtention_year,
                "Dernière année util.": last_year_util,
                "Années expérience": xp_years,
                "Supervisor Name": supervisor,
                "Interest Level of Competencies": competency_interest
            }
            fake_data.append(row)

            psarm_rows += 1

    return pd.DataFrame(fake_data), psarm_rows

new_coaff, coaff_rows = generate_fake_coaff(names)
new_psarm, psarm_rows = generate_fake_psarm(names)

# Enregistrer le résultat dans un nouveau fichier CSV
new_coaff.to_csv(
    r"C:\Users\k.simon\Projet\avv-matcher\processing_data\datas\fixtures_coaff.csv",
    index=False,
)

new_psarm.to_csv(
    r"C:\Users\k.simon\Projet\avv-matcher\processing_data\datas\fixtures_psarm.csv",
    index=False,
)

print(f"Création d'un fichier PSA RM avec {psarm_rows} nouvelles lignes de données.")
print(f"Création d'un fichier COAFF avec {coaff_rows} nouvelles lignes de données.")