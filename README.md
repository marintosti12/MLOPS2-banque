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

Cette API permet de prédire l’attrition des employés à partir de données RH.
Elle a pour objectif d’aider les équipes RH à identifier les risques de départ et mettre en place des actions préventives.

- 📊 **Lister** les modèles ML disponibles (`/`)
- 🤖 **Prédire** avec un modèle donné (`/predict`)
- 🗄️ **Sauvegarder** automatiquement les inputs et outputs en base
- 📚 **Documentation Swagger/OpenAPI** générée automatiquement

---

## 📦 Prérequis

- Python 3.12+
- [Poetry](gestion des dépendances)
- Docker (PostgreSQL local via Compose)

---

## Installation

### 1. Cloner le dépôt
~~~bash
git clone https://github.com/marintosti12/deploy-machine-learning.git
cd deploy-machine-learning
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


### 4. Base de données (PostgreSQL)

~~~bash
sudo docker compose up -d
~~~

🗄️ Base de données

~~~mermaid
classDiagram
  direction LR

  class MLModel {
    +String(36) id
    +String name
    +Text description
    +DateTime created_at
    +Boolean is_active
  }

  class MLInput {
    +String(36) id
    +DateTime created_at
    +Int id_employee
    +Int age
    +String genre
    +Int revenu_mensuel
    +String statut_marital
    +String departement
    +String poste
    +Int nombre_experiences_precedentes
    +Int nombre_heures_travailless
    +Int annee_experience_totale
    +Int annees_dans_l_entreprise
    +Int annees_dans_le_poste_actuel
    +Int nombre_participation_pee
    +Int nb_formations_suivies
    +Int nombre_employee_sous_responsabilite
    +Int code_sondage
    +Int distance_domicile_travail
    +Int niveau_education
    +String domaine_etude
    +String ayant_enfants
    +String frequence_deplacement
    +Int annees_depuis_la_derniere_promotion
    +Int annes_sous_responsable_actuel
    +Int satisfaction_employee_environnement
    +Int note_evaluation_precedente
    +Int niveau_hierarchique_poste
    +Int satisfaction_employee_nature_travail
    +Int satisfaction_employee_equipe
    +Int satisfaction_employee_equilibre_pro_perso
    +String eval_number
    +Int note_evaluation_actuelle
    +String heure_supplementaires
    +Int augementation_salaire_precedente
  }

  

  class MLOutput {
    +String(36) id
    +DateTime created_at
    +String(36) input_id  (FK -> MLInput.id)
    +String prediction
    +Float prob
    +String error
  }

  class EmployeeDataset {
    +BigInteger id  
    +DateTime created_at  
    +Integer id_employee  

    +Integer age
    +String genre
    +Integer revenu_mensuel
    +String statut_marital
    +String departement  
    +String poste

    +Integer nombre_experiences_precedentes
    +Integer nombre_heures_travailless
    +Integer annee_experience_totale
    +Integer annees_dans_l_entreprise
    +Integer annees_dans_le_poste_actuel

    +Integer a_quitte_l_entreprise

    +Integer nombre_participation_pee
    +Integer nb_formations_suivies
    +Integer nombre_employee_sous_responsabilite

    +Integer code_sondage
    +Integer distance_domicile_travail
    +Integer niveau_education
    +String domaine_etude

    +String ayant_enfants
    +String frequence_deplacement

    +Integer annees_depuis_la_derniere_promotion
    +Integer annes_sous_responsable_actuel
    +Integer satisfaction_employee_environnement
    +Integer note_evaluation_precedente
    +Integer niveau_hierarchique_poste
    +Integer satisfaction_employee_nature_travail
    +Integer satisfaction_employee_equipe
    +Integer satisfaction_employee_equilibre_pro_perso

    +String eval_number  
    +Integer note_evaluation_actuelle
    +String heure_supplementaires
    +Integer augementation_salaire_precedente

    +String source_file  
}

  %% Relations
  MLInput "1" --> "0..*" MLOutput
~~~

### 5. Lancer Migrations

~~~bash
export DATABASE_URL='postgresql+asyncpg://futu:futu_pass@localhost:5432/futurisys'
poetry run alembic upgrade head
~~~

### 6. Lancer Seeder

~~~bash
export DATABASE_URL='postgresql+psycopg2://futu:futu_pass@localhost:5432/futurisys'
poetry run python src/seeds/ml_models_seed.py 
~~~

### 7. Lancer l’API

~~~bash
poetry run uvicorn main:app --reload --app-dir src
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
