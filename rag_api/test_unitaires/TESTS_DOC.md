# Documentation des Tests Automatisés
Cette documentation fournit des directives sur l'installation de l'environnement de test, les dépendances nécessaires et la procédure d'exécution des tests automatisés pour le projet d'intelligence artificielle.

## Procédure d’Installation de l’Environnement de Test
Pour préparer l'environnement de test, suivez les étapes suivantes :

- Étape 1 : Installer Python
Assurez-vous d'avoir Python 3.9.11 installée sur votre machine. Vous pouvez télécharger Python depuis le site officiel : python.org.

- Étape 2 : Créer un Environnement Virtuel
Il est recommandé d'utiliser un environnement virtuel pour isoler les dépendances du projet. Suivez ces instructions :
```bash
# Créer l'environnemennt
conda create votre-environnement

# Activer l'environnement
conda activate votre-environnement
```

- Étape 3 : Installer les Dépendances
Une fois l'environnement virtuel activé, installez les dépendances requises. Un fichier requirements.txt devrait être présent dans le répertoire du projet, listant toutes les bibliothèques nécessaires.
```bash
# Installer les dépendances
pip install -r requirements.txt
```

## Dépendances Installées
Voici la liste des bibliothèques installées :
```py
Faker==26.0.0
openpyxl==3.1.5
pandas==2.2.2
openai==1.25.0
ollama==0.3.3
chromadb==0.4.13
streamlit==1.39.0
streamlit-authenticator==0.3.3 
unittest2==1.1.0
spacy==3.7.2
fuzzywuzzy==0.18.0
python-levenshtein==0.26.0
sqlalchemy==2.0.35 
psycopg2==2.9.9
openlit==1.26.0
requests==2.32.3
beautifulsoup4==4.12.3
bs4==0.0.2
pyarrow==17.0.0
mlflow==2.17.1
pymongo==4.10.1
python-multipart==0.0.17
passlib==1.7.4
python-jose==3.3.0
```

## Procédure d’Exécution des Tests
- Étape 1 : Activation de l’Environnement Virtuel
Avant d'exécuter les tests, assurez-vous que l'environnement virtuel est activé (voir Étape 2 de la procédure d’installation).

- Étape 2 : Exécution des Tests
Pour exécuter les tests, ouvrez un terminal dans le répertoire principal du projet et utilisez la commande suivante :
```bash
python -m unittest discover -s test_unitaires
```
Cette commande recherchera et exécutera tous les fichiers de test situés dans le répertoire test_unitaires.

- Étape 3 : Vérification de la Couverture des Tests
Pour évaluer la couverture des tests, vous pouvez utiliser coverage.py. Suivez ces étapes :

```bash
# Installer Coverage
pip install coverage

# Exécutez les tests avec couverture :
coverage run -m unittest discover -s test_unitaires

# Générez un rapport de couverture :
coverage report

# (Optionnel) Pour visualiser un rapport HTML :
coverage html
# Ouvrez ensuite le fichier htmlcov/index.html dans votre navigateur pour une vue détaillée de la couverture des tests.
```