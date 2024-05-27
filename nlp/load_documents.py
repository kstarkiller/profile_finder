import os
import textract

# Fonction pour charger les documents
def load_documents(file_path):
    """
    Charge les documents à partir du chemin spécifié.
    De nombreux types de fichiers sont supportés :
    .doc, .docx, .eml, .epub, .gif, .jpg, .json, .html, .png, .pdf, .pptx, .ps, .rtf, .tiff, .txt, .xlsx, .xls, etc.

    Args:
        file_path (str): Le chemin vers le répertoire contenant les fichiers.

    Returns:
        list: Une liste de dictionnaires contenant le nom du fichier et son contenu.
    """
    documents = []
    for filename in os.listdir(file_path):
        try:
            file_content = textract.process(os.path.join(file_path, filename))
            documents.append(file_content.decode('utf-8'))
        except textract.exceptions.ExtensionNotSupported as e:
            print(f"Le fichier {filename} a une extension non supportée.")
    return documents
