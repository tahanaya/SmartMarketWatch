# RAPPORT DE PROJET - SmartMarketWatch
## Module RPA (Collecte de Donnees) - Version 1.0

**Date:** 27 Janvier 2026
**Responsable:** Taha Naya
**Statut:** TERMINE

---

## 1. RESUME EXECUTIF

Le module RPA du projet SmartMarketWatch a ete developpe et deploye avec succes. Le robot de collecte automatique est operationnel et a permis d'extraire **200 produits** du site Jumia Les donnees sont pretes a etre transmises a l'equipe IA pour le nettoyage et l'enrichissement.

---

## 2. OBJECTIFS DU MODULE RPA

| Objectif | Statut |
|----------|--------|
| Developper un robot de scraping automatise | ATTEINT |
| Collecter les donnees produits (titre, prix, images) | ATTEINT |
| Gerer la pagination automatique | ATTEINT |
| Sauvegarder les donnees en format CSV | ATTEINT |
| Creer une architecture modulaire pour les autres equipes | ATTEINT |

---

## 3. ARCHITECTURE TECHNIQUE LIVREE

### 3.1 Structure du Projet

```
SmartMarketWatch/
├── main.py                      # Orchestrateur du pipeline complet
├── requirements.txt             # Dependances Python
├── README.md                    # Documentation
├── .gitignore                   # Fichiers ignores par Git
│
├── src/
│   ├── config.py               # Configuration centralisee
│   │
│   ├── rpa/                    # MODULE RPA [TERMINE]
│   │   ├── __init__.py
│   │   └── scraper.py          # Robot de collecte Jumia
│   │
│   ├── ai/                     # MODULE IA [SQUELETTE]
│   │   ├── __init__.py
│   │   ├── data_cleaner.py     # Nettoyage des donnees
│   │   └── feature_extractor.py # Extraction de features
│   │
│   └── bi/                     # MODULE BI [SQUELETTE]
│       ├── __init__.py
│       └── dashboard.py        # Tableau de bord
│
├── data/
│   ├── raw/                    # Donnees brutes [REMPLI]
│   │   └── raw_data.csv        # 200 produits collectes
│   ├── processed/              # Donnees nettoyees [VIDE - Equipe IA]
│   └── reports/                # Rapports d'analyse [VIDE - Equipe BI]
│
├── logs/                       # Fichiers de log
│   └── scraper.log             # Logs du robot RPA
│
└── docs/                       # Documentation
    └── RAPPORT_RPA_v1.md       # Ce rapport
```

### 3.2 Technologies Utilisees

| Composant | Technologie | Version |
|-----------|-------------|---------|
| Langage | Python | 3.x |
| Automatisation Web | Selenium | 4.15+ |
| Gestion Driver | webdriver-manager | 4.0+ |
| Traitement Donnees | Pandas | 2.0+ |
| Logging | logging (stdlib) | - |

### 3.3 Configuration du Robot

```python
RPA_CONFIG = {
    "url_base": "https://www.jumia.ma/catalog/?q=ordinateur+portable",
    "pages_a_scraper": 5,
    "delai_entre_pages": 4,  # secondes
    "timeout": 20,           # secondes
    "retry_count": 2,        # tentatives par page
    "headless": False,
    "source_name": "Jumia"
}
```

---

## 4. DONNEES COLLECTEES

### 4.1 Volume

| Metrique | Valeur |
|----------|--------|
| Nombre total de produits | 200 |
| Pages scrapees | 5 |
| Produits par page (moyenne) | 40 |
| Taille du fichier CSV | ~85 KB |
| Encodage | UTF-8 BOM |

### 4.2 Schema des Donnees

| Champ | Type | Taux Remplissage | Description |
|-------|------|------------------|-------------|
| Titre | String | 100% | Nom complet du produit |
| Prix_Actuel | String | 100% | Prix en DHS (ex: "1,389.00 Dhs") |
| Ancien_Prix | String | ~70% | Prix avant promotion |
| Discount | String | ~85% | Pourcentage de reduction (ex: "47%") |
| Rating | String | ~50% | Note (ex: "4.5 out of 5") |
| Image_URL | String | 100% | URL de l'image produit |
| Source | String | 100% | "Jumia" |
| Date_Collecte | String | 100% | Timestamp de collecte |

### 4.3 Exemples de Donnees

```csv
Titre: "HP EliteBook 840 G8 I5-1145g7 11eme Generation RAM 16Go DDR4 256Gb SSD"
Prix_Actuel: "3,890.00 Dhs"
Ancien_Prix: "4,990.00 Dhs"
Discount: "22%"
Rating: ""
Image_URL: "https://ma.jumia.is/unsafe/fit-in/300x300/..."
```

### 4.4 Qualite des Donnees - Points d'Attention

| Probleme Identifie | Impact | Solution Recommandee |
|--------------------|--------|---------------------|
| **Doublons** | ~10-15 produits en double | Deduplication par Image_URL |
| **Accessoires melanges** | ~40% des produits | Filtrage par mots-cles dans le titre |
| **Format prix** | Necessite parsing | Regex pour extraire les nombres |
| **Format rating** | "X out of 5" | Parsing en float |
| **Champs vides** | Rating/Ancien_Prix | Gestion des valeurs null |

---

## 5. PERFORMANCES DU ROBOT

### 5.1 Metriques d'Execution

| Metrique | Valeur |
|----------|--------|
| Temps total d'execution | ~2 minutes |
| Temps moyen par page | ~20-25 secondes |
| Taux de succes des pages | 80-100% |
| Produits extraits par seconde | ~1.5 |

### 5.2 Gestion des Erreurs

Le robot inclut:
- **Systeme de retry**: 2 tentatives par page en cas d'echec
- **Gestion des timeouts**: 20 secondes max par page
- **Fermeture des popups**: Detection et fermeture automatique
- **Scroll progressif**: Chargement des images lazy-loaded
- **Logging complet**: Fichier `logs/scraper.log`

---

## 6. FICHIERS LIVRES A L'EQUIPE IA

### 6.1 Fichier Principal

**Chemin:** `data/raw/raw_data.csv`

Ce fichier contient toutes les donnees brutes et constitue l'input pour le module IA.

### 6.2 Squelettes a Implementer

| Fichier | Description | Methodes TODO |
|---------|-------------|---------------|
| `src/ai/data_cleaner.py` | Nettoyage des donnees | `nettoyer_prix()`, `extraire_marque()`, `extraire_cpu()`, `extraire_ram()`, `calculer_reduction()` |
| `src/ai/feature_extractor.py` | Extraction avancee | `classifier_gamme()`, `detecter_anomalies_prix()` |

### 6.3 Configuration IA Preparee

```python
AI_CONFIG = {
    "marques_connues": ["HP", "Dell", "Lenovo", "Asus", "Acer", "Apple", "Samsung", "MSI", "Toshiba", "Huawei"],
    "processeurs_patterns": ["i3", "i5", "i7", "i9", "Ryzen 3", "Ryzen 5", "Ryzen 7", "Celeron", "Pentium"],
    "ram_patterns": ["4GB", "8GB", "16GB", "32GB"],
    "stockage_patterns": ["128GB", "256GB", "512GB", "1TB", "2TB"]
}
```

---

## 7. PROCHAINES ETAPES

### 7.1 Equipe IA - Priorite HAUTE

| Tache | Description | Livrable |
|-------|-------------|----------|
| 1. Nettoyage des prix | Convertir "1,389.00 Dhs" en 1389.0 | Colonne `Prix_Clean` |
| 2. Extraction des marques | Parser le titre pour identifier HP, Dell, etc. | Colonne `Marque` |
| 3. Extraction des specs | CPU, RAM, Stockage depuis le titre | Colonnes `CPU`, `RAM`, `Stockage` |
| 4. Filtrage des accessoires | Garder uniquement les PC portables | Dataset filtre |
| 5. Suppression des doublons | Deduplication par Image_URL | Dataset unique |
| 6. Classification par gamme | Entree/Milieu/Haut de gamme | Colonne `Gamme` |

**Fichier de sortie attendu:** `data/processed/cleaned_data.csv`

### 7.2 Equipe BI - Priorite MOYENNE

| Tache | Description | Livrable |
|-------|-------------|----------|
| 1. Calcul des KPIs | Prix moyen, min, max, etc. | Metriques |
| 2. Dashboard interactif | Streamlit ou Power BI | Application |
| 3. Visualisations | Graphiques prix/marque | Charts |
| 4. Top promotions | Tableau des meilleures affaires | Widget |

**Fichier de sortie attendu:** Dashboard interactif avec visualisations

### 7.3 Ameliorations Futures (Equipe RPA)

| Amelioration | Priorite | Description |
|--------------|----------|-------------|
| Mode headless | Basse | Execution sans fenetre visible |
| Scraping multi-sites | Moyenne | Ajouter Amazon, Marjane, etc. |
| Planification automatique | Haute | Execution quotidienne via cron/Task Scheduler |
| Detection des changements | Moyenne | Alertes si structure HTML change |

---

## 8. COMMANDES UTILES

### Execution du Pipeline

```bash
# Pipeline complet
python main.py --all

# Scraping uniquement
python main.py --scrape

# Nettoyage IA (apres implementation)
python main.py --clean

# Dashboard BI (apres implementation)
python main.py --dashboard
```

### Execution Directe des Modules

```bash
# Module RPA
python src/rpa/scraper.py

# Module IA
python src/ai/data_cleaner.py

# Module BI
python src/bi/dashboard.py
```

---

## 9. CONCLUSION

Le module RPA du projet SmartMarketWatch est **operationnel et livre**. Les 200 produits collectes constituent une base solide pour les analyses IA et BI.

### Recapitulatif

| Module | Statut | Responsable |
|--------|--------|-------------|
| RPA (Scraping) | **TERMINE** | Equipe RPA |
| IA (Data Mining) | **A IMPLEMENTER** | Equipe IA |
| BI (Dashboard) | **A IMPLEMENTER** | Equipe BI |

### Progression Globale du Projet

```
[##########....................] 33% Complete

[X] Module RPA - Collecte des donnees
[ ] Module IA  - Nettoyage et enrichissement
[ ] Module BI  - Dashboard et visualisations
```

---

**Document genere le:** 27 Janvier 2026
**Version:** 1.0
**Prochaine revision:** Apres livraison Module IA
