import getpass
import ollama

from custom_logging import log_access, log_response
import config

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
    success = (username == config.USERNAME) and (password == config.PASSWORD)
    if success:
        log_access(username, success)  # Log the login attempt
        return success
    else:
        log_access(username, success)  # Log the login attempt
        return success

def validate_input(data, question, model):
    if not authenticate():
        raise ValueError(ERROR_MESSAGES["access_denied"])
    if not data:
        raise ValueError(ERROR_MESSAGES["no_data"])
    if not question or question.isspace():
        raise ValueError(ERROR_MESSAGES["no_question"])
    if len(question) > 512:
        raise ValueError(ERROR_MESSAGES["question_too_long"])
    if model not in ollama.list_models():
        raise ValueError(ERROR_MESSAGES["invalid_model"].format(model, ollama.list_models()))

def generate_response(data, question, model="llama3.1:8b"):
    '''
    Generates a response using the model of your choice (llama3.1 8B here).

    Args:
        data (str): The data to use for the response.
        question (str): The question to respond to.

    Returns:
        str: The generated response.
    '''
    
    try:
        # Validate inputs
        validate_input(data, question, model)
        
        # Generate the response
        output = ollama.generate(
            model=model,
            prompt=f"Using this data: {data}, respond to this prompt: {question}. "
                   "If you don't know the answer, just say that you don't know, don't try to make up an answer. "
                   "Use three sentences maximum and keep the answer as concise as possible."
        )

        response = output['response']
        log_response(question, response)  # Log the asked question and the generated response
        return response

    except Exception as e:  # Capturer toutes les exceptions
        log_response(question, str(e))  # Log the error message
        return str(e)