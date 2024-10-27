import os

# Vérifier si l'application est en cours d'exécution dans un conteneur Docker
# et définir l'hôte de la base de données en conséquence
def is_running_in_docker():
    try:
        with open("/proc/1/cgroup", "rt") as f:
            db_api_host = os.getenv("DB_API_HOST")
            db_api_port = os.getenv("DB_API_PORT")
            return db_api_host, db_api_port
    except FileNotFoundError:
        db_api_host = "localhost"
        db_api_port = 5050
        return db_api_host, db_api_port
