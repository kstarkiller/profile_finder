import spacy
import re

# Charger le modèle pré-entraîné pour le français
nlp = spacy.load("fr_core_news_sm")

# Liste simplifiée de compétences pour l'exemple
skills_list = ["intelligence artificielle", "data science", "programmation", "gestion de projet"]

# Expressions régulières pour détecter différents formats de dates, si nécessaire
date_patterns = [
    r"\b(\d{1,2}/\d{1,2}/\d{4})\b",  # Format DD/MM/YYYY
    r"\b(\d{1,2}-\d{1,2}-\d{4})\b",  # Format DD-MM-YYYY
    r"\b(\d{1,2} \w+ \d{4})\b",      # Format DD Month YYYY (ex: 15 septembre 2024)
    r"\b(\d{1,2} \d{1,2} \d{4})\b",  # Format DD MM YYYY (ex: 28 05 2025)
]

# Compile all patterns into a single regex
date_pattern = re.compile("|".join(date_patterns))

# Fonction pour détecter les compétences
def detect_skills(text):
    skills_detected = []
    for skill in skills_list:
        if skill.lower() in text.lower():
            skills_detected.append(skill)
    return skills_detected

# Fonction pour traiter la requête
def process_query(query):
    # Analyser la requête utilisateur
    doc = nlp(query)
    
    # Extraction des entités
    person = None
    location = None
    dates = []
    skills = detect_skills(query)

    for ent in doc.ents:
        if ent.label_ == "PER" and ent.text.lower() != "date":
            person = ent.text
        elif ent.label_ in ("GPE", "LOC"):
            location = ent.text
        elif ent.label_ == "DATE":
            print(f"Detected date entity by SpaCy: {ent.text}")
            dates.append(ent.text)

    # Ajouter les dates détectées par regex
    date_matches = date_pattern.findall(query)
    print(f"Regex date matches: {date_matches}")
    for match in date_matches:
        # Extraire la première partie non vide du tuple
        date_str = next(filter(None, match), None)
        if date_str and date_str not in dates:  # Évite les doublons et les valeurs vides
            dates.append(date_str)

    # Trier les dates et identifier date de début et date de fin
    dates = sorted(dates)  # Trier les dates
    print(f"All detected dates: {dates}")
    date_debut = dates[0] if dates else "Non spécifiée"
    date_fin = dates[1] if len(dates) > 1 else "Non spécifiée"
    
    # Format de la réponse
    response = (
        f"Nom : {person or 'Non spécifié'}\n"
        f"Compétences : {', '.join(skills) if skills else 'Non spécifiées'}\n"
        f"Localisation : {location or 'Non spécifiée'}\n"
        f"Date début : {date_debut}\n"
        f"Date de fin : {date_fin}"
    )

    return response

# Exemple d'utilisation
query = """La société XYZ recherche une entreprise de services numériques (ESN) pour un projet de développement logiciel avancé. Le projet concerne le développement d'une application de gestion de données destinée à une utilisation interne. Le candidat idéal devra posséder une expertise approfondie dans les domaines suivants : développement en Python, data science, gestion de projet et intelligence artificielle.

Nom du projet : Application de Gestion Intelligente de Données (AGID)

Compétences requises :

Un professionnel nommé Kevin Durant, Thibaut Dupont
Maîtrise des langages de programmation Python et Java
Expérience en développement de solutions basées sur l'intelligence artificielle et l'apprentissage automatique
Compétences en gestion de projet et méthodologies agiles
Expérience en conception de bases de données et gestion des données

Date de début : 15 septembre 2024
Date de fin : 28 05 2025

Le projet se déroulera principalement à Lyon, avec des possibilités de télétravail partiel en fonction de l'avancement du projet et des besoins spécifiques. Les soumissionnaires intéressés sont invités à soumettre leur proposition avant le 31 août 2024, en détaillant leur approche méthodologique, les compétences de l'équipe proposée, ainsi que les coûts estimés.

Nous attendons des propositions qui mettent en avant l'innovation, l'efficacité et une approche collaborative. Le prestataire sélectionné devra être capable de fournir un support continu et des améliorations post-livraison, en garantissant la pérennité et la scalabilité de l'application développée."""

print(process_query(query))

