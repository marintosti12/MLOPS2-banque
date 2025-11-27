---
title: "Deploy MPLOPS 2"
emoji: "🚀"
colorFrom: "blue"
colorTo: "green"
sdk: "docker"
sdk_version: "latest"
app_file: "app.py"
pinned: false
---

📖 Présentation du projet

Cette API fournit un service d’inférence permettant d’évaluer la solvabilité d’un client dans le cadre d’une demande de prêt.
Elle s’intègre dans un pipeline MLOps complet incluant versioning des modèles, monitoring, conteneurisation et automatisation CI/CD.

🧭 Fonctionnalités principales

📊 Lister les modèles ML disponibles (/models)

🤖 Prédire la solvabilité d’un client (/predict)

🗄️ Enregistrer automatiquement les données d’entrée et de sortie en base

📚 Documentation OpenAPI/Swagger générée automatiquement

🐳 Déploiement Docker-Ready

---

## 📦 Prérequis

- Python 3.12+
- [Poetry](gestion des dépendances)
- Docker (PostgreSQL local via Compose)

---

## Installation

### 1. Cloner le dépôt
~~~bash
git https://github.com/marintosti12/MLOPS2-banque.git
cd MLOPS2-banque
~~~


### 2. Créer un environnement virtuel avec Poetry
~~~bash
poetry install
~~~

### 3. Configurer l’environnement

Crée un fichier **.env** à la racine :

~~~env
# PostgreSQL
DATABASE_URL=postgresql+psycopg2://futu:futu_pass@localhost:5432/futurisys
# Hugging Face
HF_TOKEN= Token Hugging Face
HF_REPO_ID= Repo Hugging Face
~~~


### 4. Base de données / Grafana

~~~bash
sudo docker compose up -d
~~~

🗄️ Base de données

~~~mermaid
classDiagram
    direction LR

    class MLModel {
        +UUID id
        +String name
        +Text description
        +DateTime created_at
        +Boolean is_active
    }

    class MLInput {
        +UUID id
        +DateTime created_at
        +String model_name
        +JSONB raw_data
        +JSONB features
    }

    class MLOutput {
        +UUID id
        +UUID input_id
        +String request_id
        +String model_name
        +String model_version
        +DateTime created_at
        +Integer latency_ms
        +String prediction
        +Float prob
        +Float proba_defaut
        +Float proba_solvable
        +Float threshold
        +JSONB classes
        +JSONB meta
        +String error
    }

    class ProfilingLog {
        +UUID id
        +DateTime created_at
        +String endpoint
        +String method
        +String model_name
        +Float total_time_ms
        +Integer num_predictions
        +Float time_preprocessing_ms
        +Float time_inference_ms
        +Float time_database_ms
        +Float time_serialization_ms
        +JSON top_functions
        +Integer ncalls_total
        +Integer ncalls_pandas
        +Integer ncalls_database
        +Float cpu_percent
        +Float memory_mb
        +Text full_profile
    }

    %% Relations
    MLInput "1" --> "0..*" MLOutput : input_id
~~~

### 5. Lancer Migrations

~~~bash
poetry run alembic upgrade head
~~~

### 7. Lancer l’API

~~~bash
poetry run uvicorn src.main:app --reload 
~~~

### 8. Huggings Face

Pour générer les artefacts, exécuter les notebooks de machine learning.

Sur Hugging Face (Models), stocker les artefacts du modèle dans le dépôt du Space (models/) et nommer le fichier exactement comme le nom du modèle en base de données.


### 🧹 Qualité de code

**Lint :**
~~~bash
poetry run ruff check .
~~~

### 🧪 Tests & Couverture

**Lancer les tests :**
```bash
poetry run pytest --maxfail=1 --disable-warnings -q
