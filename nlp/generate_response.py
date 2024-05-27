import ollama

# Fonction pour générer une réponse
def generate_response(embed_question, embed_documents):
    """
    Génère une réponse à partir d'une question et d'une liste de documents.

    Args:
        embed_question (str): La question posée embédée.
        embed_documents (list): Une liste de documents embédés.

    Returns:
        str: La réponse générée.
    """
    prompt = f"""Use the following pieces of context to answer the question at the end.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    Use two sentences maximum and keep the answer as concise as possible. It is useless to provide all the context, only the relevant parts.
    Context: {embed_documents}
    Question: {embed_question}"""

    messages = [
        {
            'role': 'user',
            'content': prompt,
        },
    ]

    # response = ollama.generate(model='phi3', prompt=prompt)
    
    for part in ollama.chat('mistral', messages=messages, stream=True):
        print(part['message']['content'], end='', flush=True)

    # return response['response']