import spacy
import re
import json
import os
from fuzzywuzzy import fuzz

if os.name == 'posix':
    descriptions_file = 'data_processing/datas/sources/descriptions_uniques.txt'
    acronyms_file = 'data_processing/datas/sources/acronyms.txt'
    profiles_file = 'data_processing/datas/sources/profils_uniques.txt'
    professions_file = 'data_processing/datas/sources/professions_uniques.txt'
else:
    descriptions_file = r'C:\Users\k.simon\Projet\avv-matcher\data_processing\datas\sources\descriptions_uniques.txt'
    acronyms_file = r'C:\Users\k.simon\Projet\avv-matcher\data_processing\datas\sources\acronyms.txt'
    profiles_file = r'C:\Users\k.simon\Projet\avv-matcher\data_processing\datas\sources\profils_uniques.txt'
    professions_file = r'C:\Users\k.simon\Projet\avv-matcher\data_processing\datas\sources\professions_uniques.txt'

# Charger le modèle pré-entraîné pour le français
nlp = spacy.load("fr_core_news_lg")

# Liste des compétences
with open(descriptions_file, 'r', encoding='utf-8') as file:
    content = file.read()
# Diviser le contenu en éléments individuels et créer la liste
skills_list = [desc.strip() for desc in content.split(',')]
# Nettoyer la liste en supprimant les guillemets et les espaces superflus
skills_list = [desc.strip('" ') for desc in skills_list]

# Dictionnaire pour les niveaux de compétence et leurs mots-clés associés
skill_levels = {
    "Expert": ["expert", "avancé", "expérimenté"],
    "Faible": ["débutant", "junior", "novice"],
    "Bon": ["intermédiaire", "confirmé", "à l'aise"],
    "Très bon": ["senior", "avancé", "fort"]
}

# Dictionnaire pour les acronymes et leurs définitions
with open(acronyms_file, 'r', encoding='utf-8') as f:
    acronyms_dict = json.load(f)

# Liste des professions
with open(professions_file, 'r', encoding='utf-8') as file:
    content = file.read()
professions_list = [prof.strip() for prof in content.split(',')]
professions_list = [prof.strip('" ') for prof in professions_list]

# Expressions régulières pour détecter différents formats de dates
date_patterns = [
    # Formats existants
    r"\b(\d{1,2}/\d{1,2}/\d{4})\b", # JJ/MM/AAAA
    r"\b(\d{1,2}-\d{1,2}-\d{4})\b", # JJ-MM-AAAA
    r"\b(\d{1,2} \w+ \d{4})\b", # JJ Mois AAAA
    r"\b(\w+ \d{4})\b", # Mois AAAA
    r"\b(\d{1,2} \d{1,2} \d{4})\b", # JJ MM AAAA
    r"\b(\d{1,2}/\d{1,2}/\d{2,4})\b", # JJ/MM/AA
    r"\b(\w+ \d{1,2}, \d{4})\b", # Mois JJ, AAAA
    r"\b(\w+ \d{1,2} \d{4})\b", # Mois JJ AAAA
    r"\b(\d{1,2}-\w+-\d{4})\b", # JJ-Mois-AAAA
    r"\b(\w+ \d{1,2}th, \d{4})\b", # Mois JJth, AAAA
    r"\b(\d{1,2}\.\d{1,2}\.\d{4})\b", # JJ.MM.AAAA
    r"\b(\d{4}-\d{2}-\d{2})\b",  # AAAA-MM-JJ (ISO 8601)
    r"\b(\d{4}/\d{2}/\d{2})\b",  # AAAA/MM/JJ
    r"\b(\d{4}\.\d{2}\.\d{2})\b",  # AAAA.MM.JJ
    r"\b(\d{4} \d{2} \d{2})\b",  # AAAA MM JJ
    r"\b(\d{4}-\w+-\d{2})\b",  # AAAA-Mois-JJ
    r"\b(\d{4} \w+ \d{1,2})\b",  # AAAA Mois JJ
    r"\b(\d{4} \w+)\b",  # AAAA Mois
    r"\b(\d{2}\d{2}\d{2})\b",  # AAMMJJ (format compact)
]

# Expression régulière pour détecter les mois en français
month_pattern = r"\b(janvier|février|fevrier|mars|avril|mai|juin|juillet|août|aout|septembre|octobre|novembre|décembre|decembre|Janvier|Février|Fevrier|Mars|Avril|Mai|Juin|Juillet|Août|Aout|Septembre|Octobre|Novembre|Décembre|Decembre)\b"


# Compilez chaque pattern séparément avec le flag IGNORECASE
date_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in date_patterns]

def detect_dates(text):
    dates = []
    for pattern in date_patterns:
        matches = pattern.findall(text)
        for match in matches:
            date_str = match if isinstance(match, str) else match[0]
            if date_str not in dates:
                dates.append(date_str)
    return dates

def detect_skills_and_levels(text):
    """
    Detect skills and their levels in a given text.
    
    :param text: str (text to analyze)
    :return: dict (skills detected with their levels)
    """

    doc = nlp(text)
    skills_detected = {}

    # Parcours de chaque token dans le document 'doc'
    for token in doc:

        # Parcours de chaque compétence dans la liste 'skills_list'
        for skill in skills_list:

            # Vérifie si le 'skill' et le 'token' ont une similarité supérieure à 65%
            if fuzz.ratio(skill.lower(), token.text.lower()) > 70:
                
                # Ajoute la compétence détectée dans le dictionnaire 'skills_detected' avec un niveau "Non spécifié"
                skills_detected[skill] = "Non spécifié"
                
                # Définit une fenêtre de contexte autour du token courant (7 tokens avant et 8 après)
                context_window = doc[max(0, token.i-7):token.i+8]
                
                # Parcours des niveaux de compétence et des mots-clés associés dans 'skill_levels'
                for level, keywords in skill_levels.items():
                    
                    # Parcours de chaque mot-clé associé à un niveau de compétence
                    for keyword in keywords:
                        
                        # Vérifie si un mot-clé dans la fenêtre de contexte a une similarité supérieure à 80%
                        if any(fuzz.ratio(keyword, t.text.lower()) > 80 for t in context_window):
                            
                            # Trouve les index des tokens dans la fenêtre de contexte correspondant au mot-clé
                            keyword_index = [t.i for t in context_window if fuzz.ratio(keyword, t.text.lower()) > 70]
                            
                            # Si un mot-clé est trouvé dans la fenêtre de contexte et qu'il est à moins de 7 positions du token courant
                            if keyword_index and abs(keyword_index[0] - token.i) <= 7:
                                
                                # Met à jour le niveau de compétence détecté pour cette compétence
                                skills_detected[skill] = level
                                break  # Sort de la boucle des mots-clés une fois le niveau de compétence détecté

    print(f"Compétences détectées : {skills_detected}")
    return skills_detected

def detect_profession(text):
    """
    Detect the main profession in a given text.
    
    :param text: str (text to analyze)
    :return: tuple (main profession detected, confidence level)
    """
    
    doc = nlp(text)
    professions = {}
    
    # Parcours de chaque token dans le document 'doc'
    for token in doc:
        
        # Parcours de chaque profession dans la liste 'professions_list'
        for profession in professions_list:
            
            # Vérifie si la 'profession' et le 'token' ont une similarité supérieure à 70%
            if fuzz.ratio(profession.lower(), token.text.lower()) > 70:
                
                # Ajoute la profession détectée dans le dictionnaire 'professions' avec un niveau de confiance
                professions[profession] = fuzz.ratio(profession.lower(), token.text.lower())
    
    # Trie les professions par ordre de confiance décroissante
    sorted_professions = sorted(professions.items(), key=lambda x: x[1], reverse=True)
    
    # Retourne la profession principale avec le niveau de confiance le plus élevé
    return sorted_professions[0] if sorted_professions else None

def get_main_skill(skills):
    if not skills:
        return None
    # Trie par ordre d'apparition ou par niveau de confiance
    sorted_skills = sorted(skills.items(), key=lambda x: len(x[1]), reverse=True)
    return sorted_skills[0]

def detect_acronyms_and_definitions(text):
    acronyms_detected = {}
    
    for acronym, definition in acronyms_dict.items():
        patterns = [
            rf"\b{re.escape(acronym)}\b",  # Acronyme seul
            rf"{re.escape(acronym)}\s*\({re.escape(definition)}\)",  # Acronyme suivi de définition entre parenthèses
            rf"\b{re.escape(definition)}\b"  # Définition seule
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            
            if matches:
                acronyms_detected[acronym] = definition
                break  # On arrête la recherche pour cet acronyme si on l'a déjà trouvé

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
    dates = detect_dates(query)
    months = []
    skills_with_levels = detect_skills_and_levels(query)
    acronyms_with_definitions = detect_acronyms_and_definitions(query)

    for ent in doc.ents:
        if ent.label_ == "PER":
            if ent.text not in skills_list:
                person_names.append(ent.text)
        elif ent.label_ in ("GPE", "LOC"):
            if ent.text not in skills_list and ent.text not in acronyms_with_definitions:
                location = ent.text
        elif ent.label_ == "DATE":
            dates.append(ent.text)

    # Extraire les mois du texte
    month_matches = re.findall(month_pattern, query.lower())
    months.extend(month_matches)

    # Trier les dates et identifier date de début et date de fin
    dates = sorted(dates)
    date_debut = dates[0] if dates else "Non spécifiée"
    date_fin = dates[1] if len(dates) > 1 else "Non spécifiée"


    # Créer une liste pour enregistrer les valeurs
    values = []

    # Ajouter les valeurs de person_names s'il y en a
    if person_names:
        values.extend(person_names)

    # Ajouter la valeur de location si elle est spécifiée
    if location:
        values.append(location)

    # Ajouter les valeurs de dates s'il y en a
    if dates:
        values.extend(dates)

    # Ajouter les valeurs de months s'il y en a
    if months:
        values.extend(months)

    # Ajouter la valeur de skill_with_levels s'il y en a
    if skills_with_levels:
        values.extend(skills_with_levels.keys())

    # Ajouter les valeurs de acronyms_with_definitions s'il y en a
    if acronyms_with_definitions:
        values.extend(acronyms_with_definitions.keys())

    # Convertir la liste en une chaîne de caractères séparée par des virgules
    values_str = ', '.join(values)

    # Afficher les valeurs
    print(f"Valeur(s) détéctée(s) : {values_str}")
    return values_str