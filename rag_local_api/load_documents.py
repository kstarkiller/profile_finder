import os
import textract
import openpyxl

DOC_PATH = r"C:\Users\k.simon\Projet\avv-matcher\rag_local_api\sources"

def load_documents(file_path):
    '''
    Loads the documents from the specified file path.

    Args:
        file_path (str): The path to the directory containing the documents.

    Returns:
        list: A list of documents.
    '''
    documents = []
    for filename in os.listdir(file_path):
        try:
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext == '.xlsx':
                workbook = openpyxl.load_workbook(os.path.join(file_path, filename))
                sheet = workbook.active
                file_content = "\n".join(["\t".join([str(cell.value) for cell in row]) for row in sheet.iter_rows()])
                documents.append(file_content)
            else:
                file_content = textract.process(os.path.join(file_path, filename))
                documents.append(file_content.decode('utf-8'))

        except textract.exceptions.ExtensionNotSupported as e:
            print(f"Le fichier {filename} a une extension non supportée.")

    return documents