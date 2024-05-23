import os
import ollama
import textract
import time

def load_documents(file_path):
    """
    Charge les documents à partir du chemin spécifié.
    De nombreux types de fichiers sont supportés :
    .doc, .docx, .eml, .epub, .gif, .jpg, .json, .html, .png, .pdf, .pptx, .ps, .rtf, .tiff, .txt, .xlsx, .xls, etc.

    Args:
        file_path (str): Le chemin vers le répertoire contenant les fichiers.

    Returns:
        list: Une liste de tuples contenant le nom du fichier et son contenu.
    """
    documents = []
    for filename in os.listdir(file_path):
        try:
            file_content = textract.process(os.path.join(file_path, filename))
            documents.append((filename, file_content.decode('utf-8')))
        except textract.exceptions.ExtensionNotSupported as e:
            print(f"Le fichier {filename} a une extension non supportée.")
    return documents

# Fonction pour générer une réponse
def generate_response(question, documents):
    """
    Génère une réponse à partir d'une question et d'une liste de documents.

    Args:
        question (str): La question posée.
        documents (list): Une liste de documents.

    Returns:
        str: La réponse générée.
    """
    prompt = f'Analyse {documents[0][1]} and brievely answer {question}\n\n'

    # response = ollama.generate(model='phi3', prompt=prompt)
    
    for part in ollama.generate(model='llama3', prompt=prompt, stream=True):
        print(part['response'], end='', flush=True)

    # return response['response']

# Chargement des documents
start_time = time.time()
documents = load_documents(r"C:\Users\k.simon\Desktop\test_loads")
end_time = time.time()
print(f"Documents chargés en {end_time - start_time} secondes.\n\n")
# print(f"Chargement des documents : {documents[0][1]}\n\n")

# Prompt pour avoir la question
question = input("Enter your question: ")

# Génération de la réponse
start_time = time.time()
response = generate_response(question, documents)
end_time = time.time()
print(f"\nRéponse générée en {end_time - start_time} secondes.\n\n")

# print(response)