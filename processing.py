import os
# from openai import AzureOpenAI
# from config import AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, DEPLOYMENT

# # Initialiser le client AzureOpenAI
# client = AzureOpenAI(
#     azure_endpoint=AZURE_OPENAI_ENDPOINT,
#     api_key=AZURE_OPENAI_API_KEY,
#     api_version="2024-02-01",
# )

def process_input(user_input):

    """
    Fonction pour traiter l'entrée de l'utilisateur.
    Pour les tests, nous renvoyons un texte prédéfini au lieu d'appeler l'API Azure OpenAI.
    """

    # Créer une requête de complétion de chat
    # completion = client.chat.completions.create(
    #     model=DEPLOYMENT,
    #     messages=[
    #         {
    #             "role": "user",
    #             "content": user_input,
    #         }
    #     ]
    # )

    # Imprimer l'objet completion pour voir sa structure
    # print(completion)

    # # Récupérer la réponse du modèle
    # try:
    #     # Vérifier si completion est un OpenAIObject
    #     if hasattr(completion, 'choices') and len(completion.choices) > 0:
    #         first_choice = completion.choices[0]
    #         if hasattr(first_choice, 'message') and hasattr(first_choice.message, 'content'):
    #             response = first_choice.message.content
    #             return response
    #         else:
    #             raise AttributeError("First choice message has no 'content' attribute")
    #     else:
    #         raise AttributeError("'choices' attribute missing or empty in completion object")
    # except Exception as e:
    #     print(f"An error occurred: {e}")
    #     return "An error occurred while processing the input."

    # Retourner un texte prédéfini pour les tests
    return "This is a predefined response for testing purposes."

