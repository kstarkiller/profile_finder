import spacy
import re
import json
import os
from fuzzywuzzy import fuzz

base_path = os.path.dirname(__file__)
data_path = os.path.join(base_path, "..", "data", "downloaded_files")

descriptions_file = os.path.join(data_path, "descriptions_uniques.txt")
acronyms_file = os.path.join(data_path, "acronyms.txt")
profiles_file = os.path.join(data_path, "profils_uniques.txt")
professions_file = os.path.join(data_path, "professions_uniques.txt")

# Load the pre-trained model for French
nlp = spacy.load("fr_core_news_lg")

# List of skills
with open(descriptions_file, "r", encoding="utf-8") as file:
    content = file.read()
# Split the content into individual elements and create the list
skills_list = [desc.strip() for desc in content.split(",")]
# Clean the list by removing quotes and extra spaces
skills_list = [desc.strip('" ') for desc in skills_list]

# Dictionary for skill levels and their associated keywords
skill_levels = {
    "Expert": ["expert", "avancé", "expérimenté"],
    "Faible": ["débutant", "junior", "novice"],
    "Bon": ["intermédiaire", "confirmé", "à l'aise"],
    "Très bon": ["senior", "avancé", "fort"],
}

# Dictionary for acronyms and their definitions
with open(acronyms_file, "r", encoding="utf-8") as f:
    acronyms_dict = json.load(f)

# List of professions
with open(professions_file, "r", encoding="utf-8") as file:
    content = file.read()
professions_list = [prof.strip() for prof in content.split(",")]
professions_list = [prof.strip('" ') for prof in professions_list]

# Regular expressions to detect different date formats
date_patterns = [
    # Existing formats
    r"\b(\d{1,2}/\d{1,2}/\d{4})\b",  # DD/MM/YYYY
    r"\b(\d{1,2}-\d{1,2}-\d{4})\b",  # DD-MM-YYYY
    r"\b(\d{1,2} \w+ \d{4})\b",  # DD Month YYYY
    r"\b(\w+ \d{4})\b",  # Month YYYY
    r"\b(\d{1,2} \d{1,2} \d{4})\b",  # DD MM YYYY
    r"\b(\d{1,2}/\d{1,2}/\d{2,4})\b",  # DD/MM/YY
    r"\b(\w+ \d{1,2}, \d{4})\b",  # Month DD, YYYY
    r"\b(\w+ \d{1,2} \d{4})\b",  # Month DD YYYY
    r"\b(\d{1,2}-\w+-\d{4})\b",  # DD-Month-YYYY
    r"\b(\w+ \d{1,2}th, \d{4})\b",  # Month DDth, YYYY
    r"\b(\d{1,2}\.\d{1,2}\.\d{4})\b",  # DD.MM.YYYY
    r"\b(\d{4}-\d{2}-\d{2})\b",  # YYYY-MM-DD (ISO 8601)
    r"\b(\d{4}/\d{2}/\d{2})\b",  # YYYY/MM/DD
    r"\b(\d{4}\.\d{2}\.\d{2})\b",  # YYYY.MM.DD
    r"\b(\d{4} \d{2} \d{2})\b",  # YYYY MM DD
    r"\b(\d{4}-\w+-\d{2})\b",  # YYYY-Month-DD
    r"\b(\d{4} \w+ \d{1,2})\b",  # YYYY Month DD
    r"\b(\d{4} \w+)\b",  # YYYY Month
    r"\b(\d{2}\d{2}\d{2})\b",  # YYMMDD (compact format)
]

# Regular expression to detect months in French
month_pattern = r"\b(janvier|février|fevrier|mars|avril|mai|juin|juillet|août|aout|septembre|octobre|novembre|décembre|decembre|Janvier|Février|Fevrier|Mars|Avril|Mai|Juin|Juillet|Août|Aout|Septembre|Octobre|Novembre|Décembre|Decembre)\b"

# Compile each pattern separately with the IGNORECASE flag
date_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in date_patterns]


def detect_dates(text):
    dates = []
    for pattern in date_patterns:
        matches = re.findall(pattern, text)
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

    # Iterate over each token in the document 'doc'
    for token in doc:

        # Iterate over each skill in the 'skills_list'
        for skill in skills_list:

            # Check if the 'skill' and the 'token' have a similarity greater than 65%
            if fuzz.ratio(skill.lower(), token.text.lower()) > 70:

                # Add the detected skill to the 'skills_detected' dictionary with a level "Not specified"
                skills_detected[skill] = "Non spécifié"

                # Define a context window around the current token (7 tokens before and 8 after)
                context_window = doc[max(0, token.i - 7) : token.i + 8]

                # Iterate over skill levels and associated keywords in 'skill_levels'
                for level, keywords in skill_levels.items():

                    # Iterate over each keyword associated with a skill level
                    for keyword in keywords:

                        # Check if any keyword in the context window has a similarity greater than 80%
                        if any(
                            fuzz.ratio(keyword, t.text.lower()) > 80
                            for t in context_window
                        ):

                            # Find the indices of tokens in the context window corresponding to the keyword
                            keyword_index = [
                                t.i
                                for t in context_window
                                if fuzz.ratio(keyword, t.text.lower()) > 70
                            ]

                            # If a keyword is found in the context window and it is within 7 positions of the current token
                            if keyword_index and abs(keyword_index[0] - token.i) <= 7:

                                # Update the detected skill level for this skill
                                skills_detected[skill] = level
                                break  # Exit the keyword loop once the skill level is detected

    return skills_detected


def detect_profession(text):
    """
    Detect the main profession in a given text.

    :param text: str (text to analyze)
    :return: tuple (main profession detected, confidence level)
    """

    doc = nlp(text)
    professions = {}

    # Iterate over each token in the document 'doc'
    for token in doc:

        # Iterate over each profession in the 'professions_list'
        for profession in professions_list:

            # Check if the 'profession' and the 'token' have a similarity greater than 70%
            if fuzz.ratio(profession.lower(), token.text.lower()) > 70:

                # Add the detected profession to the 'professions' dictionary with a confidence level
                professions[profession] = fuzz.ratio(
                    profession.lower(), token.text.lower()
                )

    # Sort professions by descending order of confidence
    sorted_professions = sorted(professions.items(), key=lambda x: x[1], reverse=True)

    # Return the main profession with the highest confidence level
    return sorted_professions[0] if sorted_professions else None


def get_main_skill(skills):
    if not skills:
        return None
    # Sort by order of appearance or confidence level
    sorted_skills = sorted(skills.items(), key=lambda x: len(x[1]), reverse=True)
    return sorted_skills[0]


def detect_acronyms_and_definitions(text):
    acronyms_detected = {}

    for acronym, definition in acronyms_dict.items():
        patterns = [
            rf"\b{re.escape(acronym)}\b",  # Acronym alone
            rf"{re.escape(acronym)}\s*\({re.escape(definition)}\)",  # Acronym followed by definition in parentheses
            rf"\b{re.escape(definition)}\b",  # Definition alone
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)

            if matches:
                acronyms_detected[acronym] = definition
                break  # Stop searching for this acronym if it has already been found

    return acronyms_detected


def structure_query(query):
    """
    Process a user query to extract entities and structure it.

    :param query: str (user query)
    :return: str (query structured with extracted entities)
    """

    doc = nlp(query)

    # Extract entities
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
            if (
                ent.text not in skills_list
                and ent.text not in acronyms_with_definitions
            ):
                location = ent.text
        elif ent.label_ == "DATE":
            dates.append(ent.text)

    # Extract months from the text
    month_matches = re.findall(month_pattern, query.lower())
    months.extend(month_matches)

    # Sort dates and identify start and end dates
    dates = sorted(dates)
    start_date = dates[0] if dates else "Not specified"
    end_date = dates[1] if len(dates) > 1 else "Not specified"

    # Create a list to record values
    values = []

    # Add values from person_names if any
    if person_names:
        values.extend(person_names)

    # Add the value of location if specified
    if location:
        values.append(location)

    # Add values from dates if any
    if dates:
        values.extend(dates)

    if start_date != "Not specified" and end_date != "Not specified":
        values.append(f"from {start_date} to {end_date}")

    # Add values from months if any
    if months:
        values.extend(months)

    # Add the value of skill_with_levels if any
    if skills_with_levels:
        values.extend(skills_with_levels.keys())

    # Add values from acronyms_with_definitions if any
    if acronyms_with_definitions:
        values.extend(acronyms_with_definitions.keys())

    # Convert the list to a comma-separated string
    values_str = ", ".join(values)

    # Display the values extracted from the query
    if values_str == "" or not values_str:
        return query
    return values_str
