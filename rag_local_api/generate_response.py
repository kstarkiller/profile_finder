import ollama

# Generating a response
def generate_response(data, question):
    '''
    Generates a response using the llama3/Mistral/Aya/Phi3 model.
    
    Args:
        data (str): The data to use for the response.
        question (str): The question to respond to.

    Returns:
        str: The generated response.
    '''
    output = ollama.generate(
        model="aya",
        prompt=f"""Using this data: {data}, respond to this prompt: {question}.
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        Use three sentences maximum and keep the answer as concise as possible."""
        # Don't forget to format dates in the format 'DD-MM-YYYY'."""
    )

    return output['response']