from pymongo import MongoClient
from gridfs import GridFS, NoFile
import os

separator = '\\' if os.name == 'nt' else '/'

def store_file(file, MONGO_USER, MONGO_PWD, MONGO_HOST, MONGO_PORT, MONGO_DB):
    """
    Fonction permettant de stocker un fichier dans une base de données MongoDB

    Args:
    file (str): Chemin du fichier à stocker
    MONGO_USER (str): Nom d'utilisateur de la base de données MongoDB
    MONGO_PWD (str): Mot de passe de la base de données MongoDB
    MONGO_HOST (str): Adresse IP du serveur MongoDB
    MONGO_PORT (int): Port du serveur MongoDB
    MONGO_DB (str): Nom de la base de données MongoDB

    Returns:
    str: Message de confirmation du stockage du fichier
    """
    try:
        # Connexion à la base de données MongoDB
        client = MongoClient(f'mongodb://{MONGO_USER}:{MONGO_PWD}@{MONGO_HOST}:{MONGO_PORT}/?authSource=admin')
        db = client[MONGO_DB]
        grid_fs = GridFS(db, collection="files")

        # Sauvegarde du fichier dans GridFS
        with open(file, 'rb') as file_data:
            grid_fs.put(file_data, filename=file.split(separator)[-1])

        return "Fichier traité avec succès !"
    except Exception as e:
        return f"Erreur lors du traitement de votre fichier : {str(e)}"

def download_files(MONGO_USER, MONGO_PWD, MONGO_HOST, MONGO_PORT, MONGO_DB):
    """
    Fonction permettant de télécharger tous les fichiers stockés dans une base de données MongoDB

    Args:
    MONGO_USER (str): Nom d'utilisateur de la base de données MongoDB
    MONGO_PWD (str): Mot de passe de la base de données MongoDB
    MONGO_HOST (str): Adresse IP du serveur MongoDB
    MONGO_PORT (int): Port du serveur MongoDB
    MONGO_DB (str): Nom de la base de données MongoDB

    Returns:
    str: Message de confirmation du téléchargement du fichier
    """
    try:
        # Connexion à la base de données MongoDB
        client = MongoClient(f'mongodb://{MONGO_USER}:{MONGO_PWD}@{MONGO_HOST}:{MONGO_PORT}/?authSource=admin')
        db = client[MONGO_DB]
        grid_fs = GridFS(db, collection="files")

        # Chargement du dernier fichier stocké dans GridFS
        try:
            files_names = grid_fs.list()
            print(files_names)
            # Ne garder que les filenames uniques
            files_names = list(set(files_names))
            print(files_names)
            for filename in files_names:
                try:
                    file_data = grid_fs.get_last_version(filename)
                    output_file_path = fr"data{separator}downloaded_files{separator}{filename}"
                    with open(output_file_path, 'wb') as output_file:
                        output_file.write(file_data.read())
                except NoFile:
                    return f"Aucune version du fichier {filename} trouvée."
        except NoFile:
            return f"Aucun fichier trouvé dans la base de données."
        
        return f"Fichiers téléchargés avec succès."
    except Exception as e:
        return f"Erreur lors du téléchargement du fichier depuis MongoDB : {str(e)}"