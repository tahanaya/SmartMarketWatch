"""
Module d'Extraction de Features Avancées - SmartMarketWatch
Responsable: Équipe IA (Membre 2)
Description: Analyse de sentiment et création d'indicateurs avancés
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path

# Pour l'analyse de sentiment (optionnel si vous avez des commentaires)
try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False
    logging.warning("TextBlob non installé - Analyse de sentiment désactivée")

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FeatureExtractor:
    """Classe pour l'extraction de features avancées"""
    
    def __init__(self, input_file='data/processed/cleaned_data.csv'):
        """
        Initialisation de l'extracteur
        
        Args:
            input_file (str): Chemin vers les données nettoyées
        """
        self.input_file = input_file
        self.df = None
        
    def charger_donnees(self):
        """Charge les données nettoyées"""
        try:
            logger.info(f"Chargement des données depuis {self.input_file}")
            self.df = pd.read_csv(self.input_file, encoding='utf-8-sig')
            logger.info(f"✓ {len(self.df)} produits chargés")
            return True
        except Exception as e:
            logger.error(f"✗ Erreur lors du chargement: {e}")
            return False
    
    def calculer_score_performance(self):
        """
        Calcule un indice de performance basé sur les specs
        Crée la colonne: Performance_Index (0-100)
        """
        logger.info("Calcul de l'indice de performance...")
        
        # Dictionnaires de scores
        cpu_scores = {
            'i9': 100, 'Ryzen 9': 100,
            'i7': 85, 'Ryzen 7': 85,
            'i5': 60, 'Ryzen 5': 60,
            'i3': 35, 'Ryzen 3': 35,
            'Pentium': 20,
            'Celeron': 10,
            'Autre': 0
        }
        
        def calculer_score(row):
            """Calcule le score de performance"""
            score = 0
            
            # Score CPU (40 points max)
            cpu_score = cpu_scores.get(row['CPU'], 0)
            score += cpu_score * 0.4
            
            # Score RAM (30 points max)
            ram = row['RAM_GB']
            if pd.notna(ram):
                if ram >= 32:
                    score += 30
                elif ram >= 16:
                    score += 25
                elif ram >= 8:
                    score += 18
                elif ram >= 4:
                    score += 10
            
            # Score Stockage (20 points max)
            stockage = row['Stockage_GB']
            type_stockage = row['Type_Stockage']
            if pd.notna(stockage):
                if stockage >= 512:
                    score += 15
                elif stockage >= 256:
                    score += 10
                elif stockage >= 128:
                    score += 5
                
                if type_stockage == 'SSD':
                    score += 5
            
            # Score Génération (10 points max)
            gen = row['Generation_CPU']
            if pd.notna(gen):
                if gen >= 11:
                    score += 10
                elif gen >= 8:
                    score += 7
                elif gen >= 6:
                    score += 4
                elif gen >= 4:
                    score += 2
            
            return min(round(score, 1), 100)  # Plafonner à 100
        
        self.df['Performance_Index'] = self.df.apply(calculer_score, axis=1)
        
        logger.info(f"✓ Performance moyenne: {self.df['Performance_Index'].mean():.1f}/100")
    
    def calculer_score_qualite(self):
        """
        Calcule un score de qualité global pour chaque produit
        Crée la colonne: Score_Qualite (0-100)
        """
        logger.info("Calcul du score de qualité...")
        
        def calculer_score(row):
            """Calcule le score de qualité global"""
            score = 0
            
            # 1. Performance (40%)
            score += row['Performance_Index'] * 0.40
            
            # 2. Rating (30%)
            if pd.notna(row['Rating_Clean']):
                score += (row['Rating_Clean'] / 5) * 30
            
            # 3. Complétude (15%)
            score += (row['Taux_Completude'] / 100) * 15
            
            # 4. État du produit (10%)
            etat_scores = {
                'Neuf': 10,
                'Remis à neuf': 7,
                'Occasion': 4,
                'Non spécifié': 2
            }
            score += etat_scores.get(row['Etat_Produit'], 0)
            
            # 5. Bonus réduction (5%)
            if pd.notna(row['Reduction_Reelle']) and row['Reduction_Reelle'] > 0:
                bonus_reduction = min(row['Reduction_Reelle'] / 20, 5)  # Max 5 points
                score += bonus_reduction
            
            return min(round(score, 1), 100)
        
        self.df['Score_Qualite'] = self.df.apply(calculer_score, axis=1)
        
        logger.info(f"✓ Score qualité moyen: {self.df['Score_Qualite'].mean():.1f}/100")
    
    def calculer_rapport_qualite_prix(self):
        """
        Calcule le rapport qualité/prix
        Crée la colonne: RQP_Score (plus c'est élevé, meilleure est l'affaire)
        """
        logger.info("Calcul du rapport qualité/prix...")
        
        def calculer_rqp(row):
            """Calcule le ratio qualité/prix"""
            if pd.isna(row['Prix_Actuel_Clean']) or row['Prix_Actuel_Clean'] == 0:
                return 0
            
            return round((row['Score_Qualite'] / row['Prix_Actuel_Clean']) * 1000, 2)
        
        self.df['RQP_Score'] = self.df.apply(calculer_rqp, axis=1)
        
        logger.info(f"✓ RQP moyen: {self.df['RQP_Score'].mean():.2f}")
    
    def detecter_bonnes_affaires(self):
        """
        Identifie les bonnes affaires
        Crée les colonnes: Est_Bonne_Affaire, Type_Affaire
        """
        logger.info("Détection des bonnes affaires...")
        
        # Calculer les quartiles du RQP
        q75 = self.df['RQP_Score'].quantile(0.75)
        q90 = self.df['RQP_Score'].quantile(0.90)
        
        def classifier_affaire(row):
            """Classifie le type d'affaire"""
            rqp = row['RQP_Score']
            reduction = row['Reduction_Reelle']
            score = row['Score_Qualite']
            
            # Excellente affaire
            if rqp >= q90 and score >= 70:
                return True, "Excellente affaire"
            
            # Bonne affaire
            elif rqp >= q75 and score >= 60:
                return True, "Bonne affaire"
            
            # Promotion intéressante
            elif pd.notna(reduction) and reduction >= 40 and score >= 50:
                return True, "Promotion intéressante"
            
            # Affaire standard
            else:
                return False, "Standard"
        
        affaires = self.df.apply(classifier_affaire, axis=1)
        self.df['Est_Bonne_Affaire'] = affaires.apply(lambda x: x[0])
        self.df['Type_Affaire'] = affaires.apply(lambda x: x[1])
        
        nb_bonnes_affaires = self.df['Est_Bonne_Affaire'].sum()
        logger.info(f"✓ {nb_bonnes_affaires} bonnes affaires détectées")
    
    def detecter_anomalies_prix(self):
        """
        Détecte les anomalies de prix (trop bas ou trop élevé)
        Crée les colonnes: Anomalie_Prix, Type_Anomalie
        """
        logger.info("Détection des anomalies de prix...")
        
        anomalies = []
        types_anomalies = []
        
        for idx, row in self.df.iterrows():
            prix = row['Prix_Actuel_Clean']
            performance = row['Performance_Index']
            gamme = row['Gamme']
            
            est_anomalie = False
            type_anomalie = "Normal"
            
            # Anomalie 1: Prix trop bas pour les specs
            if pd.notna(prix) and pd.notna(performance):
                if performance >= 80 and prix < 3000:
                    est_anomalie = True
                    type_anomalie = "Prix suspect (trop bas)"
                
                elif performance <= 30 and prix > 4000:
                    est_anomalie = True
                    type_anomalie = "Prix suspect (trop élevé)"
            
            # Anomalie 2: Incohérence gamme/prix
            if gamme == "Haut de gamme" and pd.notna(prix) and prix < 2500:
                est_anomalie = True
                type_anomalie = "Incohérence gamme/prix"
            
            anomalies.append(est_anomalie)
            types_anomalies.append(type_anomalie)
        
        self.df['Anomalie_Prix'] = anomalies
        self.df['Type_Anomalie'] = types_anomalies
        
        nb_anomalies = sum(anomalies)
        logger.info(f"✓ {nb_anomalies} anomalies de prix détectées")
    
    def analyser_sentiment_description(self):
        """
        Analyse de sentiment sur les titres/descriptions
        Crée les colonnes: Sentiment_Score, Sentiment_Label
        
        Note: Cette fonction nécessite TextBlob (optionnel)
        """
        if not TEXTBLOB_AVAILABLE:
            logger.warning("⚠ TextBlob non disponible - Analyse de sentiment ignorée")
            self.df['Sentiment_Score'] = 0.0
            self.df['Sentiment_Label'] = 'Neutre'
            return
        
        logger.info("Analyse de sentiment des descriptions...")
        
        def analyser_sentiment(texte):
            """Analyse le sentiment d'un texte"""
            try:
                # Créer un blob de texte
                blob = TextBlob(str(texte))
                
                # Calculer la polarité (-1 à +1)
                polarite = blob.sentiment.polarity
                
                # Classifier
                if polarite > 0.2:
                    label = "Positif"
                elif polarite < -0.2:
                    label = "Négatif"
                else:
                    label = "Neutre"
                
                return polarite, label
            except:
                return 0.0, "Neutre"
        
        sentiments = self.df['Titre'].apply(analyser_sentiment)
        self.df['Sentiment_Score'] = sentiments.apply(lambda x: round(x[0], 3))
        self.df['Sentiment_Label'] = sentiments.apply(lambda x: x[1])
        
        repartition = self.df['Sentiment_Label'].value_counts()
        logger.info(f"✓ Sentiments: {repartition.to_dict()}")
    
    def creer_tags_produit(self):
        """
        Crée des tags automatiques pour chaque produit
        Crée la colonne: Tags
        """
        logger.info("Création des tags produits...")
        
        def generer_tags(row):
            """Génère une liste de tags"""
            tags = []
            
            # Tag de gamme
            tags.append(row['Gamme'])
            
            # Tag de marque
            if row['Marque'] != 'Autre':
                tags.append(row['Marque'])
            
            # Tag de performance
            if row['Performance_Index'] >= 80:
                tags.append("Haute performance")
            elif row['Performance_Index'] >= 50:
                tags.append("Performance correcte")
            
            # Tag d'état
            tags.append(row['Etat_Produit'])
            
            # Tag de stockage
            if row['Type_Stockage'] == 'SSD':
                tags.append("SSD")
            
            # Tag de bonne affaire
            if row['Est_Bonne_Affaire']:
                tags.append("Bonne affaire")
            
            # Tag de promotion
            if pd.notna(row['Reduction_Reelle']) and row['Reduction_Reelle'] >= 30:
                tags.append("Promotion")
            
            return ", ".join(tags)
        
        self.df['Tags'] = self.df.apply(generer_tags, axis=1)
        
        logger.info("✓ Tags générés")
    
    def sauvegarder_donnees_enrichies(self, output_file='data/processed/enriched_data.csv'):
        """
        Sauvegarde les données enrichies
        
        Args:
            output_file (str): Chemin du fichier de sortie
        """
        logger.info(f"Sauvegarde des données enrichies...")
        
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        self.df.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        logger.info(f"✓ {len(self.df)} produits enrichis sauvegardés dans {output_file}")
    
    def executer_pipeline_complet(self):
        """
        Exécute toutes les étapes d'enrichissement
        """
        logger.info("="*60)
        logger.info("DÉMARRAGE DU PIPELINE D'ENRICHISSEMENT")
        logger.info("="*60)
        
        etapes = [
            ("Chargement des données", self.charger_donnees),
            ("Calcul de la performance", self.calculer_score_performance),
            ("Calcul du score qualité", self.calculer_score_qualite),
            ("Calcul rapport qualité/prix", self.calculer_rapport_qualite_prix),
            ("Détection bonnes affaires", self.detecter_bonnes_affaires),
            ("Détection anomalies prix", self.detecter_anomalies_prix),
            ("Analyse de sentiment", self.analyser_sentiment_description),
            ("Création des tags", self.creer_tags_produit),
            ("Sauvegarde", self.sauvegarder_donnees_enrichies)
        ]
        
        for i, (nom, fonction) in enumerate(etapes, 1):
            logger.info(f"\n[{i}/{len(etapes)}] {nom}...")
            try:
                resultat = fonction()
                if resultat is False:
                    logger.error(f"✗ Échec de l'étape: {nom}")
                    return False
            except Exception as e:
                logger.error(f"✗ Erreur dans {nom}: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        logger.info("\n" + "="*60)
        logger.info("✓ PIPELINE D'ENRICHISSEMENT TERMINÉ")
        logger.info("="*60)
        return True


def main():
    """Point d'entrée principal"""
    extractor = FeatureExtractor()
    extractor.executer_pipeline_complet()


if __name__ == "__main__":
    main()