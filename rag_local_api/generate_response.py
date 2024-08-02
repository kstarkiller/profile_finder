import ollama

# Generating a response
def generate_response(data, question, model="llama3.1:8b"):
    '''
    Generates a response using the model of your choice (llama3.1 8B here).
    
    Args:
        data (str): The data to use for the response.
        question (str): The question to respond to.

    Returns:
        str: The generated response.
    '''
    output = ollama.generate(
        model=model,
        prompt=f"""Using this data: {data}, respond to this prompt: {question}.
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        Use three sentences maximum and keep the answer as concise as possible."""
    )

    return output['response']