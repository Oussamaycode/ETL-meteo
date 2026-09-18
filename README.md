# 🌦️ Weather Risk ETL & Dashboard

## 📌 Contexte

Une entreprise de livraison et de logistique opère dans plusieurs villes marocaines. Les conditions météorologiques peuvent impacter ses opérations, notamment en cas de fortes précipitations, de vents importants ou de températures extrêmes.

Ce projet consiste à construire une solution de données permettant de récupérer les prévisions météorologiques des prochains jours, d'identifier les périodes à risque et d'aider les responsables opérationnels à anticiper les éventuelles perturbations.

La solution utilise deux sources principales :

* **SimpleMaps** — dataset des villes marocaines et leurs coordonnées géographiques.
* **Open-Meteo** — API fournissant les prévisions météorologiques quotidiennes.

Le pipeline suit une architecture **Bronze → Silver → Gold**, est orchestré par **Apache Airflow**, stocke les données finales dans **PostgreSQL** et les présente dans un dashboard **Streamlit**.

---

## 🎯 Objectif métier

La solution doit permettre de répondre à la question :

> **Quelles villes et quelles périodes présentent le plus grand risque météorologique dans les prochains jours ?**

Elle permet notamment de :

* comparer les conditions météorologiques entre les villes ;
* identifier les périodes défavorables ;
* anticiper les risques pour les livraisons ;
* adapter l'organisation des opérations.

---

## 🏗️ Architecture

```text
                         ┌──────────────────┐
                         │    SimpleMaps    │
                         │  Morocco Cities  │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │   Open-Meteo     │
                         │       API        │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │     Airflow      │
                         │   ETL Pipeline   │
                         └────────┬─────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    ▼                           ▼
             ┌─────────────┐             ┌─────────────┐
             │   BRONZE    │             │    SILVER   │
             │ Raw data    │────────────▶│ Clean data  │
             └─────────────┘             └──────┬──────┘
                                                │
                                                ▼
                                         ┌─────────────┐
                                         │     GOLD    │
                                         │ Risk Score  │
                                         │ Features    │
                                         └──────┬──────┘
                                                │
                                                ▼
                                      ┌──────────────────┐
                                      │    PostgreSQL    │
                                      │    gold_data     │
                                      └────────┬─────────┘
                                               │
                                               ▼
                                      ┌──────────────────┐
                                      │    Streamlit     │
                                      │    Dashboard     │
                                      └──────────────────┘
```

---

# 📂 Structure du projet

```text
weather-risk/
│
├── dags/
│   └── meteo_etl.py
│
├── data/
│   ├── bronze/
│   │   └── raw.csv
│   │
│   ├── silver/
│   │   └── silver_data.csv
│   │
│   └── gold/
│       └── gold_data.csv
│
├── streamlit/
│   ├── app.py
│   └── .streamlit/
│       └── secrets.toml
│
├── data.csv
│
├── docker-compose.yaml
│
└── README.md
```

---

# 📥 Sources de données

## SimpleMaps

Le dataset SimpleMaps contient les villes marocaines ainsi que leurs coordonnées géographiques.

Source :

[SimpleMaps — Morocco Cities](https://simplemaps.com/data/ma-cities?utm_source=chatgpt.com)

Les coordonnées `latitude` et `longitude` sont utilisées pour interroger Open-Meteo.

## Open-Meteo

Les prévisions sont récupérées à partir de l'API Open-Meteo.

Variables utilisées :

* `temperature_2m_max`
* `temperature_2m_min`
* `precipitation_sum`
* `precipitation_probability_max`
* `wind_speed_10m_max`
* `wind_gusts_10m_max`
* `weather_code`

Les prévisions sont récupérées pour les prochains jours et associées aux villes marocaines.

---

# 🥉 Bronze — Données brutes

La première étape consiste à récupérer les données depuis SimpleMaps et Open-Meteo.

Les données brutes sont conservées dans :

```text
data/bronze/
```

Exemple :

```text
data/bronze/raw.csv
```

Les données Bronze ne sont pas modifiées après leur extraction.

### Gestion des erreurs

Le pipeline prend en compte les erreurs pouvant survenir lors des appels API :

* timeout ;
* erreurs HTTP ;
* réponses invalides ;
* problèmes de connexion ;
* données manquantes.

---

# 🥈 Silver — Nettoyage

Les données Bronze sont transformées en données propres et structurées.

Les principales opérations sont :

* standardisation des types ;
* conversion des dates ;
* détection des doublons ;
* détection des incohérences ;
* contrôles de qualité ;
* jointure entre les villes et les données météorologiques.

Les données nettoyées sont stockées dans :

```text
data/silver/
```

---

# 🥇 Gold — Feature Engineering

La couche Gold contient les données prêtes pour l'analyse métier.

Des indicateurs sont créés, notamment :

### Catégorie de température

```text
temperature_category
```

### Catégorie de précipitations

```text
precipitation_category
```

### Catégorie de vent

```text
wind_category
```

### Score de risque

```text
risk_score
```

---

# ⚠️ Weather Risk Score

Un score compris entre **0 et 100** est calculé afin d'identifier les conditions météorologiques potentiellement défavorables.

Le score utilise notamment :

* la température ;
* les précipitations ;
* la probabilité de précipitations ;
* la vitesse du vent ;
* les rafales de vent ;
* les conditions météorologiques.

Le score permet de faciliter la comparaison entre les villes et les différentes dates.

Les niveaux utilisés dans le dashboard sont :

|  Score | Niveau      |
| -----: | ----------- |
|   0–19 | Très faible |
|  20–39 | Faible      |
|  40–59 | Moyen       |
|  60–79 | Élevé       |
| 80–100 | Très élevé  |

---

# 🗄️ PostgreSQL

Les données Gold sont chargées dans PostgreSQL.

Deux bases sont utilisées :

```text
PostgreSQL
│
├── airflow
│   └── Métadonnées Airflow
│
└── gold_data
    └── gold_data
```

La base `airflow` est utilisée par Airflow pour ses métadonnées.

La base `gold_data` contient les données finales utilisées par le dashboard.

La table principale est :

```text
gold_data
```

Elle contient notamment :

* les villes ;
* les coordonnées ;
* les dates ;
* les prévisions météorologiques ;
* les catégories météo ;
* le `risk_score`.

---

# 🔄 Gestion des nouvelles prévisions

Les prévisions météorologiques peuvent être mises à jour lors de chaque exécution du pipeline.

Le chargement PostgreSQL permet donc de rafraîchir les données utilisées par le dashboard.

Une évolution possible du projet consiste à conserver l'historique des différentes prévisions afin de comparer les anciennes prévisions avec les nouvelles.

---

# 📊 Analyse SQL

Le projet permet d'effectuer des analyses SQL sur les données Gold.

Exemples de questions métier :

### 1. Quelles villes auront les températures les plus élevées ?

```sql
SELECT city, MAX(temperature_2m_max) AS max_temperature
FROM gold_data
GROUP BY city
ORDER BY max_temperature DESC;
```

### 2. Quelles villes auront les plus fortes précipitations ?

```sql
SELECT city, MAX(precipitation_sum) AS max_precipitation
FROM gold_data
GROUP BY city
ORDER BY max_precipitation DESC;
```

### 3. Quelles villes présentent le risque moyen le plus élevé ?

```sql
SELECT city, AVG(risk_score) AS average_risk
FROM gold_data
GROUP BY city
ORDER BY average_risk DESC;
```

### 4. Quelles périodes présentent le risque maximal ?

```sql
SELECT city, date, risk_score
FROM gold_data
ORDER BY risk_score DESC;
```

### 5. Pour chaque ville, quelle période présente le plus grand risque ?

```sql
SELECT city, date, risk_score
FROM gold_data
WHERE risk_score = (
    SELECT MAX(g2.risk_score)
    FROM gold_data g2
    WHERE g2.city = gold_data.city
)
ORDER BY risk_score DESC;
```

---

# 📈 Streamlit Dashboard

Le dashboard Streamlit est connecté directement à PostgreSQL.

Il permet de visualiser les données météorologiques et les niveaux de risque.

## KPI

Le dashboard affiche notamment :

* **Nombre de villes**
* **Température maximale**
* **Précipitations maximales**
* **Nombre de périodes à risque**
* **Ville présentant le risque maximal**

## Filtres

Les données peuvent être filtrées par :

* ville ;
* date ;
* niveau de risque.

## Visualisations

Le dashboard contient notamment :

* 🗺️ carte des villes ;
* 📈 évolution du `risk_score` ;
* 🥧 répartition du risque météorologique ;
* 📋 tableau des données filtrées.

Le dashboard est accessible avec :

```text
http://localhost:8501
```

---

# ⚙️ Airflow

Apache Airflow orchestre l'ensemble du pipeline.

Le DAG réalise les étapes suivantes :

```text
Extract
   ↓
Bronze
   ↓
Silver
   ↓
Gold
   ↓
PostgreSQL
```

Le DAG est configuré pour s'exécuter **tous les jours à 00:00**.

Configuration :

```python
schedule="0 0 * * *"
```

Le pipeline utilise également des mécanismes de gestion des erreurs et de retry afin de pouvoir réessayer une tâche en cas d'échec.

Airflow est accessible avec :

```text
http://localhost:8080
```

---

# 🐳 Docker

L'ensemble du projet est conteneurisé avec Docker Compose.

Les principaux services sont :

```text
Docker Compose
│
├── PostgreSQL
├── Airflow
└── Streamlit
```

Les services communiquent entre eux grâce aux noms des services Docker.

Par exemple, PostgreSQL est accessible depuis Airflow et Streamlit avec :

```text
postgres:5432
```

et non :

```text
localhost:5432
```

---

# 🚀 Installation et lancement

## 1. Cloner le projet

```bash
git clone <repository-url>
cd weather-risk
```

## 2. Démarrer les services

```bash
docker compose up -d
```

## 3. Vérifier les conteneurs

```bash
docker compose ps
```

## 4. Accéder aux applications

### Airflow

```text
http://localhost:8080
```

### Streamlit

```text
http://localhost:8501
```

---

# 🔄 Commandes Docker utiles

### Démarrer

```bash
docker compose up -d
```

### Arrêter

```bash
docker compose down
```

### Redémarrer

```bash
docker compose restart
```

### Voir les logs Streamlit

```bash
docker compose logs streamlit
```

### Voir les logs Airflow

```bash
docker compose logs airflow-scheduler
```

### Voir les conteneurs

```bash
docker compose ps
```

---

# 🔐 Configuration PostgreSQL

Streamlit utilise une connexion configurée dans :

```text
streamlit/.streamlit/secrets.toml
```

Configuration Docker :

```toml
[connections.postgresql]
url = "postgresql://airflow:airflow@postgres:5432/gold_data"
```

Airflow utilise également PostgreSQL, mais sa base de métadonnées reste séparée :

```text
airflow
```

Les données métier sont stockées dans :

```text
gold_data
```

---

# 🔁 Pipeline complet

Une exécution quotidienne suit ce processus :

```text
00:00
 │
 ▼
Airflow déclenche le DAG
 │
 ▼
Récupération des villes SimpleMaps
 │
 ▼
Appels Open-Meteo
 │
 ▼
Bronze
 │
 ▼
Nettoyage + contrôles qualité
 │
 ▼
Silver
 │
 ▼
Feature Engineering
 │
 ▼
Calcul du risk_score
 │
 ▼
Gold
 │
 ▼
PostgreSQL / gold_data
 │
 ▼
Streamlit
 │
 ▼
Dashboard mis à jour
```

---

# 🛠️ Technologies utilisées

| Technologie        | Utilisation                                |
| ------------------ | ------------------------------------------ |
| **Python**         | Développement du pipeline                  |
| **Pandas**         | Manipulation et transformation des données |
| **Requests**       | Appels API                                 |
| **Open-Meteo**     | Source des données météorologiques         |
| **SimpleMaps**     | Source des villes marocaines               |
| **Apache Airflow** | Orchestration et automatisation            |
| **PostgreSQL**     | Stockage des données Gold                  |
| **SQL**            | Analyse des données                        |
| **Streamlit**      | Dashboard interactif                       |
| **Plotly**         | Visualisations                             |
| **Docker**         | Conteneurisation                           |
| **Docker Compose** | Orchestration des services                 |

---

# 🎯 Résultat

Le projet fournit une chaîne de données complète et automatisée :

**Extraction → Transformation → Analyse → Stockage → Visualisation**

Le responsable opérationnel dispose ainsi d'une vue centralisée permettant d'identifier les villes et les périodes présentant des conditions météorologiques potentiellement défavorables pour les opérations de livraison.
