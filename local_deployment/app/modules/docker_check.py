import os

# Vérifier si l'application est en cours d'exécution dans un conteneur Docker
# et définir l'hôte de la base de données en conséquence
def is_running_in_docker():
    try:
        with open("/proc/1/cgroup", "rt") as f:
            db_host = os.getenv("HOST")
            api_host = "172.18.0.3"
            return db_host, api_host
    except FileNotFoundError:
        db_host = "localhost"
        api_host = "localhost"
        return db_host, api_host


db_host, api_host = is_running_in_docker()
