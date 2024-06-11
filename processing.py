import os
from openai import AzureOpenAI
from config import AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, DEPLOYMENT

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

    # Ajouter la nouvelle entrée utilisateur à l'historique
    chat_history.append({"role": "user", "content": user_input})

    # Créer une requête de complétion de chat en utilisant le client Azure OpenAI
    try:
        completion = client.chat.completions.create(
            model=DEPLOYMENT,
            messages=chat_history
        )

        # Imprimer l'objet completion pour voir sa structure
        print(completion)

        # Récupérer la réponse du modèle
        if hasattr(completion, 'choices') and len(completion.choices) > 0:
            first_choice = completion.choices[0]
            if hasattr(first_choice, 'message') and hasattr(first_choice.message, 'content'):
                response = first_choice.message.content
                # Ajouter la réponse du chatbot à l'historique
                chat_history.append({"role": "assistant", "content": response})

                # Conserver uniquement les cinq dernières paires (utilisateur-chatbot)
                if len(chat_history) > 10:
                    chat_history = chat_history[-10:]

                return response, chat_history
            else:
                raise AttributeError("First choice message has no 'content' attribute")
        else:
            raise AttributeError("'choices' attribute missing or empty in completion object")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return "An error occurred while processing the input.", chat_history










# import os
# from openai import AzureOpenAI
# from config import AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, DEPLOYMENT

# # Initialiser le client AzureOpenAI
# client = AzureOpenAI(
#     azure_endpoint=AZURE_OPENAI_ENDPOINT,
#     api_key=AZURE_OPENAI_API_KEY,
#     api_version="2024-02-01",
# )
# import os
# from openai import AzureOpenAI
# from config import AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, DEPLOYMENT

# # Initialiser le client AzureOpenAI
# client = AzureOpenAI(
#     azure_endpoint=AZURE_OPENAI_ENDPOINT,
#     api_key=AZURE_OPENAI_API_KEY,
#     api_version="2024-02-01",
# )

# def process_input(user_input, chat_history):

#     """
#     Fonction pour traiter l'entrée de l'utilisateur avec l'historique de la conversation.
#     """

#     # Ajouter la nouvelle entrée utilisateur à l'historique
#     chat_history.append({"role": "user", "content": user_input})

#     # Simuler une réponse en utilisant l'historique pour les tests
#     response = f"Prouta. Number: {user_input, len(chat_history)}"

#     # Ajouter la réponse du chatbot à l'historique
#     chat_history.append({"role": "assistant", "content": response})

#     # Conserver uniquement les cinq dernières paires (utilisateur-chatbot)
#     if len(chat_history) > 10:
#         chat_history = chat_history[-10:]

#     return response, chat_history


