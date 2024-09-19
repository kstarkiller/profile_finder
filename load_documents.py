import os
import pandas as pd

if os.name == "posix":
    DOC_PATH = r"/home/kevin/simplon/briefs/avv-matcher/rag_local_api/sources"
else:
    DOC_PATH = r"C:\Users\k.simon\Projet\avv-matcher\rag_local_api\sources"


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
        raise ValueError(f"Le répertoire {file_path} n'existe pas.")

    documents = pd.DataFrame()

    try:
        # Crawl the directory to find the file
        files = os.listdir(file_path)
        if not files:
            raise ValueError("Aucun fichier trouvé dans le répertoire.")

        for file in files:
            file_ext = os.path.splitext(file)[1].lower()

            # Check if the file is a .csv file
            if file_ext == ".csv":
                documents = pd.read_csv(os.path.join(file_path, file))
            else:
                raise ValueError(f"Le fichier {file} a une extension non supportée.")

            # transform the 'Combined' column into a list
            documents = documents["Combined"].apply(lambda x: x.split("\n"))
            documents = documents.to_list()

            # Flatten the document because it is a list of list of strings
            documents = [item for sublist in documents for item in sublist]

    except Exception as e:
        raise ValueError(f"Erreur lors du chargement du document: {e}")

    return documents
