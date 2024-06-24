import pandas as pd
import os
import tiktoken

from processing_data.normalizing import normalize_text

pd.options.mode.chained_assignment = None


def count_tokens(df, tokenizer):
    """
    Count the number of tokens for each row in the dataframe
    and the total number of tokens in the dataframe.

    :param df: DataFrame
    :param tokenizer: str
    :return: DataFrame, int
    """
    tokenizer = tiktoken.get_encoding(tokenizer)

    # Joining all values of a row into one column
    df["combined"] = df.apply(
        lambda row: f"Localisation: {row['Localisation']}, "
        + f"Nom: {row['Nom']}, "
        + f"Compétences: {row['Competences']}, "
        + f"Mission en cours: {row['Missions en cours']}, "
        + f"Date de début de mission: {row['Date Demarrage']}, "
        + f"Date de fin de mission: {row['Date de fin']}, "
        + f"Taux d'occupation: {row['Taux occupation']}",
        axis=1,
    )

    # Tokenizing the combined column
    df["n_tokens"] = df["combined"].apply(lambda x: len(tokenizer.encode(x)))

    # Counting the total number of tokens
    total_tokens = df["n_tokens"].sum()

    return df, total_tokens


def data_processing(file_path, tokenizer):
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

    # Changing the name and  value of the column 'Tx occup'
    df.rename(columns={"Tx occup": "Taux occupation"}, inplace=True)
    df["Taux occupation"] = df["Taux occupation"].apply(
        lambda x: f"{int(float(x) * 100)}%"
    )

    df, total_token = count_tokens(df, tokenizer)

    # Save the processed data
    df.to_csv("processing_data/datas/processed_data.csv", index=False)

    return df, total_token
