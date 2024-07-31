import spacy
import re
from spacy.lang.fr.stop_words import STOP_WORDS as fr_stop
from fuzzywuzzy import fuzz

# Charger le modèle pré-entraîné pour le français
nlp = spacy.load("fr_core_news_lg")

# Liste simplifiée de compétences pour l'exemple
skills_list = ["SQL", "Analyse des données", "SAS", "Linux", "Salesforce", "Python"]

# Dictionnaire pour les niveaux de compétence et leurs mots-clés associés
skill_levels = {
    "Expert": ["expert", "avancé", "expérimenté"],
    "Junior": ["débutant", "junior", "novice"],
    "Intermédiaire": ["intermédiaire", "confirmé"],
    "Senior": ["senior"]
}

# Expressions régulières pour détecter différents formats de dates
date_patterns = [
    r"\b(\d{1,2}/\d{1,2}/\d{4})\b",
    r"\b(\d{1,2}-\d{1,2}-\d{4})\b",
    r"\b(\d{1,2} \w+ \d{4})\b",
    r"\b(\d{1,2} \d{1,2} \d{4})\b",
]

# Compile all patterns into a single regex
date_pattern = re.compile("|".join(date_patterns))

# Fonction pour détecter les compétences et leurs niveaux
def detect_skills_and_levels(text):
    doc = nlp(text)
    skills_detected = {}

    for i, token in enumerate(doc):
        for skill in skills_list:
            if fuzz.ratio(skill.lower(), token.text.lower()) > 70:
                skills_detected[skill] = "Non spécifié"
                context_window = doc[max(0, i-7):i+8]  # Augmenter la fenêtre de contexte de 7 avant à 8 après
                for level, keywords in skill_levels.items():
                    for keyword in keywords:
                        if any(fuzz.ratio(keyword, t.text.lower()) > 70 for t in context_window):
                            keyword_index = [t.i for t in context_window if fuzz.ratio(keyword, t.text.lower()) > 70]
                            if keyword_index and abs(keyword_index[0] - token.i) <= 7:
                                skills_detected[skill] = level
                                break
    return skills_detected

def process_query(query):
    # Analyser la requête utilisateur
    doc = nlp(query)
    
    # Extraction des entités
    person_names = []
    location = None
    dates = []
    skills_with_levels = detect_skills_and_levels(query)

    for ent in doc.ents:
        if ent.label_ == "PER":
            # Filtrer les noms de compétences incorrectement classés comme personnes
            if ent.text not in skills_list:
                person_names.append(ent.text)
        elif ent.label_ in ("GPE", "LOC"):
            location = ent.text
        elif ent.label_ == "DATE":
            dates.append(ent.text)

    # Ajouter les dates détectées par regex
    date_matches = date_pattern.findall(query.lower())
    for match in date_matches:
        date_str = next(filter(None, match), None)
        if date_str and date_str not in dates:
            dates.append(date_str)

    # Trier les dates et identifier date de début et date de fin
    dates = sorted(dates)
    date_debut = dates[0] if dates else "Non spécifiée"
    date_fin = dates[1] if len(dates) > 1 else "Non spécifiée"
    
    # Format de la réponse
    response = (
        f"Noms : {', '.join(person_names) if person_names else 'Non spécifiés'}\n"
        f"Compétences : {', '.join(f'{skill} ({level})' for skill, level in skills_with_levels.items()) if skills_with_levels else 'Non spécifiées'}\n"
        f"Localisation : {location or 'Non spécifiée'}\n"
        f"Date début : {date_debut}\n"
        f"Date de fin : {date_fin}"
    )

    return response

# Exemple d'utilisation
query = """La société XYZ recherche une entreprise de services numériques (ESN) pour un projet de développement logiciel avancé. Le projet concerne le développement d'une application de gestion de données destinée à une utilisation interne. Le candidat idéal devra posséder une expertise approfondie dans les domaines suivants : développement en Python, data science, gestion de projet et intelligence artificielle.

Nom du projet : Application de Gestion Intelligente de Données (AGID)

Compétences requises :

Un professionnel expert en Python nommé Kevin Durant, Thibaut Dupont
Maîtrise des langages de programmation Python et Java Soutien à l‘innovation
Expérience en développement de solutions basées sur l'intelligence artificielle et l'apprentissage automatique
Compétences en gestion de projet et méthodologies agiles
Expérience en conception de bases de données et gestion des données

Date de début : 15 septembre 2024
Date de fin : 28 05 2025

Il doit vivre à Lyon et qui serait expert en SAS...
"""

print(process_query(query))
