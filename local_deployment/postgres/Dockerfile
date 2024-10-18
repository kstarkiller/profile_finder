# Utiliser une image Docker officielle de PostgreSQL comme base
FROM postgres:latest

# Définir les variables d'environnement pour PostgreSQL
ARG POSTGRES_USER
ARG POSTGRES_PASSWORD
ARG POSTGRES_DB

# Récupérer les variables d'environnement pour PostgreSQL
ENV POSTGRES_USER=${POSTGRES_USER}
ENV POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
ENV POSTGRES_DB=${POSTGRES_DB}

# Expose port 5432
EXPOSE 5432

# Ajouter une commande pour créer le rôle postgres
RUN echo "CREATE ROLE postgres WITH LOGIN SUPERUSER PASSWORD '${POSTGRES_PASSWORD}';" > /docker-entrypoint-initdb.d/create_postgres_role.sql