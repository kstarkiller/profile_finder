from pymongo import MongoClient
from gridfs import GridFS, NoFile
import os

separator = '\\' if os.name == 'nt' else '/'

def store_file(file, MONGO_USER, MONGO_PWD, MONGO_HOST, MONGO_PORT, MONGO_DB, file_type):
    # Connexion à la base de données MongoDB
    try:
        client = MongoClient(f'mongodb://{MONGO_USER}:{MONGO_PWD}@{MONGO_HOST}:{MONGO_PORT}/?authSource=admin')
        db = client[MONGO_DB]
        grid_fs = GridFS(db, collection=file_type)

        # Sauvegarde du fichier dans GridFS
        with open(file, 'rb') as file_data:
            grid_fs.put(file_data, filename=file.split(separator)[-1])

        return "Fichier stocké avec succès dans MongoDB."
    except Exception as e:
        return f"Erreur lors de la sauvegarde du fichier dans MongoDB : {str(e)}"

def download_file(filename, MONGO_USER, MONGO_PWD, MONGO_HOST, MONGO_PORT, MONGO_DB, file_type):
    try:
        print(filename)
        client = MongoClient(f'mongodb://{MONGO_USER}:{MONGO_PWD}@{MONGO_HOST}:{MONGO_PORT}/?authSource=admin')
        db = client[MONGO_DB]
        grid_fs = GridFS(db, collection=file_type)

        # Vérification de l'existence du fichier
        if not grid_fs.exists(filename=filename):
            return f"Le fichier '{filename}' n'existe pas dans GridFS."

        # Chargement du dernier fichier stocké dans GridFS
        try:
            file_data = grid_fs.get_last_version(filename=filename)
        except NoFile:
            return f"Aucune version trouvée pour le fichier '{filename}'."

        if file_data:
            output_file_path = fr"data{separator}downloaded_files{separator}{filename}"
            print(output_file_path)
            with open(output_file_path, 'wb') as output_file:
                output_file.write(file_data.read())

        return f"Fichier '{filename}' téléchargé avec succès."
    except Exception as e:
        return f"Erreur lors du téléchargement du fichier depuis MongoDB : {str(e)}"