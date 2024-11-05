import pandas as pd
import os

# Paths
base_path = os.path.dirname(__file__)
psarm_path = os.path.join(
    base_path, "downloaded_files", "UC_RS_LP_RES_SKILLS_DETLS_22_1440892995.xlsx"
)
coaff_path = os.path.join(base_path, "downloaded_files", "Coaff_V1.xlsx")
output_descriptions = os.path.join(
    base_path, "downloaded_files", "descriptions_uniques.txt"
)
output_profiles = os.path.join(base_path, "downloaded_files", "profils_uniques.txt")

def get_skills(temp_psarm, temp_coaff, temp_desc, temp_profiles):
    # Read the files into pandas DataFrames
    df_psarm = pd.read_excel(temp_psarm)
    # Read existing data from the COAFF file
    df_coaff = pd.read_excel(temp_coaff)
    df_coaff = df_coaff.rename(columns=df_coaff.iloc[2].to_dict()).drop(df_coaff.index[:3])

    # Extract the "Description" column and get unique values
    descriptions = df_psarm["Description"].unique()

    # Extract the "PROFIL" column and get unique values
    profil = df_coaff["PROFIL"].unique()


    # Function to escape apostrophes
    def escape_apostrophes(text):
        return text.replace("'", "\\'")


    # Filter non-null values, escape apostrophes, and format them as required
    formatted_descriptions = ", ".join(
        f'"{escape_apostrophes(desc)}"' for desc in descriptions if pd.notna(desc)
    )
    formatted_profil = ", ".join(
        f'"{escape_apostrophes(profil)}"' for profil in profil if pd.notna(profil)
    )

    # Write the formatted descriptions to a text file
    with open(temp_desc, "w", encoding="utf-8") as f:
        f.write(formatted_descriptions)

    # Write the profiles to a text file
    with open(temp_profiles, "w", encoding="utf-8") as f:
        f.write(formatted_profil)

    return f"Descriptions and profiles have been written to {temp_desc} and {temp_profiles} respectively."