import os
import textract


# Loading the documents
def load_documents(file_path):
    """
    Loads the documents from the specified file path.

    Args:
        file_path (str): The path to the directory containing the documents.

    Returns:
        list: A list of documents.
    """
    documents = []
    for filename in os.listdir(file_path):
        try:
            file_content = textract.process(os.path.join(file_path, filename))
            documents.append(file_content.decode("utf-8"))

        except textract.exceptions.ExtensionNotSupported as e:
            print(f"Le fichier {filename} a une extension non supportée.")

    return documents
