import os
import getpass
import ollama
import requests
from typing import Optional
from datetime import date

from custom_logging import log_access, log_response

# Import environment variables
USERNAME = os.getenv('RAG_LOCAL_USERNAME')
PASSWORD = os.getenv('RAG_LOCAL_PASSWORD')
API_KEY = os.getenv('RAG_LOCAL_API_KEY')

# Constants for error messages
ERROR_MESSAGES = {
    "access_denied": "Access denied. Invalid credentials.",
    "no_data": "Sorry, no data was provided. I need data to respond to your question. Please provide the data and try again.",
    "no_question": "I don't have a question to respond to. Please provide a valid question.",
    "question_too_long": "The question is too long. Please provide a question with less than 512 characters.",
    "invalid_model": "The model {} is not available. Please choose a valid model from this list: {}"
}

# Authenticate the user
def authenticate():
    '''
    Authenticate the user using the credentials in the config file.

    Returns:
        bool: True if the user is authenticated, False otherwise.
    '''

    # Retrieve user credentials from the config.py file
    username = input("Enter your username: ")
    password = getpass.getpass("Enter your password: ")

    # Check the credentials
    success = (username == USERNAME) and (password == PASSWORD)
    if success:
        log_access(username, success)  # Log the login attempt
        return success
    else:
        log_access(username, success)  # Log the login attempt
        return success


def validate_input(data: str, question: str, model: Optional[str] = None):
    '''
    Valide les données d'entrée, la question et le modèle.

    Args:
        data (str): Les données à utiliser pour la réponse.
        question (str): La question à laquelle répondre.
        model (str): Le modèle à utiliser pour la réponse. Optionnel.

    Raises:
        ValueError: Si les données d'entrée, la question ou le modèle sont invalides.
    '''

    # Authentifier l'utilisateur
    if not authenticate():
        raise ValueError(ERROR_MESSAGES["access_denied"])
    
    # Vérifier si les données sont fournies
    if not data:
        raise ValueError(ERROR_MESSAGES["no_data"])
    
    # Vérifier si la question est vide
    if not question or question.isspace():
        raise ValueError(ERROR_MESSAGES["no_question"])
    
    # Vérifier si la question est trop longue
    if len(question) > 512:
        raise ValueError(ERROR_MESSAGES["question_too_long"])
    
    # Vérifier si l'argument optionnel model est fourni
    if model:
        # Vérifier si le modèle est dans la liste des modèles disponibles
        available_models = ollama.list().get('models', [])
        model_names = [m['name'] for m in available_models]
        if model not in model_names:
            raise ValueError(ERROR_MESSAGES["invalid_model"].format(model, model_names))
        

def generate_ollama_response(data, question, model="llama3.1:8b"):
    '''
    Generates a response using the model of your choice (llama3.1 8B here).

    Args:
        data (str): The data to use for the response.
        question (str): The question to respond to.
        model (str): The model to use for the response.

    Returns:
        str: The generated response.
    '''
    
    try:
        # Validate inputs
        validate_input(data, question, model)

        prompt= f"""
            You are a French chatbot assistant that helps the user find team members based on their location, availability and skills.
            - Format responses as concise and consistently as possible, using headers and tables when necessary. Don't explain what you're doing and summarize the data.
            - Use the current date ({date.today()}) for any time-related questions.
            - For months, consider the nearest future month unless otherwise specified. Don't consider months in the past or months more than 12 months in the futur, unless otherwise specified.
            - Combine occupancy periods and percentages to calculate total availability over a given period.
            - Don't assume anything, don't mess with the data, and only return members that meet the user's criteria.
            - If several members match the criteria, present them in order of relevance (availability, skills, etc.).
            Using this data: {data}, respond to this prompt: {question}.
            """
        
        # Generate the response
        output = ollama.generate(
            model=model,
            prompt=prompt,
        )

        response = output['response']
        log_response(question, response)  # Log the asked question and the generated response
        return response

    except Exception as e:  # Capturer toutes les exceptions
        log_response(question, str(e))  # Log the error message
        return str(e)
    
# Generate a response
def generate_perplexity_response(data, question, model="llama-3.1-70b-instruct"):
    '''
    Generates a response using the Perplexity API.

    Args:
        data (str): The data to use for the response.
        question (str): The question to respond to.
        model (str): The model to use for the response.

    Returns:
        str: The generated response.
    '''
    
    try:
        # Validate inputs
        validate_input(data, question)
        
        # Set up the API request
        url = "https://api.perplexity.ai/chat/completions"
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        context= f"""
            You are a French chatbot assistant that helps the user find team members based on their location, availability and skills.
            - Format responses as concise and consistently as possible, using headers and tables when necessary. Don't explain what you're doing and summarize the data.
            - Use the current date ({date.today()}) for any time-related questions.
            - For months, consider the nearest future month unless otherwise specified. Don't consider months in the past or months more than 12 months in the futur, unless otherwise specified.
            - Combine occupancy periods and percentages to calculate total availability over a given period.
            - Don't assume anything, don't mess with the data, and only return members that meet the user's criteria.
            - If several members match the criteria, present them in order of relevance (availability, skills, etc.).
            """
        
        prompt = f"Using this data: {data}, respond to the user question: {question}."

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": context},
                {"role": "user", "content": prompt}
            ],
            # "max_tokens": 150
        }
        
        # Send the request to the Perplexity API
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an error for bad responses
        
        # Parse the response
        output = response.json()
        generated_response = output['choices'][0]['message']['content']
        
        # Log and return the response
        log_response(question, generated_response)
        return generated_response

    except ValueError as e:
        return str(e)
    
    except Exception as e:  # Capturer toutes les exceptions
        log_response(question, str(e))  # Log the error message
        return "An unexpected error occurred: " + str(e)