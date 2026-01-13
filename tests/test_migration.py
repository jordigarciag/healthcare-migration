"""
Tests unitaires pour le script de migration MongoDB
"""

import pytest
import pandas as pd
from pymongo import MongoClient
from datetime import datetime
import os


class TestDataLoading:
    """Tests pour le chargement du fichier CSV"""
    
    def test_csv_file_exists(self):
        """Vérifie que le fichier CSV existe"""
        csv_path = "data/healthcare_dataset.csv"
        assert os.path.exists(csv_path), f"Le fichier {csv_path} n'existe pas"
    
    def test_csv_loads_successfully(self):
        """Vérifie que le CSV se charge correctement"""
        df = pd.read_csv("data/healthcare_dataset.csv")
        assert len(df) > 0, "Le CSV est vide"
        assert len(df) == 55500, f"Attendu 55500 lignes, trouvé {len(df)}"
    
    def test_csv_has_required_columns(self):
        """Vérifie que toutes les colonnes requises sont présentes"""
        df = pd.read_csv("data/healthcare_dataset.csv")
        required_columns = [
            'Name', 'Age', 'Gender', 'Blood Type', 
            'Medical Condition', 'Date of Admission', 'Doctor',
            'Hospital', 'Insurance Provider', 'Billing Amount',
            'Room Number', 'Admission Type', 'Discharge Date',
            'Medication', 'Test Results'
        ]
        for col in required_columns:
            assert col in df.columns, f"Colonne manquante : {col}"


class TestDataValidation:
    """Tests pour la validation des données"""
    
    def test_no_missing_values_in_critical_fields(self):
        """Vérifie qu'il n'y a pas de valeurs manquantes dans les champs critiques"""
        df = pd.read_csv("data/healthcare_dataset.csv")
        critical_fields = ['Name', 'Age', 'Medical Condition']
        for field in critical_fields:
            assert df[field].isnull().sum() == 0, f"Valeurs manquantes dans {field}"
    
    def test_age_is_positive(self):
        """Vérifie que tous les âges sont positifs"""
        df = pd.read_csv("data/healthcare_dataset.csv")
        assert (df['Age'] > 0).all(), "Des âges négatifs ou nuls détectés"


class TestMongoDBConnection:
    """Tests pour la connexion MongoDB"""
    
    def test_mongodb_connection(self):
        """Vérifie que MongoDB est accessible"""
        try:
            client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
            client.server_info()  # Force une connexion
            client.close()
        except Exception as e:
            pytest.fail(f"Impossible de se connecter à MongoDB : {e}")
    
    def test_database_exists(self):
        """Vérifie que la base de données healthcare_db existe"""
        client = MongoClient("mongodb://localhost:27017/")
        db_names = client.list_database_names()
        assert "healthcare_db" in db_names, "Base de données healthcare_db non trouvée"
        client.close()
    
    def test_collection_exists(self):
        """Vérifie que la collection patients existe"""
        client = MongoClient("mongodb://localhost:27017/")
        db = client["healthcare_db"]
        collections = db.list_collection_names()
        assert "patients" in collections, "Collection patients non trouvée"
        client.close()
    
    def test_documents_count(self):
        """Vérifie que le nombre de documents est correct"""
        client = MongoClient("mongodb://localhost:27017/")
        db = client["healthcare_db"]
        collection = db["patients"]
        count = collection.count_documents({})
        assert count == 55500, f"Attendu 55500 documents, trouvé {count}"
        client.close()


class TestDataTransformation:
    """Tests pour la transformation des données"""
    
    def test_date_conversion(self):
        """Vérifie que les dates sont correctement converties"""
        df = pd.read_csv("data/healthcare_dataset.csv")
        df['Date of Admission'] = pd.to_datetime(df['Date of Admission'])
        assert df['Date of Admission'].dtype == 'datetime64[ns]', "Conversion de date échouée"
    
    def test_timestamps_added(self):
        """Vérifie que les timestamps sont ajoutés aux documents"""
        client = MongoClient("mongodb://localhost:27017/")
        db = client["healthcare_db"]
        collection = db["patients"]
        sample = collection.find_one()
        assert 'created_at' in sample, "Champ created_at manquant"
        assert 'updated_at' in sample, "Champ updated_at manquant"
        assert isinstance(sample['created_at'], datetime), "created_at n'est pas un datetime"
        client.close()


class TestIndexes:
    """Tests pour les index MongoDB"""
    
    def test_indexes_created(self):
        """Vérifie que tous les index requis sont créés"""
        client = MongoClient("mongodb://localhost:27017/")
        db = client["healthcare_db"]
        collection = db["patients"]
        
        indexes = list(collection.list_indexes())
        index_names = [idx['name'] for idx in indexes]
        
        # Index par défaut _id_ + 4 index créés
        assert len(indexes) >= 5, f"Attendu au moins 5 index, trouvé {len(indexes)}"
        
        client.close()