import os
# from openai import AzureOpenAI
# from config import AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, DEPLOYMENT

# # Initialiser le client AzureOpenAI
# client = AzureOpenAI(
#     azure_endpoint=AZURE_OPENAI_ENDPOINT,
#     api_key=AZURE_OPENAI_API_KEY,
#     api_version="2024-02-01",
# )

def process_input(user_input, response_counter):

    """
    Fonction pour traiter l'entrée de l'utilisateur.
    Pour les tests, nous renvoyons un texte prédéfini au lieu d'appeler l'API Azure OpenAI.
    """

    # Créer une requête de complétion de chat

    # Crée une requête de complétion de chat en utilisant le client Azure OpenAI
    # completion = client.chat.completions.create(
    #     # Spécifie le modèle de déploiement à utiliser pour la complétion
    #     model=DEPLOYMENT,
    #     # Définit les messages qui constituent le contexte de la conversation
    #     messages=[
    #         {
    #             # Indique que ce message provient de l'utilisateur
    #             "role": "user",
    #             # Contenu du message utilisateur à envoyer au modèle
    #             "content": user_input,
    #         }
    #     ]
    # )
    # # Imprimer l'objet completion pour voir sa structure
    # print(completion)

    # Récupérer la réponse du modèle
    # try:
    #     # Vérifier si 'completion' possède l'attribut 'choices' et s'il contient au moins un élément
    #     if hasattr(completion, 'choices') and len(completion.choices) > 0:
    #         # Accéder au premier choix de la liste 'choices'
    #         first_choice = completion.choices[0]
    #         # Vérifier si 'first_choice' possède l'attribut 'message' et si 'message' possède l'attribut 'content'
    #         if hasattr(first_choice, 'message') and hasattr(first_choice.message, 'content'):
    #             # Récupérer le contenu du message de la première option
    #             response = first_choice.message.content
    #             return response
    #         else:
    #             # Lever une erreur si 'message' n'a pas l'attribut 'content'
    #             raise AttributeError("First choice message has no 'content' attribute")
    #     else:
    #         # Lever une erreur si 'choices' est absent ou vide dans l'objet 'completion'
    #         raise AttributeError("'choices' attribute missing or empty in completion object")
    # except Exception as e:
    #     # Capturer et imprimer l'exception, et retourner un message d'erreur générique
    #     print(f"An error occurred: {e}")
    #     return "An error occurred while processing the input."

    # Retourner un texte prédéfini pour les tests
    response = f"This is a predefined response for testing purposes. Number: {response_counter}"

    return response

