
import certifi
import ssl
import requests

print("Chemin vers les certificats CA de certifi:", certifi.where())

# Configurer le contexte SSL pour utiliser les certificats CA de certifi
ssl_context = ssl.create_default_context(cafile=certifi.where())

# Effectuer une requête HTTP avec requests en utilisant les certificats CA de certifi
try:
    response = requests.get('https://example.com', verify=certifi.where())
    print("Requête réussie !")
    print(response.content)
except requests.exceptions.SSLError as e:
    print("Erreur SSL :", e)
except Exception as e:

    print("Autre erreur :", e)