# 🏥 Projet Migration Données Médicales → MongoDB

## 📋 Description

Migration de 55 500 dossiers médicaux de patients depuis CSV vers MongoDB.

## 🚀 Installation

### 1. Cloner le projet

```bash
git clone https://github.com/jordigarciag/healthcare-migration.git
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

---

## 🐳 Déploiement avec Docker

### Prérequis
- Docker Desktop installé (Windows/Mac) ou Docker Engine (Linux)
- Docker Compose installé

### Lancement rapide

```bash
# 1. Cloner le projet
git clone https://github.com/jordigarciag/healthcare-migration.git
cd healthcare-migration

# 2. Construire et démarrer
docker-compose up -d

# 3. Suivre la migration
docker-compose logs -f migration

# 4. Vérifier les données
docker exec -it healthcare-mongodb mongosh -u admin -p admin123
```

### Interface Web
Accédez à Mongo Express : http://localhost:8081

### Services déployés
- **MongoDB** : Port 27017
- **Mongo Express** : Port 8081
- **Script Migration** : S'exécute automatiquement

### Volumes persistants
- `mongodb_data` : Données MongoDB
- `mongodb_config` : Configuration MongoDB

### Arrêter les services
```bash
docker-compose down
```

---

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

## 🧪 Tests

Pour exécuter les tests unitaires :

```bash
pytest tests/test_migration.py -v
```

Pour voir la couverture de code :

```bash
pytest tests/test_migration.py --cov=scripts --cov-report=html
```

**Tests implémentés :**
- ✅ Vérification de l'existence du fichier CSV
- ✅ Validation du chargement des données (55 500 lignes)
- ✅ Contrôle des colonnes requises
- ✅ Détection des valeurs manquantes
- ✅ Validation des types de données (âge positif)
- ✅ Test de connexion à MongoDB
- ✅ Vérification de l'existence de la base et collection
- ✅ Contrôle du nombre de documents
- ✅ Validation de la conversion des dates
- ✅ Vérification des timestamps (created_at, updated_at)
- ✅ Contrôle de la création des index

## ✅ Vérification

Pour vérifier que tout fonctionne :

1. Ouvre Mongo Express : http://localhost:8081
2. Connecte-toi avec admin / admin123
3. Va dans `healthcare_db` → `patients`
4. Tu devrais voir 55 500 documents

**Note :** Le script détecte les doublons (534 identifiés) mais les conserve dans la base de données.

## 👤 Auteur

DataSoluTech - Janvier 2026