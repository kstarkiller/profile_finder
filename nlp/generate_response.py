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
        model="mistral",
        prompt=f"Using this data: {data}. Respond to this prompt: {question}"
    )

    return output