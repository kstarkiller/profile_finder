import re
import time

def response_generator(response):
    response = "Assistant : " + response
    lines = response.splitlines(True)  # Conserve les retours à la ligne
    table_pattern = re.compile(r'^\|.*\|$')  # Motif pour détecter les lignes de tableau Markdown

    buffer = []
    # in_table = False

    for line in lines:
        # Vérifier que la ligne commence par '|' et se termine par '|'
        if table_pattern.match(line):
            # Si une ligne de tableau est détectée, ajouter au tampon
            buffer.append(line)
            # in_table = True
        else:
            if not table_pattern.match(line) and buffer:
                # Si la fin du tableau est atteinte, émettre le tableau complet suivi d'un retour à la ligne
                yield ''.join(buffer) + '\n'
                buffer = []
                # in_table = False

            # Émettre les mots ligne par ligne pour le texte normal
            words = line.split()
            for i, word in enumerate(words):
                yield word + (' ' if i < len(words) - 1 else '\n')
                time.sleep(0.05)

    # Émettre tout contenu restant dans le tampon (dernier tableau)
    if buffer:
        yield ''.join(buffer)