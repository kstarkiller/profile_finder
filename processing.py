import os
from pprint import pprint
from openai import AzureOpenAI
from config import AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, DEPLOYMENT
from embedding import find_profiles


def extract_name(user_input):
    keywords = [
        "je cherche",
        "un professionnel",
        "un profil",
        "un membre",
        "dont le nom est",
        "nom est",
        "qui s'appelle",
        "qui est :",
        "un expert",
        "un junior",
        "un confirmé",
    ]
    for keyword in keywords:
        if keyword in user_input:
            # Suppression du mot clé et de tout avant
            user_input = user_input.split(keyword, 1)[-1]
            break
    return user_input.strip()


def extract_skills(user_input):
    keywords = [
        "compétences en",
        "compétences suivantes",
        "les compétences sont",
        "compétences sont",
        "qui a des compétences en",
        "expert en",
        "spécialiste en",
        "compétences :",
        "juniors en",
        "confirmés en",
    ]
    for keyword in keywords:
        if keyword in user_input:
            # Suppression du mot clé et de tout avant
            user_input = user_input.split(keyword, 1)[-1]
            break
    return user_input.strip()


# Initialiser le client AzureOpenAI
client = AzureOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY,
    api_version="2024-02-01",
)


def process_input(user_input, chat_history):
    """
    Fonction pour traiter l'entrée de l'utilisateur avec l'historique de la conversation.
    """
    # Contexte du chatbot
    starting_content = """You are a chatbot assistant that helps users to find members of a team based on their skills, names, experiences or availability.
    Use three sentences maximum for each of your answer and keep the answer as concise as possible.
    If you don't know the answer, just say that you don't know, don't try to make up an answer."""

    chat_history = [{"role": "system", "content": starting_content}]

    # Validation de l'entrée utilisateur
    if not user_input.strip():
        return "Please enter a valid input.", chat_history[1:]

    # Ajouter la nouvelle entrée utilisateur à l'historique
    chat_history.append({"role": "user", "content": user_input})
    pprint(f"Chat history after user input: {chat_history}")

    # # Détecter les noms dans la requête utilisateur
    # detected_names = extract_name(user_input)
    # pprint(f"Noms détectés : {detected_names}")

    # # Détecter les compétences dans la requête utilisateur
    # detected_skills = extract_skills(user_input)
    # pprint(f"Compétences détectées : {detected_skills}")

    # # Utiliser le premier nom détecté pour la recherche
    # if detected_names:
    #     extracted_name = detected_names
    # else:
    #     extracted_name = user_input  # Si aucun nom n'est détecté, utiliser l'entrée complète

    # Trouver les profils correspondants en utilisant le nom extrait
    profiles = find_profiles(extracted_name)
    profiles_text = "\n\n".join(profiles)
    pprint(f"Profiles text: {profiles_text}")

    # Ajouter les profils au prompt et conditionner le prompt
    # selon si c'est le premier message de la conversation ou non
    prompt_with_profiles = (
        f"Using those profiles: {profiles_text}, "
        f"{'respond to this prompt' if len(chat_history) == 1 else 'continue the conversation by replying to this prompt'}: {user_input}."
    )

    print(f"Prompt with profiles: {prompt_with_profiles}")

    # Créer une requête de complétion de chat en utilisant le client Azure OpenAI
    # pprint(f"Chat history before completion: {chat_history}")
    # try:
    #     completion = client.chat.completions.create(
    #         model=DEPLOYMENT,
    #         messages=chat_history
    #     )
    #     pprint(f"Completion response: {completion}")

    #     # Récupérer la réponse du modèle
    #     if hasattr(completion, 'choices') and len(completion.choices) > 0:
    #         first_choice = completion.choices[0]
    #         if hasattr(first_choice, 'message') and hasattr(first_choice.message, 'content'):
    #             response = first_choice.message.content
    #             # Ajouter la réponse du chatbot à l'historique
    #             chat_history.append({"role": "assistant", "content": response})
    #             pprint(f"Chat history after bot response: {chat_history}")

    #             # Conserver uniquement les 10 dernières paires (utilisateur-chatbot) ainsi que le contexte de départ (system)
    #             if len(chat_history) > 10:
    #                 chat_history = chat_history[0] + chat_history[-10:]

    #             pprint(f"Chat history after trimming: {chat_history}")

    #             return response, chat_history[1:]
    #         else:
    #             raise AttributeError("First choice message has no 'content' attribute")
    #     else:
    #         raise AttributeError("'choices' attribute missing or empty in completion object")

    # except Exception as e:
    #     print(f"An error occurred: {e}")
    #     return "An error occurred while processing the input.", chat_history
