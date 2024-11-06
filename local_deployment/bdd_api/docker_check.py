import os


# Vérifier si l'application est en cours d'exécution dans un conteneur Docker
# et définir l'hôte de la base de données en conséquence
def is_running_in_docker():
    try:
        with open("/proc/1/cgroup", "rt") as f:
            db_user = os.getenv("DB_USER")
            db_pwd = os.getenv("DB_PASSWORD")
            db_name = os.getenv("DB_NAME")
            db_host = os.getenv("DB_HOST")
            db_port = os.getenv("DB_PORT")
            return {
                "db_user": db_user,
                "db_pwd": db_pwd,
                "db_name": db_name,
                "db_host": db_host,
                "db_port": db_port,
            }
    except FileNotFoundError:
        db_user = os.getenv("DB_USER")
        db_pwd = os.getenv("DB_PASSWORD")
        db_name = os.getenv("DB_NAME")
        db_host = "localhost"
        db_port = "5432"
        return {
            "db_user": db_user,
            "db_pwd": db_pwd,
            "db_name": db_name,
            "db_host": db_host,
            "db_port": db_port,
        }
