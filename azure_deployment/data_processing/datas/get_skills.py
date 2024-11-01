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
    psarm_path = (
        r"data_processing\datas\sources\UC_RS_LP_RES_SKILLS_DETLS_22_1440892995.xlsx"
    )
    coaff_path = r"data_processing\datas\sources\Coaff_V1_cleaned.csv"
    output_descriptions = r"data_processing\datas\sources\descriptions_uniques.txt"
    output_profiles = r"data_processing\datas\sources\profils_uniques.txt"

# Read the files into pandas DataFrames
df_psarm = pd.read_excel(psarm_path)
# Read existing data from the COAFF file
df_coaff = pd.read_csv(coaff_path)
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
with open(output_descriptions, "w", encoding="utf-8") as f:
    f.write(formatted_descriptions)

# Write the profiles to a text file
with open(output_profiles, "w", encoding="utf-8") as f:
    f.write(formatted_profil)

print(f"Unique descriptions written to {output_descriptions} in the required format.")
print(f"Unique profiles written to {output_profiles} in the required format.")
