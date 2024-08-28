import spacy
import re
import json
import os
from fuzzywuzzy import fuzz
from acronyms import acronyms_dict

if os.name == 'posix':
    descriptions_file = '/home/kevin/simplon/briefs/avv-matcher/data_processing/datas/sources/descriptions_uniques.txt'
    acronyms_file = '/home/kevin/simplon/briefs/avv-matcher/data_processing/datas/sources/acronyms.txt'
    profiles_file = '/home/kevin/simplon/briefs/avv-matcher/data_processing/datas/sources/profils_uniques.txt'
else:
    descriptions_file = r'C:\Users\k.simon\Projet\avv-matcher\data_processing\datas\sources\descriptions_uniques.txt'
    acronyms_file = r'C:\Users\k.simon\Projet\avv-matcher\data_processing\datas\sources\acronyms.txt'
    profiles_file = r'C:\Users\k.simon\Projet\avv-matcher\data_processing\datas\sources\profils_uniques.txt'

# Charger le modèle pré-entraîné pour le français
nlp = spacy.load("fr_core_news_lg")

# Liste des compétences
with open(descriptions_file, 'r', encoding='utf-8') as file:
    # Lire toutes les lignes du fichier et les mettre dans une liste
    skills_list = [line.strip() for line in file]

# Dictionnaire pour les niveaux de compétence et leurs mots-clés associés
skill_levels = {
    "Expert": ["expert", "avancé", "expérimenté"],
    "Junior": ["débutant", "junior", "novice"],
    "Intermédiaire": ["intermédiaire", "confirmé"],
    "Senior": ["senior"]
}

# Dictionnaire pour les acronymes et leurs définitions
with open(acronyms_file, 'r', encoding='utf-8') as f:
    acronyms_dict = json.load(f)

# Expressions régulières pour détecter différents formats de dates
date_patterns = [
    r"\b(\d{1,2}/\d{1,2}/\d{4})\b",
    r"\b(\d{1,2}-\d{1,2}-\d{4})\b",
    r"\b(\d{1,2} \w+ \d{4})\b",
    r"\b(\d{1,2} \d{1,2} \d{4})\b",
]

# Expression régulière pour détecter les mois
month_pattern = r"\b(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\b"

# Compile all patterns into a single regex
date_pattern = re.compile("|".join(date_patterns))

def detect_skills_and_levels(text):
    """
    Detect skills and their levels in a given text.
    
    :param text: str (text to analyze)
    :return: dict (skills detected with their levels)
    """

    doc = nlp(text)
    skills_detected = {}

    # Parcours de chaque token dans le document 'doc'
    for i, token in enumerate(doc):
        
        # Parcours de chaque compétence dans la liste 'skills_list'
        for skill in skills_list:
            
            # Vérifie si le 'skill' et le 'token' ont une similarité supérieure à 70%
            if fuzz.ratio(skill.lower(), token.text.lower()) > 70:
                
                # Ajoute la compétence détectée dans le dictionnaire 'skills_detected' avec un niveau "Non spécifié"
                skills_detected[skill] = "Non spécifié"
                
                # Définit une fenêtre de contexte autour du token courant (7 tokens avant et 8 après)
                context_window = doc[max(0, i-7):i+8]
                
                # Parcours des niveaux de compétence et des mots-clés associés dans 'skill_levels'
                for level, keywords in skill_levels.items():
                    
                    # Parcours de chaque mot-clé associé à un niveau de compétence
                    for keyword in keywords:
                        
                        # Vérifie si un mot-clé dans la fenêtre de contexte a une similarité supérieure à 70%
                        if any(fuzz.ratio(keyword, t.text.lower()) > 70 for t in context_window):
                            
                            # Trouve les index des tokens dans la fenêtre de contexte correspondant au mot-clé
                            keyword_index = [t.i for t in context_window if fuzz.ratio(keyword, t.text.lower()) > 70]
                            
                            # Si un mot-clé est trouvé dans la fenêtre de contexte et qu'il est à moins de 7 positions du token courant
                            if keyword_index and abs(keyword_index[0] - token.i) <= 7:
                                
                                # Met à jour le niveau de compétence détecté pour cette compétence
                                skills_detected[skill] = level
                                break  # Sort de la boucle des mots-clés une fois le niveau de compétence détecté


    print(f"Compétences détectées : {skills_detected}")  # Debug print
    return skills_detected

# Fonction pour détecter les acronymes
def detect_acronyms(text):
    """
    Detect acronyms and their definitions in a given text.

    :param text: str (text to analyze)
    :return: dict (acronyms detected with their definitions)
    """

    doc = nlp(text)
    acronyms_detected = {}
    
    for token in doc:
        acronym = token.text.upper()
        if acronym in acronyms_dict:
            acronyms_detected[acronym] = acronyms_dict[acronym]

    print(f"Acronymes détectés : {acronyms_detected}")  # Debug print
    return acronyms_detected

def structure_query(query):
    """
    Process a user query to extract entities and structure it.
    
    :param query: str (user query)
    :return: str (query structured with extracted entities)
    """
    
    print(f"Requête utilisateur : {query}")  # Debug print
    doc = nlp(query)
    
    # Extraction des entités
    person_names = []
    location = None
    dates = []
    months = []
    skills_with_levels = detect_skills_and_levels(query)
    acronyms_with_definitions = detect_acronyms(query)

    for ent in doc.ents:
        if ent.label_ == "PER":
            if ent.text not in skills_list:
                person_names.append(ent.text)
        elif ent.label_ in ("GPE", "LOC"):
            if ent.text not in skills_list and ent.text not in acronyms_with_definitions:
                location = ent.text
        elif ent.label_ == "DATE":
            dates.append(ent.text)

    # Ajouter les dates détectées par regex
    date_matches = date_pattern.findall(query.lower())
    for match in date_matches:
        date_str = next(filter(None, match), None)
        if date_str and date_str not in dates:
            dates.append(date_str)

    # Extraire les mois du texte
    month_matches = re.findall(month_pattern, query.lower())
    months.extend(month_matches)

    # Trier les dates et identifier date de début et date de fin
    dates = sorted(dates)
    # date_debut = dates[0] if dates else "Non spécifiée"
    # date_fin = dates[1] if len(dates) > 1 else "Non spécifiée"
    
    print(f"Noms détectés : {person_names}")  # Debug print
    print(f"Localisation détectée : {location}")  # Debug print
    print(f"Dates détectées : {dates}")  # Debug print
    print(f"Mois détectés : {months}")  # Debug print

    # Format de la réponse
    response = (
        f"Noms : {', '.join(person_names) if person_names else 'Non spécifiés'}\n"
        f"Compétences : {', '.join(f'{skill} ({level})' for skill, level in skills_with_levels.items()) if skills_with_levels else 'Non spécifiées'}\n"
        f"Localisation : {location or 'Non spécifiée'}\n"
        # f"Date début : {date_debut}\n"
        # f"Date de fin : {date_fin}\n"
        f"Mois mentionnés : {', '.join(months) if months else 'Non spécifiés'}\n"
        f"Acronymes détectés : {', '.join(f'{acr} ({defn})' for acr, defn in acronyms_with_definitions.items()) if acronyms_with_definitions else 'Aucun'}"
    )
    
    print(f"Réponse générée : \n{response}")  # Debug print

    return response