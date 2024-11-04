import pandas as pd
from faker import Faker
import random
import os

# Paths
base_path = os.path.dirname(__file__)
psa_rm_path = os.path.join(
    base_path, "downloaded_files", "UC_RS_LP_RES_SKILLS_DETLS_22_1440892995.xlsx"
)
coaff_path = os.path.join(base_path, "downloaded_files", "Coaff_V1.xlsx")
certs_path = os.path.join(
    base_path, "downloaded_files", "UC_RS_RESOURCE_LIC_CERT_22_564150616.xlsx"
)
fixtures_coaff = os.path.join(base_path, "fixtures", "fixtures_coaff.csv")
fixtures_psarm = os.path.join(base_path, "fixtures", "fixtures_psarm.csv")
fixtures_certs = os.path.join(base_path, "fixtures", "fixtures_certs.csv")

fake = Faker()

# Retrieve data from the PSA RM file
psa_rm_df = pd.read_excel(psa_rm_path)

# Read existing data from the COAFF file
coaff_df = pd.read_excel(coaff_path)
# Set the 3rd row as the header and remove the first two rows
coaff_df = coaff_df.rename(columns=coaff_df.iloc[2].to_dict()).drop(coaff_df.index[:3])

# Read existing data from the certifications file
certs_df = pd.read_excel(certs_path)
# Set the first row as the header to remove unnecessary information
certs_df = certs_df.rename(columns=certs_df.iloc[0].to_dict()).drop(certs_df.index[0])

# Rename the 'Membres' column to 'Nom'
if "Membres" in coaff_df.columns:
    coaff_df.rename(columns={"Membres": "Nom"}, inplace=True)

# Rename the 'Licence/Certificat' column to 'Certification'
if "Licence/Certificat" in certs_df.columns:
    certs_df.rename(columns={"Licence/Certificat": "Certification"}, inplace=True)

# Create a dictionary with certifications and their descriptions
certs_dict = certs_df.set_index("Certification")["Description"].to_dict()
# Remove the '*' character from the values
certs_dict = {key: value.replace("*", "") for key, value in certs_dict.items()}
# Retrieve unique pairs
unique_certs_dict = set(certs_dict.items())

# Retrieve PSA RM column names as a list
# columns_psarm = psa_rm_df.columns.tolist()

# Create a dictionary to store unique values for each PSA RM column
unique_psarm_values = {}
for column in psa_rm_df.columns:
    # Add the key/value to the dictionary
    unique_psarm_values[column] = psa_rm_df[column].unique().tolist()

# Create a dictionary to store unique values for each Certifications column
unique_certs_values = {}
for column in certs_df.columns:
    # Add the key/value to the dictionary
    unique_certs_values[column] = certs_df[column].unique().tolist()

# Replace values of the 'Nom' and 'Supervisor Name' keys with fake values using faker
unique_psarm_values["Nom"] = [
    fake.name() for _ in range(len(unique_psarm_values["Nom"]) - 500)
]
unique_psarm_values["Supervisor Name"] = [
    fake.name() for _ in range(len(unique_psarm_values["Supervisor Name"]))
]

# List of specific IT skills
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

# List of member names
names = unique_psarm_values["Nom"]
print(f"Number of unique names: {len(names)}")
supervisors = unique_psarm_values["Supervisor Name"]

# List of ongoing missions
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


# Generate new fake COAFF data
def generate_fake_coaff(names):
    """
    Generate fake but consistent COAFF data for the given names.

    :param names: list (list of names)
    :return: DataFrame, int (new COAFF data, number of rows)
    """

    fake_data = []
    coaff_rows = 0
    for name in names:
        localisation = random.choice(["Mtp", "Tours", "Paris"])
        coeff = random.choice([100, 105, 115, 150, 170])
        profil = random.choice(["Junior", "Sénior", "Confirmé", "Expert"])
        stream = random.choice(
            [
                "DSIA",
                "MSBI",
                "TALEND",
                "ODI",
                "DataViz",
                "Cloud Azure",
                "Data Integration",
                "Data Management",
            ]
        )
        competency = random.choice(fonctions)
        num_missions = random.randint(3, 8)
        start_date = fake.date_between(start_date="-1y", end_date="today")
        occupancy_rate = random.choice([0.2, 0.5, 0.8])
        available_company_names = company_names[:]
        date_fin = start_date  # Initialize date_fin

        # Generate data for each mission
        for i in range(num_missions):
            if available_company_names:
                missions_en_cours = random.choice(available_company_names)
                available_company_names.remove(missions_en_cours)
            else:
                break

            # If the current mission is "congés", its start date is the end date of the previous mission plus 1 day
            date_demarrage = (
                date_fin + pd.Timedelta(days=1)
                if missions_en_cours == "congés"
                else start_date
            )

            # If the current mission is "congés", its end date is the start date plus 2 weeks
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
            # Update the start date for the next mission
            start_date = (
                date_fin + pd.Timedelta(days=1)
                if missions_en_cours == "congés"
                else fake.date_between(
                    start_date=date_fin - pd.Timedelta(weeks=12),
                    end_date=date_fin - pd.Timedelta(weeks=2),
                )
            )
            # Update the occupancy rate for the next mission
            if missions_en_cours == "congés":
                occupancy_rate = random.choice(
                    [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
                )
            else:
                occupancy_rate = round((1 - row["Tx_occup"]), 1)
            coaff_rows += 1
    return pd.DataFrame(fake_data), coaff_rows


def generate_fake_psarm(names):
    """
    Generate fake but consistent PSA RM data for the given names.

    :param names: list (list of names)
    :return: DataFrame, int (new PSA RM data, number of rows)
    """

    fake_data = []
    psarm_rows = 0

    for name in names:
        code = random.choice(unique_psarm_values["Code"])
        nom = name
        stat_pers = random.choice(unique_psarm_values["Stat. pers."])
        type = random.choice(unique_psarm_values["Type"])
        hr_bu = random.choice(unique_psarm_values["HR Business Unit"])
        dept_descr = random.choice(unique_psarm_values["Dept Descr."])
        exe_bu = random.choice(unique_psarm_values["Executive BU"])
        cgi_ga = random.choice(unique_psarm_values["CGI Groupe d'affaire"])
        cgi_bu = random.choice(unique_psarm_values["CGI BU"])
        stat_employe = random.choice(unique_psarm_values["Statut employé"])
        emploi = random.choice(unique_psarm_values["Emploi"])
        location = random.choice(unique_psarm_values["Location (CGI Office)"])
        classe = random.choice(unique_psarm_values["Classe"])
        step = random.choice(unique_psarm_values["Étape"])
        gl_type = random.choice(unique_psarm_values["Type pmt GL"])
        perm_temp = random.choice(unique_psarm_values["Perm./temp."])
        emploi_cat = random.choice(unique_psarm_values["Catégorie empl."])
        project_role = random.choice(unique_psarm_values["Proj Role"])
        home_country = random.choice(unique_psarm_values["Home Country"])
        home_city = random.choice(unique_psarm_values["Home City"])
        home_state = random.choice(unique_psarm_values["Home State/Prov"])
        tenure = random.choice(unique_psarm_values["CGI Tenure"])
        pro_xp_date = random.choice(unique_psarm_values["Professional Experience Date"])
        location_type = random.choice(unique_psarm_values["Location Type"])
        work_place = random.choice(unique_psarm_values["Lieu Travail"])
        fcp_code = random.choice(unique_psarm_values["Code FCP"])
        pool_descr = random.choice(unique_psarm_values["Pool Descr"])
        supervisor = random.choice(supervisors)
        competency_interest = random.choice(
            unique_psarm_values["Interest Level of Competencies"]
        )
        num_competency = random.randint(3, 7)

        # Generate data for each competency
        for i in range(num_competency):
            competency = random.choice(unique_psarm_values["Competency"])
            description = random.choice(unique_psarm_values["Description"])
            capacity = random.choice(unique_psarm_values["Capacité"])
            proficiency_descr = random.choice(
                unique_psarm_values["Proficiency Description"]
            )
            obtention_year = random.choice(unique_psarm_values["Année obtention"])
            last_year_util = random.choice(unique_psarm_values["Dernière année util."])
            xp_years = random.choice(unique_psarm_values["Années expérience"])

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
                "Interest Level of Competencies": competency_interest,
            }
            fake_data.append(row)

            psarm_rows += 1

    return pd.DataFrame(fake_data), psarm_rows


def generate_fake_certs(names):
    """
    Generate fake but consistent certifications data for the given names.

    :param names: list (list of names)
    :return: DataFrame, int (new certifications data, number of rows)
    """

    fake_data = []
    certs_rows = 0

    unique_certs_list = list(unique_certs_dict)  # Convert the set to a list

    for name in names:
        num_certs = random.randint(1, 3)

        # Generate data for each certification
        for i in range(num_certs):
            certification = random.choice(unique_certs_list)
            date_obtention = fake.date_between(start_date="-5y", end_date="today")
            date_expiration = date_obtention + pd.Timedelta(
                days=random.randint(365, 1096)
            )
            row = {
                "Nom": name,
                "Code_cert": certification[0],
                "Certification": certification[1],
                "Obtention": date_obtention,
                "Expiration": date_expiration,
            }
            fake_data.append(row)

            certs_rows += 1

    return pd.DataFrame(fake_data), certs_rows


new_coaff, coaff_rows = generate_fake_coaff(names)
new_psarm, psarm_rows = generate_fake_psarm(names)
new_certs, certs_rows = generate_fake_certs(names)

# Save the result in a new CSV file
new_coaff.to_csv(fixtures_coaff, index=False)
print(f"Created a COAFF file with {coaff_rows} new rows of data.")
new_psarm.to_csv(fixtures_psarm, index=False)
print(f"Created a PSA RM file with {psarm_rows} new rows of data.")
new_certs.to_csv(fixtures_certs, index=False)
print(f"Created a certifications file with {certs_rows} new rows of data.")
