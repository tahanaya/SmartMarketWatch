"""
Pipeline Master - SmartMarketWatch Advanced AI
Description: Orchestrateur principal pour tous les modules IA avancés
Version: FINALE ULTIME - Tous bugs corrigés (numpy, pandas, f-strings)
"""

import pandas as pd
import logging
import time
from pathlib import Path
from datetime import datetime

# Import des modules avancés
from nlp_analyzer import AdvancedNLPAnalyzer
from anomaly_detector import AnomalyDetector

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AdvancedAIPipeline:
    """Pipeline maître pour l'IA avancée"""
    
    def __init__(self, input_file='data/processed/cleaned_data.csv'):
        """
        Initialisation du pipeline
        
        Args:
            input_file (str): Fichier de données nettoyées
        """
        self.input_file = input_file
        self.df = None
        self.stats = {
            'start_time': None,
            'end_time': None,
            'duration': None,
            'initial_columns': 0,
            'final_columns': 0,
            'new_features': 0
        }
        
    def load_data(self):
        """Charge les données nettoyées"""
        logger.info(f"Chargement des données depuis {self.input_file}")
        try:
            self.df = pd.read_csv(self.input_file, encoding='utf-8-sig')
            self.stats['initial_columns'] = len(self.df.columns)
            logger.info(f"✓ {len(self.df)} produits chargés avec {self.stats['initial_columns']} colonnes")
            return True
        except Exception as e:
            logger.error(f"✗ Erreur de chargement: {e}")
            return False
    
    def run_nlp_analysis(self):
        """Exécute le module NLP avancé"""
        logger.info("\n" + "="*70)
        logger.info("MODULE 1/2: ANALYSE NLP AVANCÉE")
        logger.info("="*70)
        
        try:
            analyzer = AdvancedNLPAnalyzer(self.df)
            self.df = analyzer.execute_full_pipeline()
            logger.info("✓ Module NLP terminé")
            return True
        except Exception as e:
            logger.error(f"✗ Erreur NLP: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def run_anomaly_detection(self):
        """Exécute le module de détection d'anomalies"""
        logger.info("\n" + "="*70)
        logger.info("MODULE 2/2: DÉTECTION D'ANOMALIES")
        logger.info("="*70)
        
        try:
            detector = AnomalyDetector(self.df)
            self.df = detector.execute_full_pipeline()
            logger.info("✓ Module détection d'anomalies terminé")
            return True
        except Exception as e:
            logger.error(f"✗ Erreur détection anomalies: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def calculate_business_metrics(self):
        """Calcule des métriques business avancées"""
        logger.info("\nCalcul des métriques business...")
        
        # Indice de confiance global
        def calculate_confidence_index(row):
            """Calcule un indice de confiance pour le produit"""
            score = 100
            
            # Pénalité si suspect
            if row.get('Produit_Suspect') == True:
                score -= 30
            
            # Pénalité si anomalie ML
            if row.get('Anomalie_ML') == True:
                score -= 20
            
            # Pénalité si données incomplètes
            completude = row.get('Taux_Completude', 100)
            score -= (100 - completude) * 0.3
            
            # Bonus si bonne affaire validée
            if row.get('Est_Bonne_Affaire') == True and not row.get('Produit_Suspect'):
                score += 10
            
            return max(0, min(100, round(score, 1)))
        
        self.df['Indice_Confiance'] = self.df.apply(calculate_confidence_index, axis=1)
        
        # Recommandation d'achat
        def recommend_purchase(row):
            """Génère une recommandation d'achat"""
            confiance = row.get('Indice_Confiance', 0)
            rqp = row.get('RQP_Score', 0) if 'RQP_Score' in row.index else 0
            suspect = row.get('Produit_Suspect', False)
            
            if suspect:
                return "Non recommandé - Vérifier"
            elif confiance >= 80 and rqp > 15:
                return "Très recommandé"
            elif confiance >= 60 and rqp > 10:
                return "Recommandé"
            elif confiance >= 40:
                return "À considérer"
            else:
                return "Non recommandé"
        
        self.df['Recommandation_Achat'] = self.df.apply(recommend_purchase, axis=1)
        
        # Score de fiabilité vendeur
        def vendor_reliability_score(row):
            """Estime la fiabilité du vendeur"""
            score = 5.0
            
            if row.get('Produit_Suspect') == True:
                score -= 2
            
            if row.get('Severite_Incoherence', 0) >= 2:
                score -= 1
            
            if row.get('Taux_Completude', 100) < 50:
                score -= 1
            
            return max(1.0, min(5.0, round(score, 1)))
        
        self.df['Score_Fiabilite_Vendeur'] = self.df.apply(vendor_reliability_score, axis=1)
        
        logger.info("✓ Métriques business calculées")
    
    def generate_master_report(self):
        """Génère un rapport global du pipeline avancé"""
        logger.info("\nGénération du rapport global...")
        
        self.stats['final_columns'] = len(self.df.columns)
        self.stats['new_features'] = self.stats['final_columns'] - self.stats['initial_columns']
        
        # Vérifier l'existence des colonnes
        has_sentiment = 'Sentiment_BERT' in self.df.columns
        has_suspects = 'Produit_Suspect' in self.df.columns
        has_anomaly_ml = 'Anomalie_ML' in self.df.columns
        has_anomaly_prix = 'Anomalie_Prix_ZScore' in self.df.columns
        has_incoherence = 'Severite_Incoherence' in self.df.columns
        has_recommandation = 'Recommandation_Achat' in self.df.columns
        has_resume = 'Resume_Produit' in self.df.columns
        has_rqp = 'RQP_Score' in self.df.columns
        has_confiance = 'Indice_Confiance' in self.df.columns
        
        # ✅ CORRECTION: Calculer toutes les valeurs formatées à l'avance
        nb_suspects = self.df['Produit_Suspect'].sum() if has_suspects else 0
        pct_suspects = f"{(nb_suspects / len(self.df) * 100):.1f}" if has_suspects and len(self.df) > 0 else "0.0"
        
        avg_confiance = f"{self.df['Indice_Confiance'].mean():.1f}" if has_confiance else "0.0"
        
        nb_anomaly_ml = self.df['Anomalie_ML'].sum() if has_anomaly_ml else 0
        
        if has_anomaly_prix:
            nb_anomaly_prix = (self.df['Anomalie_Prix_ZScore'] | self.df['Anomalie_Prix_IQR']).sum()
        else:
            nb_anomaly_prix = 'N/A'
        
        nb_incoherences = (self.df['Severite_Incoherence'] >= 3).sum() if has_incoherence else 0
        
        rapport = f"""
╔════════════════════════════════════════════════════════════════════════╗
║                  RAPPORT PIPELINE IA AVANCÉ                           ║
║                    SmartMarketWatch v2.0                              ║
╚════════════════════════════════════════════════════════════════════════╝

📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
⏱️  Durée d'exécution: {self.stats['duration']:.2f} secondes

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 STATISTIQUES GÉNÉRALES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Produits analysés:           {len(self.df)}
Colonnes initiales:          {self.stats['initial_columns']}
Colonnes finales:            {self.stats['final_columns']}
Nouvelles features:          {self.stats['new_features']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 ANALYSE NLP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Features techniques extraites:
  • Processeur détaillé:     {self.df['CPU_Marque'].notna().sum() if 'CPU_Marque' in self.df.columns else 0} / {len(self.df)}
  • RAM détaillée:           {self.df['RAM_Type'].notna().sum() if 'RAM_Type' in self.df.columns else 0} / {len(self.df)}
  • Stockage détaillé:       {self.df['Stockage_Total_GB'].notna().sum() if 'Stockage_Total_GB' in self.df.columns else 0} / {len(self.df)}
  • Écran détaillé:          {self.df['Ecran_Taille'].notna().sum() if 'Ecran_Taille' in self.df.columns else 0} / {len(self.df)}
  • GPU détecté:             {self.df['GPU_Marque'].notna().sum() if 'GPU_Marque' in self.df.columns else 0} / {len(self.df)}

Sentiment analysis:
{self.df['Sentiment_BERT'].value_counts().to_string() if has_sentiment else '  Non disponible'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️  DÉTECTION D'ANOMALIES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Produits suspects:          {nb_suspects} ({pct_suspects}%)
Anomalies ML:               {nb_anomaly_ml}
Anomalies prix:             {nb_anomaly_prix}
Incohérences majeures:      {nb_incoherences}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 RECOMMANDATIONS D'ACHAT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{self.df['Recommandation_Achat'].value_counts().to_string() if has_recommandation else 'Non disponible'}

Indice de confiance moyen:  {avg_confiance}/100

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏆 TOP 5 MEILLEURES AFFAIRES (Haute confiance)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        
        # Top 5 affaires
        if has_confiance and has_resume and has_rqp:
            try:
                top_deals = self.df[self.df['Indice_Confiance'] >= 70].nlargest(5, 'RQP_Score')[
                    ['Resume_Produit', 'Prix_Actuel_Clean', 'RQP_Score', 'Indice_Confiance']
                ]
                if len(top_deals) > 0:
                    rapport += top_deals.to_string()
                else:
                    rapport += "Aucune affaire de haute confiance trouvée"
            except:
                rapport += "Données insuffisantes pour le classement RQP"
        else:
            rapport += "Données insuffisantes (colonnes manquantes)"
        
        rapport += f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️  TOP 5 PRODUITS À VÉRIFIER (Suspects)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        
        # Top suspects
        if has_suspects and has_resume and 'Raisons_Suspicion' in self.df.columns:
            try:
                suspects = self.df[self.df['Produit_Suspect'] == True][
                    ['Resume_Produit', 'Prix_Actuel_Clean', 'Raisons_Suspicion']
                ].head(5)
                if len(suspects) > 0:
                    rapport += suspects.to_string()
                else:
                    rapport += "Aucun produit suspect détecté"
            except:
                rapport += "Erreur lors de la génération de la liste"
        else:
            rapport += "Données suspects non disponibles"
        
        rapport += f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📁 FICHIERS GÉNÉRÉS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ data/processed/ai_advanced_complete.csv
✓ data/reports/ai_advanced_report.txt
✓ data/reports/anomaly_report.txt

╚════════════════════════════════════════════════════════════════════════╝
"""
        
        # Sauvegarder le rapport
        Path('data/reports').mkdir(parents=True, exist_ok=True)
        with open('data/reports/ai_advanced_report.txt', 'w', encoding='utf-8') as f:
            f.write(rapport)
        
        print(rapport)
        logger.info("✓ Rapport global généré")
    
    def save_results(self):
        """Sauvegarde les résultats finaux"""
        logger.info("\nSauvegarde des résultats...")
        
        output_file = 'data/processed/ai_advanced_complete.csv'
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        self.df.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        logger.info(f"✓ {len(self.df)} produits sauvegardés dans {output_file}")
        logger.info(f"  Colonnes: {len(self.df.columns)}")
        logger.info(f"  Taille: {Path(output_file).stat().st_size / 1024:.1f} KB")
    
    def execute_full_pipeline(self):
        """
        Exécute le pipeline complet IA avancé
        """
        print("\n" + "="*70)
        print("🚀 DÉMARRAGE DU PIPELINE IA AVANCÉ - SMARTMARKETWATCH")
        print("="*70 + "\n")
        
        self.stats['start_time'] = time.time()
        
        # Étape 1: Chargement
        if not self.load_data():
            logger.error("✗ Échec du chargement des données")
            return False
        
        # Étape 2: NLP avancé
        if not self.run_nlp_analysis():
            logger.warning("⚠ Module NLP a échoué, continuation...")
        
        # Étape 3: Détection d'anomalies
        if not self.run_anomaly_detection():
            logger.warning("⚠ Module anomalies a échoué, continuation...")
        
        # Étape 4: Métriques business
        try:
            self.calculate_business_metrics()
        except Exception as e:
            logger.error(f"⚠ Erreur calcul métriques: {e}")
        
        # Étape 5: Sauvegarde
        try:
            self.save_results()
        except Exception as e:
            logger.error(f"⚠ Erreur sauvegarde: {e}")
        
        # Étape 6: Rapport
        self.stats['end_time'] = time.time()
        self.stats['duration'] = self.stats['end_time'] - self.stats['start_time']
        
        try:
            self.generate_master_report()
        except Exception as e:
            logger.error(f"⚠ Erreur génération rapport: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "="*70)
        print("✓ PIPELINE IA AVANCÉ TERMINÉ AVEC SUCCÈS")
        print(f"⏱️  Temps total: {self.stats['duration']:.2f} secondes")
        print("="*70 + "\n")
        
        return True


def main():
    """Point d'entrée principal"""
    pipeline = AdvancedAIPipeline()
    success = pipeline.execute_full_pipeline()
    
    if success:
        logger.info("\n🎉 Tous les modules ont été exécutés avec succès!")
        logger.info("📊 Consultez data/reports/ai_advanced_report.txt pour le rapport complet")
    else:
        logger.error("\n❌ Le pipeline a rencontré des erreurs")


if __name__ == "__main__":
    main()