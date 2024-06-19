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
        You are a chatbot assistant that helps users to find members of a team based on their skills, names, or availability.
        Use three sentences maximum for each of your answer and keep the answer as concise as possible.
        If you don't know the answer, just say that you don't know, don't try to make up an answer."""
    )

    return output['response']