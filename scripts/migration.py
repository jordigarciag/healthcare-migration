# ============================================================================
# SCRIPT DE MIGRATION : CSV → MongoDB (VERSION DOCKER)
# ============================================================================
# Ce script migre des données médicales depuis un fichier CSV vers MongoDB.
# Compatible avec Docker et exécution locale.
# Auteur : DataSoluTech
# Date : Janvier 2026
# ============================================================================

# ============================================================================
# IMPORTS : Bibliothèques nécessaires
# ============================================================================
import os
# os : Module pour interagir avec le système d'exploitation
# Utilisé ici pour lire les variables d'environnement et gérer les chemins

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
    level=logging.INFO,  # Niveau INFO : affiche les messages informatifs
    format='%(asctime)s - %(levelname)s - %(message)s'
    # Format : [Date/Heure] - [Niveau] - [Message]
)
logger = logging.getLogger(__name__)

# ============================================================================
# FONCTION PRINCIPALE DE MIGRATION
# ============================================================================
def migrate_data():
    """
    Fonction principale qui orchestre toute la migration.
    
    Étapes :
    1. Se connecter à MongoDB (compatible Docker et local)
    2. Charger le fichier CSV (chemin flexible)
    3. Valider les données
    4. Transformer les données (dates, structure)
    5. Supprimer les anciennes données (si on refait la migration)
    6. Insérer les nouvelles données
    7. Créer des index pour accélérer les recherches
    8. Vérifier que tout s'est bien passé
    9. Démontrer les opérations CRUD (Create, Read, Update, Delete)
    """
    
    # ========================================================================
    # ÉTAPE 1 : CONNEXION À MONGODB (COMPATIBLE DOCKER)
    # ========================================================================
    
    logger.info("🔌 Connexion à MongoDB...")
    
    # Configuration depuis les variables d'environnement
    # os.getenv() lit une variable d'environnement
    # Si elle n'existe pas, utilise la valeur par défaut (2e paramètre)
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    MONGO_DB = os.getenv("MONGO_DB", "healthcare_db")
    
    # MongoClient crée une connexion à MongoDB
    # En Docker : mongodb://admin:admin123@mongodb:27017/
    # En local : mongodb://localhost:27017/
    client = MongoClient(MONGO_URI)
    
    # Sélection de la base de données
    db = client[MONGO_DB]
    
    # Sélection de la collection "patients"
    collection = db["patients"]
    
    logger.info(f"✅ Connexion réussie à {MONGO_URI}")
    logger.info(f"✅ Base de données : {MONGO_DB}")
    
    # ========================================================================
    # ÉTAPE 2 : CHARGEMENT DU FICHIER CSV (CHEMIN FLEXIBLE)
    # ========================================================================
    
    logger.info("📂 Chargement du fichier CSV...")
    
    # Chemin du fichier CSV (compatible Docker et local)
    # Priorité 1 : Variable d'environnement CSV_PATH
    # Priorité 2 : Chemin relatif local ../data/healthcare_dataset.csv
    # Priorité 3 : Chemin Docker data/healthcare_dataset.csv
    csv_path = os.getenv("CSV_PATH", "../data/healthcare_dataset.csv")
    
    # Vérification : si le chemin n'existe pas, essayer le chemin Docker
    if not os.path.exists(csv_path):
        csv_path = "data/healthcare_dataset.csv"
        logger.info(f"   📍 Utilisation du chemin Docker : {csv_path}")
    else:
        logger.info(f"   📍 Utilisation du chemin local : {csv_path}")
    
    # pandas.read_csv() lit le fichier CSV et le convertit en DataFrame
    df = pd.read_csv(csv_path)
    
    logger.info(f"✅ {len(df)} enregistrements chargés")
    
    # ========================================================================
    # ÉTAPE 3 : VALIDATION DES DONNÉES
    # ========================================================================
    
    logger.info("🔍 Validation des données...")
    
    # Affiche la liste des colonnes du CSV
    logger.info(f"   Colonnes: {list(df.columns)}")
    
    # Compte le nombre total de valeurs manquantes
    logger.info(f"   Valeurs manquantes: {df.isnull().sum().sum()}")
    
    # Compte le nombre de lignes en double
    logger.info(f"   Doublons: {df.duplicated().sum()}")
    
    # ========================================================================
    # ÉTAPE 4 : TRANSFORMATION DES DONNÉES
    # ========================================================================
    
    logger.info("🔄 Transformation des données...")
    
    # Conversion des colonnes de dates en objets datetime
    df['Date of Admission'] = pd.to_datetime(df['Date of Admission'])
    df['Discharge Date'] = pd.to_datetime(df['Discharge Date'])
    
    # Conversion du DataFrame en liste de dictionnaires
    documents = df.to_dict('records')
    
    # Ajout de timestamps à chaque document
    for doc in documents:
        doc['created_at'] = datetime.utcnow()
        doc['updated_at'] = datetime.utcnow()
    
    logger.info(f"✅ {len(documents)} documents prêts")
    
    # ========================================================================
    # ÉTAPE 5 : SUPPRESSION DES ANCIENNES DONNÉES
    # ========================================================================
    
    collection.delete_many({})
    logger.info("🗑️ Anciennes données supprimées")
    
    # ========================================================================
    # ÉTAPE 6 : INSERTION DANS MONGODB (CREATE)
    # ========================================================================
    
    logger.info("💾 Insertion dans MongoDB...")
    
    # insert_many() insère plusieurs documents en une seule opération
    result = collection.insert_many(documents)
    
    logger.info(f"✅ {len(result.inserted_ids)} documents insérés!")
    
    # ========================================================================
    # ÉTAPE 7 : CRÉATION DES INDEX
    # ========================================================================
    
    logger.info("📇 Création des index...")
    
    # Un INDEX accélère les recherches sur un champ spécifique
    collection.create_index([("Name", ASCENDING)])
    collection.create_index([("Medical Condition", ASCENDING)])
    collection.create_index([("Hospital", ASCENDING)])
    collection.create_index([("Date of Admission", ASCENDING)])
    
    logger.info("✅ Index créés!")
    
    # ========================================================================
    # ÉTAPE 8 : VÉRIFICATION FINALE (READ)
    # ========================================================================
    
    logger.info("✔️ Vérification finale...")
    
    # Compte le nombre total de documents dans la collection
    count = collection.count_documents({})
    logger.info(f"✅ Total dans MongoDB: {count} documents")
    
    # Récupère UN document au hasard pour l'afficher en exemple
    sample = collection.find_one()
    logger.info(f"📄 Exemple de document: {sample['Name']}, {sample['Age']} ans")
    
    # ========================================================================
    # ÉTAPE 9 : DÉMONSTRATION DES OPÉRATIONS CRUD
    # ========================================================================
    
    logger.info("\n" + "="*70)
    logger.info("🧪 DÉMONSTRATION DES OPÉRATIONS CRUD")
    logger.info("="*70)
    
    # ------------------------------------------------------------------------
    # READ (Lecture avancée avec filtres)
    # ------------------------------------------------------------------------
    
    logger.info("\n📖 READ - Lecture avec filtres:")
    
    # Exemple 1 : Trouver tous les patients diabétiques
    diabetic_count = collection.count_documents({"Medical Condition": "Diabetes"})
    logger.info(f"   ✅ Patients diabétiques trouvés: {diabetic_count}")
    
    # Exemple 2 : Trouver un patient spécifique par nom
    patient = collection.find_one({"Name": {"$regex": "^Bobby", "$options": "i"}})
    if patient:
        logger.info(f"   ✅ Patient trouvé: {patient['Name']} - {patient['Medical Condition']}")
    
    # Exemple 3 : Compter les patients par hôpital
    first_hospital = collection.find_one({}, {"Hospital": 1})
    if first_hospital:
        hospital_name = first_hospital['Hospital']
        hospital_count = collection.count_documents({"Hospital": hospital_name})
        logger.info(f"   ✅ Patients à l'hôpital '{hospital_name}': {hospital_count}")
    
    # ------------------------------------------------------------------------
    # UPDATE (Mise à jour ciblée)
    # ------------------------------------------------------------------------
    
    logger.info("\n🔄 UPDATE - Mise à jour de documents:")
    
    # Exemple 1 : Mettre à jour le statut d'admission d'un patient
    update_result_1 = collection.update_one(
        {"Name": {"$regex": "^Bobby", "$options": "i"}},
        {
            "$set": {
                "Admission Type": "Elective (Updated)",
                "updated_at": datetime.utcnow()
            }
        }
    )
    logger.info(f"   ✅ Statut d'admission mis à jour: {update_result_1.modified_count} document(s)")
    
    # Exemple 2 : Modifier les informations d'un hôpital
    if first_hospital:
        update_result_2 = collection.update_many(
            {"Hospital": hospital_name},
            {
                "$set": {
                    "Hospital": f"{hospital_name} (Nom mis à jour)",
                    "updated_at": datetime.utcnow()
                }
            }
        )
        logger.info(f"   ✅ Nom d'hôpital mis à jour: {update_result_2.modified_count} document(s)")
    
    # Exemple 3 : Ajouter un champ "status" à tous les patients diabétiques
    update_result_3 = collection.update_many(
        {"Medical Condition": "Diabetes"},
        {
            "$set": {
                "status": "Nécessite suivi régulier",
                "updated_at": datetime.utcnow()
            }
        }
    )
    logger.info(f"   ✅ Champ 'status' ajouté: {update_result_3.modified_count} document(s)")
    
    # ------------------------------------------------------------------------
    # DELETE (Suppression ciblée)
    # ------------------------------------------------------------------------
    
    logger.info("\n🗑️ DELETE - Suppression ciblée de documents:")
    
    # Exemple 1 : Supprimer UN patient de test
    test_patient = {
        "Name": "Test Patient TO DELETE",
        "Age": 99,
        "Gender": "Male",
        "Medical Condition": "Test",
        "Hospital": "Test Hospital",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    collection.insert_one(test_patient)
    
    delete_result_1 = collection.delete_one({"Name": "Test Patient TO DELETE"})
    logger.info(f"   ✅ Patient de test supprimé: {delete_result_1.deleted_count} document(s)")
    
    # Exemple 2 : Supprimer les patients avec le statut temporaire
    delete_result_2 = collection.delete_many({
        "status": "Nécessite suivi régulier"
    })
    logger.info(f"   ✅ Patients avec statut temporaire supprimés: {delete_result_2.deleted_count} document(s)")
    
    # Exemple 3 : Supprimer les documents incomplets
    delete_result_3 = collection.delete_many({
        "$or": [
            {"Name": {"$exists": False}},
            {"Age": {"$exists": False}}
        ]
    })
    logger.info(f"   ✅ Documents incomplets supprimés: {delete_result_3.deleted_count} document(s)")
    
    # ------------------------------------------------------------------------
    # VÉRIFICATION FINALE APRÈS CRUD
    # ------------------------------------------------------------------------
    
    logger.info("\n📊 STATISTIQUES FINALES:")
    final_count = collection.count_documents({})
    logger.info(f"   ✅ Total de documents après opérations CRUD: {final_count}")
    
    logger.info("\n" + "="*70)
    logger.info("🎉 OPÉRATIONS CRUD TERMINÉES AVEC SUCCÈS!")
    logger.info("="*70)
    
    # Fermeture de la connexion MongoDB
    client.close()
    
    logger.info("\n🎉 MIGRATION TERMINÉE AVEC SUCCÈS!")

# ============================================================================
# POINT D'ENTRÉE DU SCRIPT
# ============================================================================
if __name__ == "__main__":
    # Si on exécute CE fichier directement, on lance la migration
    migrate_data()