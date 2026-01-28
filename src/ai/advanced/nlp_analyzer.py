"""
Module NLP Avancé - SmartMarketWatch
Description: Analyse de texte approfondie avec extraction d'entités, sentiment analysis,
            et détection automatique de caractéristiques techniques
"""

import pandas as pd
import numpy as np
import re
import logging
from pathlib import Path
from collections import Counter
import json

# NLP Libraries - Gérer l'incompatibilité Python 3.14
SPACY_AVAILABLE = False
TRANSFORMERS_AVAILABLE = False
SKLEARN_AVAILABLE = False

# spaCy - désactivé pour Python 3.14
try:
    import spacy
    SPACY_AVAILABLE = True
except (ImportError, Exception) as e:
    logging.warning(f"spaCy non disponible ({type(e).__name__}) - Certaines features NLP seront désactivées")
    logging.info("Note: spaCy n'est pas compatible avec Python 3.14. Utilisez Python 3.11 ou 3.12 si nécessaire.")

# Transformers
try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    logging.warning("Transformers non installé - Sentiment analysis avancée désactivée")

# scikit-learn
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    logging.warning("scikit-learn non installé - Analyse TF-IDF désactivée")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AdvancedNLPAnalyzer:
    """Analyseur NLP avancé pour les descriptions de produits"""
    
    def __init__(self, df):
        """
        Initialisation de l'analyseur NLP
        
        Args:
            df (pd.DataFrame): DataFrame avec les données produits
        """
        self.df = df
        self.nlp = None
        self.sentiment_analyzer = None
        self.tfidf_vectorizer = None
        
        # Chargement des modèles
        self._load_models()
        
        # Dictionnaires de patterns techniques
        self.tech_patterns = self._build_tech_patterns()
        
    def _load_models(self):
        """Charge les modèles NLP"""
        # spaCy - désactivé pour Python 3.14
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load("fr_core_news_sm")
                logger.info("✓ Modèle spaCy français chargé")
            except:
                try:
                    self.nlp = spacy.load("en_core_web_sm")
                    logger.info("✓ Modèle spaCy anglais chargé")
                except:
                    logger.warning("⚠ Aucun modèle spaCy disponible")
        else:
            logger.info("ℹ️ spaCy désactivé (incompatible Python 3.14) - Extraction de features basique utilisée")
        
        # Charger sentiment analyzer si disponible
        if TRANSFORMERS_AVAILABLE:
            try:
                self.sentiment_analyzer = pipeline(
                    "sentiment-analysis",
                    model="nlptown/bert-base-multilingual-uncased-sentiment"
                )
                logger.info("✓ Analyseur de sentiment multilingue chargé")
            except:
                logger.warning("⚠ Sentiment analyzer non disponible")
        
        # Initialiser TF-IDF
        if SKLEARN_AVAILABLE:
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=100,
                ngram_range=(1, 2),
                stop_words='english'
            )
    
    def _build_tech_patterns(self):
        """Construit les patterns de détection de caractéristiques techniques"""
        return {
            'processeur': {
                'intel': r'(?:Intel\s+)?Core\s+i([3579])-?(\d{4,5}[A-Z]*)',
                'amd': r'(?:AMD\s+)?Ryzen\s+([3579])\s+(\d{4}[A-Z]*)',
                'generation': r'(\d+)(?:ème|th|e)\s+(?:Gen|Génération)',
            },
            'ram': {
                'capacite': r'(\d+)\s*(?:GB|Go|GB)\s*(?:DDR\d?|RAM)',
                'type': r'DDR([34])',
                'frequence': r'(\d{4})\s*MHz',
            },
            'stockage': {
                'ssd': r'(\d+)\s*(?:GB|Go|TB|To)\s+SSD',
                'hdd': r'(\d+)\s*(?:GB|Go|TB|To)\s+(?:HDD|Disque dur)',
                'nvme': r'NVMe|M\.2',
                'total': r'(\d+)\s*(?:GB|Go|TB|To)',
            },
            'ecran': {
                'taille': r'(\d{2}(?:\.\d)?)\s*(?:pouces?|"|\'\')',
                'resolution': r'(\d{3,4})\s*[xX×]\s*(\d{3,4})',
                'type': r'(IPS|OLED|LED|LCD|TN|VA)',
                'tactile': r'(?:tactile|touch|touchscreen)',
            },
            'carte_graphique': {
                'nvidia': r'(?:NVIDIA|GeForce)\s+(GTX|RTX)\s+(\d{4})',
                'amd': r'(?:AMD\s+)?Radeon\s+([A-Z0-9]+)',
                'intel': r'Intel\s+(?:UHD|Iris|HD)\s+Graphics?\s*(\d{3,4})?',
            },
            'connectivite': {
                'wifi': r'Wi-?Fi\s*([456])?',
                'bluetooth': r'Bluetooth\s*([\d.]+)?',
                'usb': r'USB(?:-([AC]))?\s*([\d.]+)?',
                'hdmi': r'HDMI\s*([\d.]+)?',
            },
            'batterie': {
                'capacite': r'(\d+)\s*(?:Wh|mAh)',
                'autonomie': r'(\d+)\s*heures?',
            }
        }
    
    def extract_advanced_features(self):
        """
        Extrait des caractéristiques techniques avancées depuis les titres
        """
        logger.info("Extraction avancée des caractéristiques techniques...")
        
        features_data = []
        
        for idx, row in self.df.iterrows():
            titre = str(row['Titre'])
            features = {
                'Index': idx,
                
                # Processeur détaillé
                'CPU_Marque': None,
                'CPU_Serie': None,
                'CPU_Modele': None,
                'CPU_Generation_Detectee': None,
                
                # RAM détaillée
                'RAM_Type': None,
                'RAM_Frequence': None,
                
                # Stockage détaillé
                'Stockage_SSD_GB': None,
                'Stockage_HDD_GB': None,
                'Stockage_NVMe': False,
                'Stockage_Total_GB': None,
                
                # Écran
                'Ecran_Taille': None,
                'Ecran_Resolution_Width': None,
                'Ecran_Resolution_Height': None,
                'Ecran_Type': None,
                'Ecran_Tactile': False,
                
                # Carte graphique
                'GPU_Marque': None,
                'GPU_Serie': None,
                'GPU_Modele': None,
                
                # Connectivité
                'WiFi_Version': None,
                'Bluetooth_Version': None,
                'USB_Type': None,
                
                # Batterie
                'Batterie_Capacite': None,
                'Batterie_Autonomie': None,
            }
            
            # === PROCESSEUR ===
            # Intel
            intel_match = re.search(self.tech_patterns['processeur']['intel'], titre, re.IGNORECASE)
            if intel_match:
                features['CPU_Marque'] = 'Intel'
                features['CPU_Serie'] = f"i{intel_match.group(1)}"
                features['CPU_Modele'] = intel_match.group(2)
            
            # AMD
            amd_match = re.search(self.tech_patterns['processeur']['amd'], titre, re.IGNORECASE)
            if amd_match:
                features['CPU_Marque'] = 'AMD'
                features['CPU_Serie'] = f"Ryzen {amd_match.group(1)}"
                features['CPU_Modele'] = amd_match.group(2)
            
            # Génération
            gen_match = re.search(self.tech_patterns['processeur']['generation'], titre)
            if gen_match:
                features['CPU_Generation_Detectee'] = int(gen_match.group(1))
            
            # === RAM ===
            ram_match = re.search(self.tech_patterns['ram']['capacite'], titre, re.IGNORECASE)
            ram_type = re.search(self.tech_patterns['ram']['type'], titre)
            ram_freq = re.search(self.tech_patterns['ram']['frequence'], titre)
            
            if ram_type:
                features['RAM_Type'] = f"DDR{ram_type.group(1)}"
            if ram_freq:
                features['RAM_Frequence'] = int(ram_freq.group(1))
            
            # === STOCKAGE ===
            ssd_match = re.search(self.tech_patterns['stockage']['ssd'], titre, re.IGNORECASE)
            hdd_match = re.search(self.tech_patterns['stockage']['hdd'], titre, re.IGNORECASE)
            nvme_match = re.search(self.tech_patterns['stockage']['nvme'], titre, re.IGNORECASE)
            
            if ssd_match:
                capacite = int(ssd_match.group(1))
                if 'TB' in ssd_match.group(0).upper() or 'TO' in ssd_match.group(0).upper():
                    capacite *= 1024
                features['Stockage_SSD_GB'] = capacite
                features['Stockage_Total_GB'] = capacite
            
            if hdd_match:
                capacite = int(hdd_match.group(1))
                if 'TB' in hdd_match.group(0).upper() or 'TO' in hdd_match.group(0).upper():
                    capacite *= 1024
                features['Stockage_HDD_GB'] = capacite
                if features['Stockage_Total_GB']:
                    features['Stockage_Total_GB'] += capacite
                else:
                    features['Stockage_Total_GB'] = capacite
            
            if nvme_match:
                features['Stockage_NVMe'] = True
            
            # === ÉCRAN ===
            taille_match = re.search(self.tech_patterns['ecran']['taille'], titre)
            res_match = re.search(self.tech_patterns['ecran']['resolution'], titre)
            type_match = re.search(self.tech_patterns['ecran']['type'], titre, re.IGNORECASE)
            tactile_match = re.search(self.tech_patterns['ecran']['tactile'], titre, re.IGNORECASE)
            
            if taille_match:
                features['Ecran_Taille'] = float(taille_match.group(1))
            
            if res_match:
                features['Ecran_Resolution_Width'] = int(res_match.group(1))
                features['Ecran_Resolution_Height'] = int(res_match.group(2))
            
            if type_match:
                features['Ecran_Type'] = type_match.group(1).upper()
            
            if tactile_match:
                features['Ecran_Tactile'] = True
            
            # === CARTE GRAPHIQUE ===
            nvidia_match = re.search(self.tech_patterns['carte_graphique']['nvidia'], titre, re.IGNORECASE)
            amd_gpu_match = re.search(self.tech_patterns['carte_graphique']['amd'], titre, re.IGNORECASE)
            intel_gpu_match = re.search(self.tech_patterns['carte_graphique']['intel'], titre, re.IGNORECASE)
            
            if nvidia_match:
                features['GPU_Marque'] = 'NVIDIA'
                features['GPU_Serie'] = nvidia_match.group(1)
                features['GPU_Modele'] = nvidia_match.group(2)
            elif amd_gpu_match:
                features['GPU_Marque'] = 'AMD'
                features['GPU_Modele'] = amd_gpu_match.group(1)
            elif intel_gpu_match:
                features['GPU_Marque'] = 'Intel'
                if intel_gpu_match.group(1):
                    features['GPU_Modele'] = intel_gpu_match.group(1)
            
            # === CONNECTIVITÉ ===
            wifi_match = re.search(self.tech_patterns['connectivite']['wifi'], titre, re.IGNORECASE)
            bt_match = re.search(self.tech_patterns['connectivite']['bluetooth'], titre, re.IGNORECASE)
            
            if wifi_match and wifi_match.group(1):
                features['WiFi_Version'] = f"WiFi {wifi_match.group(1)}"
            
            if bt_match and bt_match.group(1):
                features['Bluetooth_Version'] = bt_match.group(1)
            
            # === BATTERIE ===
            bat_cap_match = re.search(self.tech_patterns['batterie']['capacite'], titre)
            bat_auto_match = re.search(self.tech_patterns['batterie']['autonomie'], titre)
            
            if bat_cap_match:
                features['Batterie_Capacite'] = int(bat_cap_match.group(1))
            
            if bat_auto_match:
                features['Batterie_Autonomie'] = int(bat_auto_match.group(1))
            
            features_data.append(features)
        
        # Créer un DataFrame avec les features
        features_df = pd.DataFrame(features_data)
        
        # Fusionner avec le DataFrame principal
        for col in features_df.columns:
            if col != 'Index':
                self.df[col] = features_df[col].values
        
        logger.info(f"✓ {len(features_df.columns) - 1} caractéristiques avancées extraites")
        
        return self.df
    
    def analyze_sentiment_advanced(self):
        """
        Analyse de sentiment avancée avec BERT multilingue
        """
        if not self.sentiment_analyzer:
            logger.warning("⚠ Sentiment analyzer non disponible - utilisation méthode simple")
            return self._analyze_sentiment_simple()
        
        logger.info("Analyse de sentiment avancée (BERT)...")
        
        sentiments = []
        scores = []
        
        for titre in self.df['Titre']:
            try:
                # Limiter la longueur pour BERT (512 tokens max)
                titre_court = str(titre)[:500]
                
                result = self.sentiment_analyzer(titre_court)[0]
                
                # Le modèle retourne 1-5 étoiles
                label = result['label']
                score = int(label.split()[0])  # "5 stars" -> 5
                confidence = result['score']
                
                # Convertir en sentiment
                if score >= 4:
                    sentiment = "Positif"
                elif score <= 2:
                    sentiment = "Négatif"
                else:
                    sentiment = "Neutre"
                
                sentiments.append(sentiment)
                scores.append(score / 5.0)  # Normaliser 0-1
                
            except Exception as e:
                sentiments.append("Neutre")
                scores.append(0.5)
        
        self.df['Sentiment_BERT'] = sentiments
        self.df['Sentiment_Score_BERT'] = scores
        
        logger.info(f"✓ Sentiment analysé - Distribution: {Counter(sentiments)}")
        
        return self.df
    
    def _analyze_sentiment_simple(self):
        """Analyse de sentiment simple basée sur des mots-clés"""
        
        mots_positifs = [
            'excellent', 'parfait', 'super', 'top', 'meilleur', 'qualité',
            'rapide', 'performant', 'puissant', 'fiable', 'recommande',
            'génial', 'incroyable', 'fantastique', 'premium', 'pro',
            'nouveau', 'récent', 'moderne', 'haute', 'grand'
        ]
        
        mots_negatifs = [
            'lent', 'mauvais', 'défectueux', 'problème', 'cassé',
            'décevant', 'faible', 'médiocre', 'ancien', 'obsolète',
            'bug', 'erreur', 'panne', 'défaut', 'occasion'
        ]
        
        def analyser(texte):
            texte_lower = str(texte).lower()
            score_pos = sum(1 for mot in mots_positifs if mot in texte_lower)
            score_neg = sum(1 for mot in mots_negatifs if mot in texte_lower)
            
            if score_pos > score_neg:
                return "Positif", 0.7
            elif score_neg > score_pos:
                return "Négatif", 0.3
            else:
                return "Neutre", 0.5
        
        resultats = self.df['Titre'].apply(analyser)
        self.df['Sentiment_BERT'] = resultats.apply(lambda x: x[0])
        self.df['Sentiment_Score_BERT'] = resultats.apply(lambda x: x[1])
        
        return self.df
    
    def extract_keywords_tfidf(self, top_n=10):
        """
        Extrait les mots-clés les plus importants avec TF-IDF
        """
        if not SKLEARN_AVAILABLE:
            logger.warning("⚠ scikit-learn non disponible - Extraction TF-IDF ignorée")
            return self.df
        
        logger.info("Extraction des mots-clés avec TF-IDF...")
        
        # Préparer les textes
        textes = self.df['Titre'].fillna('').tolist()
        
        # Calculer TF-IDF
        try:
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(textes)
            feature_names = self.tfidf_vectorizer.get_feature_names_out()
            
            # Extraire les top keywords pour chaque produit
            keywords_list = []
            
            for idx in range(len(textes)):
                # Récupérer les scores TF-IDF pour ce document
                tfidf_scores = tfidf_matrix[idx].toarray()[0]
                
                # Trier et prendre les top N
                top_indices = tfidf_scores.argsort()[-top_n:][::-1]
                top_keywords = [feature_names[i] for i in top_indices if tfidf_scores[i] > 0]
                
                keywords_list.append(", ".join(top_keywords[:5]))  # Top 5
            
            self.df['Keywords_TFIDF'] = keywords_list
            
            logger.info("✓ Mots-clés TF-IDF extraits")
            
        except Exception as e:
            logger.error(f"✗ Erreur TF-IDF: {e}")
        
        return self.df
    
    def detect_named_entities(self):
        """
        Détection d'entités nommées avec spaCy (marques, modèles, etc.)
        Note: Désactivé pour Python 3.14 (incompatibilité spaCy)
        """
        if not self.nlp:
            logger.info("ℹ️ Détection d'entités nommées ignorée (spaCy non disponible)")
            return self.df
        
        logger.info("Détection d'entités nommées...")
        
        entites_produit = []
        entites_marque = []
        entites_org = []
        
        for titre in self.df['Titre']:
            doc = self.nlp(str(titre))
            
            produits = [ent.text for ent in doc.ents if ent.label_ == 'PRODUCT']
            marques = [ent.text for ent in doc.ents if ent.label_ in ['ORG', 'BRAND']]
            orgs = [ent.text for ent in doc.ents if ent.label_ == 'ORG']
            
            entites_produit.append(", ".join(produits) if produits else None)
            entites_marque.append(", ".join(marques) if marques else None)
            entites_org.append(", ".join(orgs) if orgs else None)
        
        self.df['Entites_Produit'] = entites_produit
        self.df['Entites_Marque'] = entites_marque
        self.df['Entites_Organisation'] = entites_org
        
        logger.info("✓ Entités nommées détectées")
        
        return self.df
    
    def generate_product_summary(self):
        """
        Génère un résumé automatique pour chaque produit
        """
        logger.info("Génération de résumés produits...")
        
        summaries = []
        
        for idx, row in self.df.iterrows():
            parts = []
            
            # Marque et modèle
            if pd.notna(row.get('Marque')) and row['Marque'] != 'Autre':
                parts.append(row['Marque'])
            
            # CPU
            if pd.notna(row.get('CPU_Serie')):
                parts.append(f"Processeur {row['CPU_Serie']}")
            elif pd.notna(row.get('CPU')):
                parts.append(f"Processeur {row['CPU']}")
            
            # RAM
            if pd.notna(row.get('RAM_GB')):
                ram_text = f"{int(row['RAM_GB'])}GB RAM"
                if pd.notna(row.get('RAM_Type')):
                    ram_text += f" {row['RAM_Type']}"
                parts.append(ram_text)
            
            # Stockage
            if pd.notna(row.get('Stockage_Total_GB')):
                storage = int(row['Stockage_Total_GB'])
                if storage >= 1024:
                    parts.append(f"{storage//1024}TB")
                else:
                    parts.append(f"{storage}GB")
                
                if row.get('Stockage_NVMe'):
                    parts[-1] += " NVMe SSD"
                elif pd.notna(row.get('Type_Stockage')):
                    parts[-1] += f" {row['Type_Stockage']}"
            
            # Écran
            if pd.notna(row.get('Ecran_Taille')):
                ecran_text = f"Écran {row['Ecran_Taille']}\""
                if row.get('Ecran_Tactile'):
                    ecran_text += " tactile"
                parts.append(ecran_text)
            
            # État
            if pd.notna(row.get('Etat_Produit')) and row['Etat_Produit'] != 'Non spécifié':
                parts.append(row['Etat_Produit'])
            
            # Prix
            if pd.notna(row.get('Prix_Actuel_Clean')):
                parts.append(f"{int(row['Prix_Actuel_Clean'])} Dhs")
            
            summary = " | ".join(parts) if parts else "Informations limitées"
            summaries.append(summary)
        
        self.df['Resume_Produit'] = summaries
        
        logger.info("✓ Résumés générés")
        
        return self.df
    
    def execute_full_pipeline(self):
        """
        Exécute toutes les analyses NLP avancées
        """
        logger.info("="*60)
        logger.info("PIPELINE NLP AVANCÉ")
        logger.info("="*60)
        
        # Extraction de features avancées
        self.extract_advanced_features()
        
        # Analyse de sentiment
        self.analyze_sentiment_advanced()
        
        # Extraction de mots-clés
        self.extract_keywords_tfidf()
        
        # Détection d'entités (optionnel - désactivé si spaCy non dispo)
        if self.nlp:
            self.detect_named_entities()
        
        # Génération de résumés
        self.generate_product_summary()
        
        logger.info("="*60)
        logger.info("✓ PIPELINE NLP TERMINÉ")
        logger.info("="*60)
        
        return self.df


def main():
    """Test du module"""
    # Charger les données
    df = pd.read_csv('data/processed/cleaned_data.csv', encoding='utf-8-sig')
    
    # Analyser
    analyzer = AdvancedNLPAnalyzer(df)
    df_enriched = analyzer.execute_full_pipeline()
    
    # Sauvegarder
    df_enriched.to_csv('data/processed/nlp_enriched.csv', index=False, encoding='utf-8-sig')
    logger.info(f"✓ Données sauvegardées avec {len(df_enriched.columns)} colonnes")


if __name__ == "__main__":
    main()