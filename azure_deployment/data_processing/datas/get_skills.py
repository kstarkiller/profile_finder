import pandas as pd
import os

# Paths according to the OS
if os.name == "posix":
    psarm_path = (
        "data_processing/datas/sources/UC_RS_LP_RES_SKILLS_DETLS_22_1440892995.xlsx"
    )
    coaff_path = "data_processing/datas/sources/Coaff_V1.xlsx"
    output_descriptions = "data_processing/datas/sources/descriptions_uniques.txt"
    output_profiles = "data_processing/datas/sources/profils_uniques.txt"
else:
    psarm_path = r"C:\Users\k.simon\Projet\avv-matcher\azure_deployment\data_processing\datas\sources\UC_RS_LP_RES_SKILLS_DETLS_22_1440892995.xlsx"
    coaff_path = r"C:\Users\k.simon\Projet\avv-matcher\azure_deployment\data_processing\datas\sources\Coaff_V1_cleaned.csv"
    output_descriptions = r"C:\Users\k.simon\Projet\avv-matcher\azure_deployment\data_processing\datas\sources\descriptions_uniques.txt"
    output_profiles = r"C:\Users\k.simon\Projet\avv-matcher\azure_deployment\data_processing\datas\sources\profils_uniques.txt"

# Lire les fichier dans des DataFrames pandas
df_psarm = pd.read_excel(psarm_path)
# Lire les données existantes à partir du fichier COAFF
df_coaff = pd.read_csv(coaff_path)
df_coaff = df_coaff.rename(columns=df_coaff.iloc[2].to_dict()).drop(df_coaff.index[:3])

# Extraire la colonne "Description" et obtenir les valeurs uniques
descriptions = df_psarm["Description"].unique()

# Extraire la colonne "PROFIL" et obtenir les valeurs uniques
profil = df_coaff["PROFIL"].unique()


# Fonction pour échapper les apostrophes
def escape_apostrophes(text):
    return text.replace("'", "\\'")


# Filtrer les valeurs non nulles, échapper les apostrophes et les mettre au format requis
formatted_descriptions = ", ".join(
    f'"{escape_apostrophes(desc)}"' for desc in descriptions if pd.notna(desc)
)
formatted_profil = ", ".join(
    f'"{escape_apostrophes(profil)}"' for profil in profil if pd.notna(profil)
)

# Écrire les descriptions formatées dans un fichier texte
with open(output_descriptions, "w", encoding="utf-8") as f:
    f.write(formatted_descriptions)

# Ecrire les profils dans un fichier texte
with open(output_profiles, "w", encoding="utf-8") as f:
    f.write(formatted_profil)

print(f"Descriptions uniques écrites dans {output_descriptions} au format requis.")
print(f"Profils uniques écrits dans {output_profiles} au format requis.")
