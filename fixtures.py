import pandas as pd
from faker import Faker
import random

# Initialiser Faker
fake = Faker()

# Liste des compétences IT spécifiques
it_competences = [
    'Python Development', 'Java Development', 'Web Development', 'Data Analysis', 
    'Machine Learning', 'Cloud Computing', 'DevOps', 'Cybersecurity', 
    'Database Management', 'Network Administration', 'Software Testing', 
    'Mobile Development', 'IT Support', 'Project Management', 'Business Analysis'
]

# Lire les données existantes à partir du fichier CSV
existing_data = pd.read_csv('Coaff_v1_cleaned.csv')

# Renommer la colonne 'Membres' en 'Nom'
if 'Membres' in existing_data.columns:
    existing_data.rename(columns={'Membres': 'Nom'}, inplace=True)

# Générer de nouvelles données
def generate_fake_data(n):
    fake_data = []
    for _ in range(n):
        row = {
            'Localisation': random.choice(['Mtp', 'Tours', 'Paris']),
            'COEFF_F212': random.choice([100, 105, 115, 150, 170]),
            'PROFIL': random.choice(['Junior', 'Confirmé', 'Expert']),
            'Nom': fake.name(),
            'Missions_en_cours': fake.company(),
            'Competences': random.choice(it_competences),
            'Date_Demarrage': fake.date_between(start_date='-2y', end_date='today').strftime('%Y-%m-%d'),
            'Date_de_fin': fake.date_between(start_date='today', end_date='+2y').strftime('%Y-%m-%d'),
            'Tx_occup': round(random.uniform(0.1, 1.0), 2),
            'Stream_BT': random.choice(['DSIA', 'SSIS', 'MSBI', 'TALEND', 'ODI']),
        }
        fake_data.append(row)
    return pd.DataFrame(fake_data)

# Nombre de nouvelles lignes à ajouter
num_new_rows = 500
new_data = generate_fake_data(num_new_rows)

# Ajouter les nouvelles données aux données existantes
combined_data = pd.concat([existing_data, new_data], ignore_index=True)

# Vérifiez à nouveau que la colonne 'Nom' est présente
if 'Membres' in combined_data.columns:
    combined_data.rename(columns={'Membres': 'Nom'}, inplace=True)

# Enregistrer le résultat dans un nouveau fichier CSV
combined_data.to_csv('combined_data.csv', index=False)

print(f"Ajout de {num_new_rows} nouvelles lignes de données.")
