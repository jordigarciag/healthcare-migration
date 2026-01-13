# 🏥 Projet Migration Données Médicales → MongoDB

## 📋 Description
Migration de 55 500 dossiers médicaux de patients depuis CSV vers MongoDB.

## 🚀 Installation

### 1. Cloner le projet
```bash
git clone [URL_DU_REPO]
cd healthcare-migration
```

### 2. Créer l'environnement virtuel
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Télécharger le dataset
Télécharge le fichier depuis [Kaggle](https://www.kaggle.com/datasets/prasad22/healthcare-dataset) et place-le dans `data/healthcare_dataset.csv`

## ▶️ Lancer la migration

```bash
python scripts/migration.py
```

## 📊 Structure de la base de données

**Base de données :** `healthcare_db`
**Collection :** `patients`

**Champs :**
- Name (string)
- Age (integer)
- Gender (string)
- Blood Type (string)
- Medical Condition (string)
- Date of Admission (date)
- Doctor (string)
- Hospital (string)
- Insurance Provider (string)
- Billing Amount (float)
- Room Number (integer)
- Admission Type (string)
- Discharge Date (date)
- Medication (string)
- Test Results (string)
- created_at (datetime) - Date de création du document
- updated_at (datetime) - Date de dernière modification

## 🔍 Exemples de requêtes MongoDB

```javascript
// Trouver tous les diabétiques
db.patients.find({"Medical Condition": "Diabetes"})

// Compter par hôpital
db.patients.aggregate([
  { $group: { _id: "$Hospital", count: { $sum: 1 } } }
])
```

## ✅ Vérification

Pour vérifier que tout fonctionne :

1. Ouvre MongoDB Compass
2. Connecte-toi à `mongodb://localhost:27017`
3. Va dans `healthcare_db` → `patients`
4. Tu devrais voir 55 500 documents

**Note :** Le script détecte les doublons (534 identifiés) mais les conserve dans la base de données.

## 👤 Auteur
DataSoluTech - Janvier 2026