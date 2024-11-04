import os

# Vérifier si l'application est en cours d'exécution dans un conteneur Docker
# et définir l'hôte de la base de données en conséquence
def is_running_in_docker():
    try:
        with open("/proc/1/cgroup", "rt") as f:
            db_api_host = os.getenv("DB_API_HOST")
            db_api_port = os.getenv("DB_API_PORT")
            db_api_user = os.getenv("DB_API_USER")
            db_api_pwd = os.getenv("DB_API_PASSWORD")
            db_api_name = os.getenv("DB_API_NAME")
            mongo_host = os.getenv("MONGO_HOST")
            mongo_port = os.getenv("MONGO_PORT")
            mongo_user = os.getenv("MONGO_USER")
            mongo_pwd = os.getenv("MONGO_PWD")
            mongo_db = os.getenv("MONGO_DB")
            return db_api_host, db_api_port, db_api_user, db_api_pwd, db_api_name, mongo_host, mongo_port, mongo_user, mongo_pwd, mongo_db
    except FileNotFoundError:
        db_api_host = "localhost"
        db_api_port = 5050
        db_api_user = os.getenv("DB_USER")
        db_api_pwd = os.getenv("DB_PASSWORDD")
        db_api_name = os.getenv("DB_NAME")
        mongo_host = "localhost"
        mongo_port = 27017
        mongo_user = os.getenv("MONGO_USER")
        mongo_pwd = os.getenv("MONGO_PWD")
        mongo_db = os.getenv("MONGO_DB")
        return db_api_host, db_api_port, db_api_user, db_api_pwd, db_api_name, mongo_host, mongo_port, mongo_user, mongo_pwd, mongo_db
