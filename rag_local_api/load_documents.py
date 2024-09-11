import os
import textract
import openpyxl
import pandas as pd

if os.name == 'posix':
    DOC_PATH = r"/home/kevin/simplon/briefs/avv-matcher/rag_local_api/sources"
else:
    DOC_PATH = r"C:\Users\k.simon\Projet\avv-matcher\rag_local_api\sources"

def load_documents(file_path):
    '''
    Loads a .csv document from the specified file path.

    Args:
        file_path (str): The path to the directory containing the .csv document.

    Returns:
        List: A list where each line is a line of the document.
    '''

    # Load the document
    documents = pd.DataFrame()

    for file in os.listdir(file_path):
        try:
            file_ext = os.path.splitext(file)[1].lower()
            if file_ext == ".csv":
                documents = pd.read_csv(os.path.join(file_path, file))

        except textract.exceptions.ExtensionNotSupported as e:
            print(f"Le fichier {file} a une extension non supportée.")

        # transform the 'Combined' column into a list
        documents = documents['Combined'].apply(lambda x: x.split("\n"))
        documents = documents.to_list()

    return documents