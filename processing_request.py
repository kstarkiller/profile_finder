import os
from pprint import pprint
from openai import AzureOpenAI
from config import AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, DEPLOYMENT_LLM
from similarity_search import find_profiles

model = DEPLOYMENT_LLM

# Initialiser le client AzureOpenAI
client = AzureOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY,
    api_version="2024-02-01",
)


def process_input(user_input, chat_history):
    # Validation de l'entrée utilisateur
    if not user_input[-1]["query"].strip():
        return "Please enter a valid input.", chat_history[1:]

    if len(user_input[-1]) > 1:
        user_query = (
            str(user_input[-1]["context"]) + ", " + str(user_input[-1]["query"])
        )
    else:
        user_query = str(user_input[-1]["query"])

    # Prétraitement de l'entrée utilisateur
    profiles = find_profiles(user_query)
    # Convertir les profils en string
    profiles = [str(profile) for profile in profiles]

    # Ajouter les profils au prompt et conditionner le prompt
    # selon si c'est le premier message de la conversation ou non
    prompt_with_profiles = (
        f"Using those datas: {profiles}, "
        f"{'respond to this prompt' if len(chat_history) == 1 else 'continue the conversation by replying to this prompt'}: {user_input}."
    )

    # Ajouter la nouvelle entrée utilisateur à l'historique
    chat_history.append({"role": "user", "content": prompt_with_profiles})

    # Créer une requête de complétion de chat en utilisant le client Azure OpenAI
    try:
        completion = client.chat.completions.create(
            model=DEPLOYMENT_LLM, messages=chat_history
        )

        # Récupérer la réponse du modèle
        if hasattr(completion, "choices") and len(completion.choices) > 0:
            first_choice = completion.choices[0]
            if hasattr(first_choice, "message") and hasattr(
                first_choice.message, "content"
            ):
                response = first_choice.message.content
                # Ajouter la réponse du chatbot à l'historique
                chat_history.append({"role": "assistant", "content": response})

                # Conserver uniquement les 10 dernières paires (utilisateur-chatbot) ainsi que le contexte de départ (system)
                if len(chat_history) > 10:
                    chat_history = chat_history[0] + chat_history[-10:]

                return response, chat_history
            else:
                raise AttributeError("First choice message has no 'content' attribute")
        else:
            raise AttributeError(
                "'choices' attribute missing or empty in completion object"
            )

    except Exception as e:
        print(f"An error occurred: {e}")
        return "An error occurred while processing the input.", chat_history


# user_input = "Donne-moi le taux d'occupation de Afrodille Pouliotte en juillet 2024"
# chat_history = []

# process_input(user_input, chat_history)
