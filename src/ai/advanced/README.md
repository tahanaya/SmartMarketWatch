# 🧠 Module IA Avancé - SmartMarketWatch

## 🎯 Vue d'Ensemble

Ce module IA avancé apporte des capacités de **Natural Language Processing (NLP)** et **Machine Learning** professionnelles au projet SmartMarketWatch, bien au-delà du nettoyage de données basique.

---

## 🏗️ Architecture

```
src/ai/advanced/
├── nlp_analyzer.py          # Analyse NLP avec spaCy & BERT
├── anomaly_detector.py      # Détection ML avec Isolation Forest
├── pipeline_master.py       # Orchestrateur principal
└── README.md                # Cette documentation
```

---

## ⚡ Fonctionnalités Avancées

### 🔤 **1. NLP Analyzer** (`nlp_analyzer.py`)

#### **Extraction de Features Techniques Avancées**
- **Processeur détaillé**: Marque (Intel/AMD), série (i3/i5/i7/Ryzen), modèle exact, génération
- **RAM détaillée**: Capacité, type (DDR3/DDR4), fréquence (MHz)
- **Stockage détaillé**: SSD vs HDD, capacité, type NVMe, stockage total
- **Écran**: Taille exacte, résolution (width×height), type (IPS/OLED), tactile oui/non
- **Carte graphique**: Marque (NVIDIA/AMD/Intel), série (GTX/RTX/Radeon), modèle
- **Connectivité**: WiFi (version), Bluetooth, USB, HDMI
- **Batterie**: Capacité (Wh/mAh), autonomie estimée

**Exemple de patterns regex utilisés**:
```python
Intel: r'(?:Intel\s+)?Core\s+i([3579])-?(\d{4,5}[A-Z]*)'
AMD: r'(?:AMD\s+)?Ryzen\s+([3579])\s+(\d{4}[A-Z]*)'
RAM: r'(\d+)\s*(?:GB|Go|GB)\s*(?:DDR\d?|RAM)'
```

#### **Analyse de Sentiment Multilingue**
- **Modèle BERT**: `nlptown/bert-base-multilingual-uncased-sentiment`
- Support français, anglais, arabe
- Retourne: Label (Positif/Neutre/Négatif) + Score de confiance (0-1)
- Fallback sur analyse par mots-clés si BERT indisponible

#### **Extraction de Mots-Clés (TF-IDF)**
- Identification automatique des termes les plus représentatifs
- Top 5 keywords par produit
- Utile pour la recherche et le SEO

#### **Détection d'Entités Nommées (NER)**
- Extraction automatique des marques, modèles, organisations
- Utilise spaCy (fr_core_news_sm ou en_core_web_sm)

#### **Génération de Résumés Intelligents**
- Résumé automatique en une ligne par produit
- Format: `HP | Processeur i5 | 8GB RAM DDR4 | 256GB SSD | Écran 15.6" | Remis à neuf | 2199 Dhs`

**Colonnes créées**:
```
CPU_Marque, CPU_Serie, CPU_Modele, CPU_Generation_Detectee
RAM_Type, RAM_Frequence
Stockage_SSD_GB, Stockage_HDD_GB, Stockage_NVMe, Stockage_Total_GB
Ecran_Taille, Ecran_Resolution_Width, Ecran_Resolution_Height, Ecran_Type, Ecran_Tactile
GPU_Marque, GPU_Serie, GPU_Modele
WiFi_Version, Bluetooth_Version
Batterie_Capacite, Batterie_Autonomie
Sentiment_BERT, Sentiment_Score_BERT
Keywords_TFIDF
Resume_Produit
```

---

### 🚨 **2. Anomaly Detector** (`anomaly_detector.py`)

#### **Détection Statistique Multi-Méthodes**

**Méthode 1: Z-Score**
- Détecte les valeurs à >3 écarts-types de la moyenne
- Par gamme de produit pour plus de précision

**Méthode 2: IQR (Interquartile Range)**
- Outliers = valeurs < Q1 - 1.5×IQR ou > Q3 + 1.5×IQR
- Méthode robuste aux distributions non-normales

**Méthode 3: Isolation Forest (ML)**
- Algorithme d'apprentissage non-supervisé
- Détecte les anomalies multivariées (prix + specs combinées)
- Contamination configurée à 10%
- Score d'anomalie normalisé entre 0 (très anormal) et 1 (très normal)

#### **Détection d'Incohérences Specs/Prix**

Règles métier implémentées:
```python
RÈGLE 1: Performance élevée (≥80) + prix bas (<3000 Dhs) → Suspect
RÈGLE 2: i7/i9/Ryzen7/9 + prix <2500 Dhs → CPU premium sous-évalué
RÈGLE 3: 32GB RAM + prix <4000 Dhs → Configuration sous-évaluée
RÈGLE 4: Performance faible (≤40) + prix >4000 Dhs → Surpayé
RÈGLE 5: Celeron/Pentium + prix >3000 Dhs → Entrée de gamme surévalué
RÈGLE 6: Réduction >70% → Promotion suspecte
```

Chaque incohérence reçoit un **score de sévérité** (0-5).

#### **Marquage des Produits Suspects**

Un produit est marqué suspect si:
- ✅ Anomalie ML détectée (Isolation Forest)
- ✅ Anomalie prix statistique (Z-Score ou IQR)
- ✅ Incohérence sévère (score ≥3)
- ✅ Données très incomplètes (<40% de complétude)
- ✅ Prix extrême (<500 ou >20000 Dhs)

**Colonnes créées**:
```
Anomalie_Prix_ZScore, Anomalie_Prix_IQR
Type_Anomalie_Prix
Anomalie_ML, Anomalie_Score_ML, Anomalie_Score_Normalized
Incoherence_Spec_Prix, Severite_Incoherence
Produit_Suspect, Raisons_Suspicion
```

---

### 🎛️ **3. Pipeline Master** (`pipeline_master.py`)

Orchestrateur intelligent qui:
1. Charge les données nettoyées
2. Exécute le module NLP
3. Exécute le module de détection d'anomalies
4. Calcule les **métriques business avancées**:
   - **Indice de Confiance** (0-100): Fiabilité globale du produit
   - **Recommandation d'Achat**: Très recommandé / Recommandé / À considérer / Non recommandé
   - **Score de Fiabilité Vendeur** (1-5 étoiles)
5. Génère un rapport complet
6. Sauvegarde les résultats enrichis

---

## 📦 Installation

### **Option 1: Installation Légère** (Recommandée pour démo)
```bash
pip install pandas numpy scikit-learn scipy textblob
```
Taille: ~100 MB

### **Option 2: Installation Complète** (Production)
```bash
pip install -r requirements_advanced.txt

# Télécharger les modèles spaCy
python -m spacy download fr_core_news_sm
python -m spacy download en_core_web_sm

# Télécharger corpus TextBlob
python -m textblob.download_corpora
```
Taille: ~2-3 GB

---

## 🚀 Utilisation

### **Mode Standalone**

```bash
# NLP uniquement
python src/ai/advanced/nlp_analyzer.py

# Détection d'anomalies uniquement
python src/ai/advanced/anomaly_detector.py

# Pipeline complet (recommandé)
python src/ai/advanced/pipeline_master.py
```

### **Intégration dans main.py**

```python
from src.ai.advanced.pipeline_master import AdvancedAIPipeline

# Après le nettoyage basique
pipeline = AdvancedAIPipeline(input_file='data/processed/cleaned_data.csv')
pipeline.execute_full_pipeline()
```

---

## 📊 Sorties Générées

### **1. Fichier CSV Enrichi**
`data/processed/ai_advanced_complete.csv`

**Contient**:
- Toutes les colonnes originales
- +40 nouvelles colonnes de features NLP
- +15 colonnes de détection d'anomalies
- +3 colonnes de métriques business

**Taille typique**: ~500 KB pour 200 produits

### **2. Rapport d'Analyse NLP**
(Intégré dans le rapport global)

### **3. Rapport de Détection d'Anomalies**
`data/reports/anomaly_report.txt`

**Contient**:
- Nombre d'anomalies par type
- Top 10 produits suspects
- Distribution des scores
- Statistiques par gamme

### **4. Rapport Global IA Avancée**
`data/reports/ai_advanced_report.txt`

**Contient**:
- Statistiques complètes d'exécution
- Résumé de tous les modules
- Top 5 meilleures affaires (haute confiance)
- Top 5 produits à vérifier (suspects)
- Métriques de recommandation

---

## 🎓 Concepts Techniques Expliqués

### **TF-IDF (Term Frequency-Inverse Document Frequency)**
Mesure l'importance d'un mot dans un document par rapport à un corpus.

**Formule**: `TF-IDF = (nombre d'occurrences du mot / total mots) × log(nombre total documents / documents contenant le mot)`

**Utilité**: Identifier les mots-clés les plus distinctifs de chaque produit.

### **Isolation Forest**
Algorithme d'apprentissage non-supervisé pour la détection d'anomalies.

**Principe**: Les anomalies sont isolées plus rapidement dans un arbre de décision car elles sont "rares et différentes".

**Avantages**:
- Ne nécessite pas de labellisation
- Performant même avec peu de données
- Détecte les anomalies multivariées

### **Z-Score**
Mesure la distance d'une valeur par rapport à la moyenne en unités d'écart-type.

**Formule**: `Z = (X - μ) / σ`

**Seuil**: |Z| > 3 → Anomalie (probabilité <0.3%)

### **Named Entity Recognition (NER)**
Identification automatique d'entités nommées dans le texte (personnes, organisations, lieux, produits).

**Modèles utilisés**: spaCy (fr_core_news_sm / en_core_web_sm)

### **BERT (Bidirectional Encoder Representations from Transformers)**
Modèle de langage pré-entraîné sur des millions de documents.

**Utilité ici**: Analyse de sentiment multilingue avec compréhension contextuelle.

---

## ⚙️ Configuration Avancée

### **Paramètres Modifiables**

**Dans `nlp_analyzer.py`**:
```python
# Nombre de mots-clés extraits
top_n = 10  # ligne 295

# Modèle BERT (changez si nécessaire)
model = "nlptown/bert-base-multilingual-uncased-sentiment"
```

**Dans `anomaly_detector.py`**:
```python
# Taux d'anomalies attendu
contamination = 0.1  # 10%, ligne 130

# Seuil Z-Score
z_threshold = 3  # ligne 67

# Multiplicateur IQR
iqr_multiplier = 1.5  # ligne 74
```

**Dans `pipeline_master.py`**:
```python
# Seuil de confiance pour recommandations
high_confidence_threshold = 80  # ligne 104
medium_confidence_threshold = 60  # ligne 106
```

---

## 🐛 Troubleshooting

### **Erreur: "spaCy model not found"**
```bash
python -m spacy download fr_core_news_sm
```

### **Erreur: "No module named 'transformers'"**
```bash
pip install transformers torch
```
⚠️ Note: Torch est volumineux (~2GB). Pour une démo, utilisez TextBlob à la place.

### **Out of Memory avec BERT**
Réduire la longueur des textes analysés:
```python
# ligne 263 de nlp_analyzer.py
titre_court = str(titre)[:200]  # Au lieu de 500
```

### **Isolation Forest trop lent**
Réduire le nombre d'arbres:
```python
# ligne 130 de anomaly_detector.py
n_estimators = 50  # Au lieu de 100
```

---

## 📈 Performances

**Temps d'exécution typique** (200 produits):

| Module | Sans modèles lourds | Avec BERT & spaCy |
|--------|-------------------|-------------------|
| NLP Analyzer | ~5 secondes | ~30 secondes |
| Anomaly Detector | ~2 secondes | ~2 secondes |
| **TOTAL** | **~7 secondes** | **~32 secondes** |

**Mémoire RAM requise**:
- Configuration légère: 500 MB
- Configuration complète: 2-3 GB

---

## 🔬 Exemples de Résultats

### **Extraction NLP Réussie**
```
Titre: "Hp PC Portable ELITEBOOK 840 G8 - INTEL CORE I7-11ème GÉNÉRATION - 32GB - 512GB SSD"

Extraction:
✓ CPU_Marque: Intel
✓ CPU_Serie: i7
✓ CPU_Modele: (non présent dans titre)
✓ CPU_Generation_Detectee: 11
✓ RAM_GB: 32
✓ Stockage_SSD_GB: 512
✓ Resume: HP | Processeur i7 | 32GB RAM | 512GB SSD | Remis à neuf | 6399 Dhs
```

### **Anomalie Détectée**
```
Titre: "DELL Latitude 7420 Intel i5-11ème 16GB 256GB SSD 14" - 3690 Dhs"

Flags:
⚠️ Anomalie_ML: True
⚠️ Anomalie_Prix_IQR: False
⚠️ Incoherence_Spec_Prix: "Haute perf mais prix bas"
⚠️ Severite_Incoherence: 3
⚠️ Produit_Suspect: True
⚠️ Raisons_Suspicion: "Anomalie ML + Incohérence majeure"
✓ Indice_Confiance: 45/100
✓ Recommandation_Achat: "Non recommandé - Vérifier"
```

---

## 🎯 Cas d'Usage Business

### **1. E-Commerce**
- Détection automatique de prix frauduleux
- Recommandations d'achat fiables
- Enrichissement SEO avec mots-clés TF-IDF

### **2. Veille Concurrentielle**
- Surveillance des anomalies de prix concurrents
- Analyse de sentiment sur les descriptions produits
- Extraction automatique des specs pour comparaison

### **3. Conformité & Qualité**
- Validation automatique des fiches produits
- Détection de descriptions incomplètes ou trompeuses
- Score de fiabilité vendeur

---

## 🚀 Évolutions Futures Possibles

- [ ] **Clustering de produits similaires** (K-Means, DBSCAN)
- [ ] **Prédiction de prix** (Régression, Random Forest)
- [ ] **Détection de tendances temporelles** (Time Series Analysis)
- [ ] **Génération de descriptions par GPT** (OpenAI API)
- [ ] **Analyse d'images produits** (CNN, YOLO pour détection de défauts)
- [ ] **Recommandation collaborative** (Matrix Factorization)

---

## 📚 Références

- **spaCy**: https://spacy.io/
- **Transformers (Hugging Face)**: https://huggingface.co/docs/transformers
- **Isolation Forest**: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html
- **TF-IDF**: https://scikit-learn.org/stable/modules/feature_extraction.html#tfidf-term-weighting

---

## 👨‍💻 Support

Pour toute question ou bug, consulter:
- **Documentation principale**: README.md du projet
- **Logs**: `logs/data_cleaner.log`
- **Rapports**: `data/reports/`

---

**Version**: 2.0  
**Date**: Janvier 2026  
**Auteur**: Équipe IA - SmartMarketWatch  
**License**: Projet Académique
