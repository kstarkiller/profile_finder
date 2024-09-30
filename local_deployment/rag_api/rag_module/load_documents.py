import os
import pandas as pd


def load_documents(file_path):
    """
    Loads a .csv document(s) from the specified file_path.

    Args:
        file_path (str): The path to the directory containing the document(s).

    Returns:
        List: A list where each line is a line of the document(s).
    """

    # Check if the directory exists
    if not os.path.exists(file_path):
        raise ValueError(f"The directory {file_path} does not exist.")

    documents = pd.DataFrame()

    try:
        # Crawl the directory to find the file
        files = os.listdir(file_path)
        if not files:
            raise ValueError("No files found in the directory.")

        for file in files:
            file_ext = os.path.splitext(file)[1].lower()

            # Check if the file is a .csv file
            if file_ext == ".csv":
                documents = pd.read_csv(os.path.join(file_path, file))
            else:
                raise ValueError(f"The file {file} has an unsupported extension.")

            # Transform the 'Combined' column into a list
            documents = documents["Combined"].apply(lambda x: x.split("\n"))
            documents = documents.to_list()

            # Flatten the document because it is a list of list of strings
            documents = [item for sublist in documents for item in sublist]

    except Exception as e:
        raise ValueError(f"Error loading the document: {e}")

    return documents
