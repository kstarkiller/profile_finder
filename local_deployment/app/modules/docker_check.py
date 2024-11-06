import os


# Vérifier si l'application est en cours d'exécution dans un conteneur Docker
# et définir l'hôte de la base de données en conséquence
def is_running_in_docker():
    try:
        with open("/proc/1/cgroup", "rt") as f:
            db_host = os.getenv("DB_API_HOST")
            db_port = os.getenv("DB_API_PORT")
            rag_host = os.getenv("RAG_API_HOST")
            rag_port = os.getenv("RAG_API_PORT")
        return {"db_host": db_host, "db_port": db_port, "rag_host": rag_host, "rag_port": rag_port}
    except FileNotFoundError:
        db_host = "localhost"
        db_port = 5050
        rag_host = "localhost"
        rag_port = 8080
        return {"db_host": db_host, "db_port": db_port, "rag_host": rag_host, "rag_port": rag_port}
