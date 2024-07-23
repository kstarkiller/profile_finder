import pandas as pd
import os
import tiktoken

from processing_data.normalizing import normalize_text

pd.options.mode.chained_assignment = None


def tokenizing(df, tokenizer="cl100k_base"):
    """
    Count the number of tokens for each row in the dataframe
    and the total number of tokens in the dataframe.

    Use tokenizer cl100k_base if not specified.

    :param df: DataFrame
    :param tokenizer: str
    :return: DataFrame, int
    """
    # (TU)
    if df.empty:
        df["combined"] = []
        df["n_tokens"] = []
        return df, 0
    
    tokenizer = tiktoken.get_encoding(tokenizer)

    # Joining all values of a row into one column
    df["combined"] = df.apply(
        lambda row: f"Nom: {row['Nom']}, "
        + f"Localisation: {row['Localisation']}, "
        + f"Fonction: '{row['Competences']}', "
        + (
            "Disponible, "
            if row["Missions en cours"] == "DISPO ICE"
            else f"Mission: '{row['Missions en cours']}', "
        )
        + (
            f"Dates de disponibilité: {row['Date Demarrage']} - {row['Date de fin']}, "
            if row["Missions en cours"] == "DISPO ICE"
            else f"Dates de mission: {row['Date Demarrage']} - {row['Date de fin']}, "
        )
        + (
            f"Mois de disponibilité: '{row['Mois']}', "
            if row["Missions en cours"] == "DISPO ICE"
            else f"Mois de mission: '{row['Mois']}', "
        )
        + (
            f"Taux d'occupation: {int((1 - float(row['Taux occupation']))*100)}%"
            if row["Missions en cours"] == "DISPO ICE"
            else f"Taux d'occupation: {int(float(row['Taux occupation'])*100)}%"
        ),
        axis=1,
    )

    # Tokenizing the combined column
    df["n_tokens"] = df["combined"].apply(lambda x: len(tokenizer.encode(x)))

    # Counting the total number of tokens
    total_tokens = df["n_tokens"].sum()

    return df, total_tokens


def data_processing_coaff(file_path, tokenizer):
    """
    Load the data from a csv file and normalize it.
    Then use count_tokens() to count the number of tokens in the dataframe.

    :param file_path: str
    :return: DataFrame, int
    """
    # Check if the file exists and load it
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_path} not found.")
    df = pd.read_csv(file_path)

    # Normalizing columns' names
    df.columns = [normalize_text(col) for col in df.columns]

    # Convert columns to string type
    df = df.astype(str)

    # Normalizing values of string columns
    for col in df.columns:
        df[col] = df[col].apply(normalize_text)

    # Changing the name of the column 'Tx occup'
    df.rename(columns={"Tx occup": "Taux occupation"}, inplace=True)

    # Replace "," by "-" in the "Competences" column
    df["Competences"] = df["Competences"].apply(lambda x: x.replace(", ", " - "))

    # Pour chaque ligne, récupérer tous les mois entre les dates de début et de fin, et les convertir en chaîne
    df["Mois"] = df.apply(
        lambda row: ", ".join(
            pd.date_range(
                row["Date Demarrage"], row["Date de fin"], freq="MS"
            ).strftime("%B %Y")
        ),
        axis=1,
    )

    # Si le mois de Date Demarrage et le mois de Date de fin sont égaux, ajouter ce mois à la colonne "Mois"
    df["Mois"] = df.apply(
        lambda row: (
            f"{pd.to_datetime(row['Date Demarrage']).strftime('%B %Y')}"
            if pd.to_datetime(row["Date Demarrage"]).month
            == pd.to_datetime(row["Date de fin"]).month
            else row["Mois"]
        ),
        axis=1,
    )

    # Combine the values of the columns into one column and count tokens
    df, total_token = tokenizing(df, tokenizer)

    # Save the processed data
    df.to_csv("processing_data/datas/processed_data_v2.csv", index=False)

    return df, total_token



data_processing_coaff("processing_data/datas/fixtures_coaff.csv", "cl100k_base")
