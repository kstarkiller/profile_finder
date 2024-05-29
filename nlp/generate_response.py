import ollama

# Generating a response
def generate_response(data, question):
    '''
    Generates a response using the llama3 model.
    
    Args:
        data (str): The data to use for the response.
        question (str): The question to respond to.

    Returns:
        str: The generated response.
    '''
    output = ollama.generate(
        model="llama3",
        prompt=f"Using this data: {data}. Respond to this prompt: {question}. Don't forget to format dates in the format 'DD-MM-YYYY'."
    )

    return output['response']