# ============================================================================
# SCRIPT DE MIGRATION : CSV → MongoDB
# ============================================================================
# Ce script migre des données médicales depuis un fichier CSV vers MongoDB.
# Auteur : DataSoluTech
# Date : Janvier 2026
# ============================================================================


# ============================================================================
# IMPORTS : Bibliothèques nécessaires
# ============================================================================

import pandas as pd
# pandas (pd) : Bibliothèque pour manipuler des données tabulaires (CSV, Excel, etc.)
# C'est l'outil principal pour lire et transformer des fichiers CSV

from pymongo import MongoClient, ASCENDING
# pymongo : Bibliothèque officielle pour connecter Python à MongoDB
# - MongoClient : Classe pour créer une connexion à MongoDB
# - ASCENDING : Constante pour créer des index triés par ordre croissant

from datetime import datetime
# datetime : Module Python pour manipuler les dates et heures
# Utilisé ici pour ajouter des timestamps (horodatages) à nos documents

import logging
# logging : Module pour afficher des messages informatifs pendant l'exécution
# Permet de suivre la progression du script et de déboguer en cas d'erreur


# ============================================================================
# CONFIGURATION DU LOGGING : Afficher des messages pendant l'exécution
# ============================================================================

logging.basicConfig(
    level=logging.INFO,  # Niveau INFO : affiche les messages informatifs (pas juste les erreurs)
    format='%(asctime)s - %(levelname)s - %(message)s'
    # Format : [Date/Heure] - [Niveau] - [Message]
    # Exemple : 2026-01-13 19:30:15 - INFO - Connexion réussie!
)
logger = logging.getLogger(__name__)
# Crée un objet "logger" qu'on utilisera pour afficher des messages avec logger.info()


# ============================================================================
# FONCTION PRINCIPALE DE MIGRATION
# ============================================================================

def migrate_data():
    """
    Fonction principale qui orchestre toute la migration.
    
    Étapes :
    1. Se connecter à MongoDB
    2. Charger le fichier CSV
    3. Valider les données
    4. Transformer les données (dates, structure)
    5. Supprimer les anciennes données (si on refait la migration)
    6. Insérer les nouvelles données
    7. Créer des index pour accélérer les recherches
    8. Vérifier que tout s'est bien passé
    """
    
    # ========================================================================
    # ÉTAPE 1 : CONNEXION À MONGODB
    # ========================================================================
    
    logger.info("🔌 Connexion à MongoDB...")
    
    # MongoClient crée une connexion à MongoDB
    # "mongodb://localhost:27017/" signifie :
    # - mongodb:// → protocole de connexion
    # - localhost → serveur local (ton ordinateur)
    # - 27017 → port par défaut de MongoDB
    client = MongoClient("mongodb://localhost:27017/")
    
    # Sélection de la base de données "healthcare_db"
    # Si elle n'existe pas, MongoDB la créera automatiquement
    db = client["healthcare_db"]
    
    # Sélection de la collection "patients" (équivalent d'une "table" en SQL)
    # Si elle n'existe pas, MongoDB la créera automatiquement
    collection = db["patients"]
    
    logger.info("✅ Connexion réussie!")
    
    
    # ========================================================================
    # ÉTAPE 2 : CHARGEMENT DU FICHIER CSV
    # ========================================================================
    
    logger.info("📂 Chargement du fichier CSV...")
    
    # pandas.read_csv() lit le fichier CSV et le convertit en DataFrame
    # Un DataFrame est comme un tableau Excel en Python
    # Chaque ligne = un patient, chaque colonne = une information (nom, âge, etc.)
    # CORRECTION : "../data/" pour remonter d'un niveau depuis le dossier scripts/
    df = pd.read_csv("../data/healthcare_dataset.csv")
    
    # len(df) compte le nombre de lignes (= nombre de patients)
    logger.info(f"✅ {len(df)} enregistrements chargés")
    
    
    # ========================================================================
    # ÉTAPE 3 : VALIDATION DES DONNÉES
    # ========================================================================
    
    logger.info("🔍 Validation des données...")
    
    # Affiche la liste des colonnes du CSV pour vérifier qu'on a tout
    # Exemple : ['Name', 'Age', 'Gender', 'Blood Type', ...]
    logger.info(f"   Colonnes: {list(df.columns)}")
    
    # Compte le nombre total de valeurs manquantes dans tout le DataFrame
    # df.isnull() → identifie les cellules vides
    # .sum().sum() → additionne tout
    logger.info(f"   Valeurs manquantes: {df.isnull().sum().sum()}")
    
    # Compte le nombre de lignes en double (patients identiques)
    # df.duplicated() → identifie les doublons
    # .sum() → compte combien il y en a
    logger.info(f"   Doublons: {df.duplicated().sum()}")
    
    
    # ========================================================================
    # ÉTAPE 4 : TRANSFORMATION DES DONNÉES
    # ========================================================================
    
    logger.info("🔄 Transformation des données...")
    
    # Conversion des colonnes de dates en objets datetime
    # Par défaut, pandas lit les dates comme du texte (string)
    # pd.to_datetime() les convertit en vraies dates manipulables
    df['Date of Admission'] = pd.to_datetime(df['Date of Admission'])
    df['Discharge Date'] = pd.to_datetime(df['Discharge Date'])
    
    # Conversion du DataFrame en liste de dictionnaires
    # 'records' signifie : chaque ligne devient un dictionnaire
    # Exemple : {'Name': 'Bobby Jackson', 'Age': 30, 'Gender': 'Male', ...}
    # C'est le format attendu par MongoDB
    documents = df.to_dict('records')
    
    # Ajout de timestamps (horodatages) à chaque document
    # created_at : date de création du document dans MongoDB
    # updated_at : date de dernière modification (même valeur au début)
    # datetime.utcnow() : date/heure actuelle en temps universel (UTC)
    for doc in documents:
        doc['created_at'] = datetime.utcnow()
        doc['updated_at'] = datetime.utcnow()
    
    logger.info(f"✅ {len(documents)} documents prêts")
    
    
    # ========================================================================
    # ÉTAPE 5 : SUPPRESSION DES ANCIENNES DONNÉES
    # ========================================================================
    
    # Si on relance le script plusieurs fois, on supprime d'abord les anciennes données
    # collection.delete_many({}) : supprime tous les documents (le {} vide = "tout")
    # Comme un "TRUNCATE TABLE" en SQL
    collection.delete_many({})
    logger.info("🗑️ Anciennes données supprimées")
    
    
    # ========================================================================
    # ÉTAPE 6 : INSERTION DANS MONGODB
    # ========================================================================
    
    logger.info("💾 Insertion dans MongoDB...")
    
    # insert_many() insère plusieurs documents en une seule opération
    # C'est beaucoup plus rapide que d'insérer un par un
    # result contient des infos sur l'insertion (IDs générés, etc.)
    result = collection.insert_many(documents)
    
    # result.inserted_ids : liste des IDs MongoDB générés automatiquement
    # On compte combien il y en a pour vérifier que tout est inséré
    logger.info(f"✅ {len(result.inserted_ids)} documents insérés!")
    
    
    # ========================================================================
    # ÉTAPE 7 : CRÉATION DES INDEX
    # ========================================================================
    
    logger.info("📇 Création des index...")
    
    # Un INDEX accélère les recherches sur un champ spécifique
    # C'est comme un sommaire dans un livre : au lieu de lire tout le livre
    # pour trouver un chapitre, on regarde le sommaire
    #
    # ASCENDING : tri croissant (A→Z, 0→9, dates anciennes→récentes)
    #
    # On crée des index sur les champs qu'on utilisera souvent pour filtrer :
    
    collection.create_index([("Name", ASCENDING)])
    # Accélère : db.patients.find({"Name": "Bobby Jackson"})
    
    collection.create_index([("Medical Condition", ASCENDING)])
    # Accélère : db.patients.find({"Medical Condition": "Diabetes"})
    
    collection.create_index([("Hospital", ASCENDING)])
    # Accélère : db.patients.find({"Hospital": "Smith PLC"})
    
    collection.create_index([("Date of Admission", ASCENDING)])
    # Accélère : db.patients.find({"Date of Admission": {$gte: date}})
    
    logger.info("✅ Index créés!")
    
    
    # ========================================================================
    # ÉTAPE 8 : VÉRIFICATION FINALE
    # ========================================================================
    
    logger.info("✔️ Vérification finale...")
    
    # Compte le nombre total de documents dans la collection
    # Doit correspondre au nombre de lignes du CSV
    count = collection.count_documents({})
    logger.info(f"✅ Total dans MongoDB: {count} documents")
    
    # Récupère UN document au hasard pour l'afficher en exemple
    # find_one() sans filtre retourne le premier document trouvé
    sample = collection.find_one()
    logger.info(f"📄 Exemple de document: {sample['Name']}, {sample['Age']} ans")
    
    # Fermeture de la connexion MongoDB
    # Bonne pratique : toujours fermer les connexions pour libérer les ressources
    client.close()
    
    logger.info("🎉 MIGRATION TERMINÉE AVEC SUCCÈS!")


# ============================================================================
# POINT D'ENTRÉE DU SCRIPT
# ============================================================================

if __name__ == "__main__":
    # Cette ligne signifie : "Si on exécute CE fichier directement"
    # (pas si on l'import dans un autre fichier)
    # Alors on lance la fonction migrate_data()
    migrate_data()
