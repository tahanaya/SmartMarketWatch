# GUIDE DES RESPONSABILITES PAR MEMBRE

## Projet SmartMarketWatch - Version 1.0

**Date:** 27 Janvier 2026
**Chef de Projet:** Taha Naya
**Statut Global:** 33% Complete

---

## ETAT ACTUEL DU PROJET

```
[##########....................] 33% Complete

[X] Module RPA    - Collecte des donnees      (TERMINE)
[ ] Module IA     - Nettoyage et NLP          (A IMPLEMENTER)
[ ] Module BDD    - Schema et insertion SQL   (A IMPLEMENTER)
[ ] Module BI     - Dashboard Power BI        (A IMPLEMENTER)
[ ] Integration   - Pipeline main.py          (PARTIELLEMENT FAIT)
```

### Donnees Disponibles

- **Fichier source:** `data/raw/raw_data.csv`
- **Volume:** 200 produits collectes
- **Colonnes:** Titre, Prix_Actuel, Ancien_Prix, Discount, Rating, Image_URL, Source, Date_Collecte

---

## MEMBRE 1 - INGENIEUR RPA (Taha Naya)

### Statut: TERMINE

### Travail Accompli

| Tache                       | Fichier                 | Statut |
| --------------------------- | ----------------------- | ------ |
| Script de scraping Selenium | `src/rpa/scraper.py`    | FAIT   |
| Configuration centralisee   | `src/config.py`         | FAIT   |
| Gestion pagination et retry | `src/rpa/scraper.py`    | FAIT   |
| Sauvegarde CSV              | `data/raw/raw_data.csv` | FAIT   |

### Livrables Produits

1. **Robot de collecte fonctionnel** - 200 produits extraits
2. **Architecture projet** - Structure modulaire pour les autres equipes
3. **Documentation** - `docs/RAPPORT_RPA_v1.md`

### Prochaines Actions (Optionnel - Ameliorations Futures)

- [ ] Ajouter le mode headless pour execution en arriere-plan
- [ ] Implementer le scraping multi-sites (Amazon, Marjane)
- [ ] Creer une planification automatique (cron/Task Scheduler)

---

## MEMBRE 2 - DATA ANALYST / IA

### Statut: A IMPLEMENTER

### Fichiers a Modifier

1. **`src/ai/data_cleaner.py`** - Nettoyage des donnees
2. **`src/ai/feature_extractor.py`** - Extraction avancee et NLP

### Taches Detaillees

#### TACHE 2.1 - Nettoyage des Prix

**Fichier:** `src/ai/data_cleaner.py`
**Methode:** `nettoyer_prix()`

```python
# Input:  "1,389.00 Dhs" ou "42.00 Dhs"
# Output: 1389.0 ou 42.0

def nettoyer_prix(self, prix_str):
    """
    Convertit le prix texte en nombre flottant.
    - Supprimer " Dhs"
    - Supprimer les virgules des milliers
    - Convertir en float
    """
    if pd.isna(prix_str) or prix_str == "":
        return None

    import re
    # Extraire uniquement les chiffres et le point decimal
    prix_clean = re.sub(r'[^\d.]', '', prix_str.replace(',', ''))

    try:
        return float(prix_clean)
    except ValueError:
        return None
```

#### TACHE 2.2 - Extraction de la Marque

**Fichier:** `src/ai/data_cleaner.py`
**Methode:** `extraire_marque()`

```python
# Utiliser la liste de marques dans config.py
# AI_CONFIG["marques_connues"] = ["HP", "Dell", "Lenovo", "Asus", ...]

def extraire_marque(self, titre):
    """
    Extrait la marque du titre du produit.
    """
    if pd.isna(titre):
        return "Autre"

    titre_upper = titre.upper()
    for marque in AI_CONFIG["marques_connues"]:
        if marque.upper() in titre_upper:
            return marque
    return "Autre"
```

#### TACHE 2.3 - Extraction des Specifications

**Fichier:** `src/ai/data_cleaner.py`
**Methodes:** `extraire_cpu()`, `extraire_ram()`, `extraire_stockage()`

```python
# Patterns disponibles dans config.py:
# processeurs_patterns: ["i3", "i5", "i7", "i9", "Ryzen 3", ...]
# ram_patterns: ["4GB", "8GB", "16GB", "32GB", ...]
# stockage_patterns: ["128GB", "256GB", "512GB", "1TB", ...]

def extraire_cpu(self, titre):
    """Extrait le type de processeur du titre."""
    if pd.isna(titre):
        return None
    titre_upper = titre.upper()
    for pattern in AI_CONFIG["processeurs_patterns"]:
        if pattern.upper() in titre_upper:
            return pattern
    return None

def extraire_ram(self, titre):
    """Extrait la RAM du titre."""
    # Meme logique avec ram_patterns
    pass

def extraire_stockage(self, titre):
    """Extrait le stockage du titre."""
    # Meme logique avec stockage_patterns
    pass
```

#### TACHE 2.4 - Filtrage des Accessoires

**Fichier:** `src/ai/data_cleaner.py`
**Methode:** `filtrer_accessoires()`

```python
def filtrer_accessoires(self, df):
    """
    Garde uniquement les PC portables, filtre les accessoires.

    Mots-cles a EXCLURE:
    - "souris", "mouse", "tapis", "sacoche", "sac", "cartable"
    - "support", "chargeur", "cable", "adaptateur", "clavier"
    - "casque", "haut-parleur", "webcam", "ecran seul"

    Mots-cles a INCLURE:
    - "laptop", "portable", "notebook", "pc portable"
    - "elitebook", "probook", "thinkpad", "latitude"
    """
    mots_exclus = ["souris", "mouse", "tapis", "sacoche", "sac",
                   "support", "chargeur", "cable", "adaptateur",
                   "casque", "haut-parleur", "clavier seul"]

    def est_pc_portable(titre):
        if pd.isna(titre):
            return False
        titre_lower = titre.lower()

        # Verifier mots exclus
        for mot in mots_exclus:
            if mot in titre_lower:
                return False

        # Verifier presence de mots PC
        mots_pc = ["laptop", "portable", "notebook", "elitebook",
                   "probook", "thinkpad", "latitude", "ideapad"]
        return any(mot in titre_lower for mot in mots_pc)

    return df[df["Titre"].apply(est_pc_portable)]
```

#### TACHE 2.5 - Suppression des Doublons

**Fichier:** `src/ai/data_cleaner.py`
**Methode:** `supprimer_doublons()`

```python
def supprimer_doublons(self, df):
    """
    Supprime les doublons bases sur Image_URL.
    """
    return df.drop_duplicates(subset=["Image_URL"], keep="first")
```

#### TACHE 2.6 - Classification par Gamme (NLP/IA)

**Fichier:** `src/ai/feature_extractor.py`
**Methode:** `classifier_gamme()`

```python
def classifier_gamme(self, prix, cpu=None, ram=None):
    """
    Classifie le produit par gamme de prix.

    Regles suggerees:
    - ENTREE DE GAMME: prix < 2500 DHS
    - MILIEU DE GAMME: 2500 <= prix < 5000 DHS
    - HAUT DE GAMME: prix >= 5000 DHS

    Bonus: Ajuster selon CPU (i3=entree, i5=milieu, i7+=haut)
    """
    if pd.isna(prix):
        return "Inconnu"

    if prix < 2500:
        return "Entree de gamme"
    elif prix < 5000:
        return "Milieu de gamme"
    else:
        return "Haut de gamme"
```

#### TACHE 2.7 - Detection d'Anomalies Prix (Optionnel)

**Fichier:** `src/ai/feature_extractor.py`
**Methode:** `detecter_anomalies_prix()`

```python
def detecter_anomalies_prix(self, df):
    """
    Detecte les prix anormalement bas ou hauts.
    Utiliser IQR (Interquartile Range) ou Z-score.
    """
    Q1 = df["Prix_Clean"].quantile(0.25)
    Q3 = df["Prix_Clean"].quantile(0.75)
    IQR = Q3 - Q1

    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    df["Anomalie_Prix"] = (df["Prix_Clean"] < lower_bound) | \
                          (df["Prix_Clean"] > upper_bound)
    return df
```

### Schema de Donnees en Sortie

Le fichier `data/processed/cleaned_data.csv` doit contenir:

| Colonne           | Type     | Description                      |
| ----------------- | -------- | -------------------------------- |
| Titre             | String   | Titre original                   |
| Prix_Clean        | Float    | Prix nettoye (ex: 1389.0)        |
| Ancien_Prix_Clean | Float    | Ancien prix nettoye              |
| Reduction_Pct     | Float    | Pourcentage de reduction calcule |
| Marque            | String   | HP, Dell, Lenovo, etc.           |
| CPU               | String   | i3, i5, i7, Ryzen 5, etc.        |
| RAM               | String   | 4GB, 8GB, 16GB, etc.             |
| Stockage          | String   | 256GB, 512GB, 1TB, etc.          |
| Gamme             | String   | Entree/Milieu/Haut de gamme      |
| Rating_Clean      | Float    | Note sur 5 (ex: 4.5)             |
| Image_URL         | String   | URL image                        |
| Source            | String   | Jumia                            |
| Date_Collecte     | DateTime | Timestamp                        |

### Livrables Attendus

1. **`data/processed/cleaned_data.csv`** - Donnees nettoyees et enrichies
2. **Methodes implementees** dans `data_cleaner.py` et `feature_extractor.py`

### Commande de Test

```bash
python src/ai/data_cleaner.py
# ou
python main.py --clean
```

---

## MEMBRE 3 - ARCHITECTE DE DONNEES

### Statut: A IMPLEMENTER

### Fichiers a Creer

1. **`src/database/db_manager.py`** - Gestionnaire de base de donnees
2. **`src/database/schema.sql`** - Schema SQL de la table

### Taches Detaillees

#### TACHE 3.1 - Conception du Schema SQL

**Fichier a creer:** `src/database/schema.sql`

#### TACHE 3.2 - Gestionnaire de Base de Donnees

**Fichier a creer:** `src/database/db_manager.py`

````python
"""
SmartMarketWatch - Module Base de Donnees
=========================================
Responsable: Architecte de Donnees (Membre 3)
"""

#### TACHE 3.3 - Creer le dossier et __init__.py
```bash
# Structure a creer:
src/
  database/
    __init__.py
    db_manager.py
    schema.sql
````

**Fichier:** `src/database/__init__.py`

```python
from .db_manager import DatabaseManager
```

### Livrables Attendus

1. **`src/database/schema.sql`** - Schema de la base de donnees
2. **`src/database/db_manager.py`** - Classe DatabaseManager
3. **`data/smartmarketwatch.db`** - Base de donnees creee

### Commande de Test

```bash
python src/database/db_manager.py
```

---

## MEMBRE 4 - CONCEPTEUR BI

### Statut: A IMPLEMENTER

### Outils Requis

- **Power BI Desktop**

### Option A: Power BI (Recommande)

#### TACHE 4.1 - Installation et Configuration

1. Telecharger et installer Power BI Desktop
2. Ouvrir Power BI Desktop

#### TACHE 4.2 - Connexion aux Donnees

**Alternative Mysql:**

1. "Obtenir les donnees" > "Base de donnees" >
2. Configurer la connexion vers ta base de donne

#### TACHE 4.3 - Creation des KPIs

Creer les mesures suivantes dans Power BI:

| KPI                | Formule DAX                        |
| ------------------ | ---------------------------------- |
| Nombre de produits | `COUNTROWS(produits)`              |
| Prix moyen         | `AVERAGE(produits[prix_actuel])`   |
| Prix minimum       | `MIN(produits[prix_actuel])`       |
| Prix maximum       | `MAX(produits[prix_actuel])`       |
| Reduction moyenne  | `AVERAGE(produits[reduction_pct])` |
| Top marque         | `FIRSTNONBLANK(...)`               |

#### TACHE 4.4 - Creation des Visualisations

**Page 1: Vue d'ensemble**

- 4 cartes KPI (nb produits, prix moyen, min, max)
- Graphique a barres: Nombre de produits par marque
- Graphique circulaire: Repartition par gamme

**Page 2: Analyse des Prix**

- Histogramme: Distribution des prix
- Graphique a barres: Prix moyen par marque
- Nuage de points: Prix vs Reduction

**Page 3: Top Promotions**

- Tableau: Top 10 des meilleures reductions
- Filtres: Marque, Gamme, Fourchette de prix

#### TACHE 4.5 - Filtres et Slicers

Ajouter des slicers pour:

- Marque (multi-selection)
- Gamme (entree/milieu/haut)
- Fourchette de prix
- Date de collecte

### Option B: Streamlit (Alternative Python)

**Fichier:** `src/bi/dashboard.py`

```python
"""
SmartMarketWatch - Dashboard BI avec Streamlit
==============================================
Responsable: Concepteur BI (Membre 4)


### Livrables Attendus
1. **Fichier Power BI** (`reports/SmartMarketWatch.pbix`) OU
2. **Dashboard Streamlit** (`src/bi/dashboard.py`) fonctionnel


```

---

## MEMBRE 5 - INTEGRATEUR

### Statut: PARTIELLEMENT FAIT

### Fichier Principal

**`main.py`** - Deja cree, a completer avec les nouveaux modules

### Taches Detaillees

#### TACHE 5.1 - Integration du Module BDD

Modifier `main.py` pour ajouter l'option `--db`:

#### TACHE 5.2 - Pipeline Complet Mis a Jour

`

## CALENDRIER SUGGERE

| Semaine | Membre         | Tache                                    |
| ------- | -------------- | ---------------------------------------- |
| S1      | Membre 2 (IA)  | Nettoyage des prix et extraction marques |
| S1      | Membre 3 (BDD) | Creation du schema SQL                   |
| S2      | Membre 2 (IA)  | Extraction specs + filtrage accessoires  |
| S2      | Membre 3 (BDD) | Implementation db_manager.py             |
| S2      | Membre 4 (BI)  | Installation Power BI + connexion        |
| S3      | Membre 4 (BI)  | Creation des visualisations              |
| S3      | Membre 5 ()    | Integration finale                       |
| S4      | TOUS           | Tests et corrections                     |

---
