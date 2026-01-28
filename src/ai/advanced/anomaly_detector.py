"""
Détecteur d'Anomalies ML - SmartMarketWatch
Description: Détection automatique d'anomalies dans les prix et caractéristiques
            en utilisant l'apprentissage automatique
Version: FINALE ULTIME - Tous bugs numpy et pandas corrigés
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path

try:
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("scikit-learn non installé - Détection d'anomalies désactivée")

try:
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    logging.warning("scipy non installé - Tests statistiques désactivés")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnomalyDetector:
    """Détecteur d'anomalies basé sur le Machine Learning"""
    
    def __init__(self, df):
        """
        Initialisation du détecteur
        
        Args:
            df (pd.DataFrame): DataFrame avec les données produits
        """
        self.df = df.copy()
        self.scaler = StandardScaler() if SKLEARN_AVAILABLE else None
        self.isolation_forest = None
        self.anomalies_detected = {}
        
    def detect_price_anomalies_statistical(self):
        """
        Détection d'anomalies de prix avec méthodes statistiques
        (Z-score, IQR)
        """
        logger.info("Détection d'anomalies de prix (statistiques)...")
        
        # Initialiser les colonnes pour tous les produits
        self.df['Anomalie_Prix_ZScore'] = False
        self.df['Anomalie_Prix_IQR'] = False
        self.df['Type_Anomalie_Prix'] = "Normal"
        
        nb_anomalies = 0
        
        # Calculer par gamme pour plus de précision
        for gamme in self.df['Gamme'].unique():
            if pd.isna(gamme) or gamme == 'Non classé':
                continue
            
            # Filtrer par gamme et prix non-nuls
            mask = (self.df['Gamme'] == gamme) & (self.df['Prix_Actuel_Clean'].notna())
            
            if mask.sum() < 3:  # Pas assez de données
                continue
            
            prix_serie = self.df.loc[mask, 'Prix_Actuel_Clean']
            
            # Méthode 1: Z-Score
            if SCIPY_AVAILABLE:
                z_scores_array = stats.zscore(prix_serie)
                # ✅ Convertir numpy array en Series pour avoir .loc
                z_scores = pd.Series(np.abs(z_scores_array), index=prix_serie.index)
                outliers_z = z_scores > 3
            else:
                mean = prix_serie.mean()
                std = prix_serie.std()
                if std > 0:
                    z_scores = np.abs(prix_serie - mean) / std
                    outliers_z = z_scores > 3
                else:
                    outliers_z = pd.Series([False] * len(prix_serie), index=prix_serie.index)
            
            # Méthode 2: IQR (Interquartile Range)
            Q1 = prix_serie.quantile(0.25)
            Q3 = prix_serie.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outliers_iqr = (prix_serie < lower_bound) | (prix_serie > upper_bound)
            
            # ✅ Utiliser .loc sur des Series pandas, pas des numpy arrays
            for idx in prix_serie.index:
                is_anomaly_z = bool(outliers_z.loc[idx]) if idx in outliers_z.index else False
                is_anomaly_iqr = bool(outliers_iqr.loc[idx]) if idx in outliers_iqr.index else False
                prix_val = prix_serie.loc[idx]
                
                # Mettre à jour le DataFrame principal
                self.df.loc[idx, 'Anomalie_Prix_ZScore'] = is_anomaly_z
                self.df.loc[idx, 'Anomalie_Prix_IQR'] = is_anomaly_iqr
                
                # Déterminer le type d'anomalie
                if is_anomaly_z or is_anomaly_iqr:
                    nb_anomalies += 1
                    if prix_val < lower_bound:
                        self.df.loc[idx, 'Type_Anomalie_Prix'] = f"Prix anormalement bas ({gamme})"
                    elif prix_val > upper_bound:
                        self.df.loc[idx, 'Type_Anomalie_Prix'] = f"Prix anormalement élevé ({gamme})"
                    else:
                        self.df.loc[idx, 'Type_Anomalie_Prix'] = f"Anomalie détectée ({gamme})"
        
        logger.info(f"✓ {nb_anomalies} anomalies de prix détectées")
        
        self.anomalies_detected['prix_statistical'] = nb_anomalies
        
        return self.df
    
    def detect_anomalies_isolation_forest(self):
        """
        Détection d'anomalies multivariée avec Isolation Forest
        """
        if not SKLEARN_AVAILABLE:
            logger.warning("⚠ scikit-learn non disponible - Isolation Forest ignoré")
            self.df['Anomalie_ML'] = False
            self.df['Anomalie_Score_ML'] = 0.0
            self.df['Anomalie_Score_Normalized'] = 0.5
            return self.df
        
        logger.info("Détection d'anomalies avec Isolation Forest...")
        
        # Sélectionner les features numériques pertinentes
        features = [
            'Prix_Actuel_Clean',
            'Rating_Clean',
            'RAM_GB',
            'Stockage_GB',
            'Generation_CPU',
            'Reduction_Reelle',
            'Performance_Index',
            'Score_Qualite'
        ]
        
        # Filtrer les features disponibles
        available_features = [f for f in features if f in self.df.columns]
        
        if len(available_features) == 0:
            logger.warning("⚠ Aucune feature disponible pour Isolation Forest")
            self.df['Anomalie_ML'] = False
            self.df['Anomalie_Score_ML'] = 0.0
            self.df['Anomalie_Score_Normalized'] = 0.5
            return self.df
        
        # Créer une copie avec seulement les lignes complètes
        df_for_ml = self.df[available_features].copy()
        
        # Remplir les NaN avec la médiane
        for col in available_features:
            if df_for_ml[col].isna().any():
                median_val = df_for_ml[col].median()
                df_for_ml[col].fillna(median_val, inplace=True)
        
        # Normaliser les données
        X_scaled = self.scaler.fit_transform(df_for_ml)
        
        # Entraîner Isolation Forest
        self.isolation_forest = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_estimators=100
        )
        
        # Prédire (-1 = anomalie, 1 = normal)
        predictions = self.isolation_forest.fit_predict(X_scaled)
        
        # Scores d'anomalie (plus négatif = plus anormal)
        anomaly_scores = self.isolation_forest.score_samples(X_scaled)
        
        # Ajouter au DataFrame
        self.df['Anomalie_ML'] = predictions == -1
        self.df['Anomalie_Score_ML'] = anomaly_scores
        
        # Normaliser le score entre 0 et 1
        min_score = anomaly_scores.min()
        max_score = anomaly_scores.max()
        if max_score > min_score:
            self.df['Anomalie_Score_Normalized'] = (anomaly_scores - min_score) / (max_score - min_score)
        else:
            self.df['Anomalie_Score_Normalized'] = 0.5
        
        nb_anomalies = (predictions == -1).sum()
        logger.info(f"✓ {nb_anomalies} anomalies ML détectées ({nb_anomalies/len(self.df)*100:.1f}%)")
        
        self.anomalies_detected['ml'] = nb_anomalies
        
        return self.df
    
    def detect_spec_price_inconsistencies(self):
        """
        Détecte les incohérences entre spécifications et prix
        """
        logger.info("Détection d'incohérences specs/prix...")
        
        inconsistencies = []
        severity_levels = []
        
        for idx, row in self.df.iterrows():
            issues = []
            severity = 0
            
            prix = row.get('Prix_Actuel_Clean')
            perf = row.get('Performance_Index')
            cpu = row.get('CPU')
            ram = row.get('RAM_GB')
            
            if pd.isna(prix):
                inconsistencies.append("Prix manquant")
                severity_levels.append(0)
                continue
            
            # === RÈGLE 1: Haute performance + prix bas ===
            if pd.notna(perf) and perf >= 80 and prix < 3000:
                issues.append("Haute perf mais prix bas")
                severity += 3
            
            # === RÈGLE 2: i7/i9 très bon marché ===
            if cpu in ['i7', 'i9', 'Ryzen 7', 'Ryzen 9'] and prix < 2500:
                issues.append("CPU premium sous-évalué")
                severity += 3
            
            # === RÈGLE 3: 32GB RAM à prix d'entrée ===
            if pd.notna(ram) and ram >= 32 and prix < 4000:
                issues.append("32GB RAM sous-évalué")
                severity += 2
            
            # === RÈGLE 4: Performance faible + prix élevé ===
            if pd.notna(perf) and perf <= 40 and prix > 4000:
                issues.append("Perf faible mais prix élevé")
                severity += 2
            
            # === RÈGLE 5: Celeron/Pentium surévalué ===
            if cpu in ['Celeron', 'Pentium'] and prix > 3000:
                issues.append("CPU entrée surévalué")
                severity += 2
            
            # === RÈGLE 6: Écart énorme avec ancien prix ===
            ancien_prix = row.get('Ancien_Prix_Clean')
            if pd.notna(ancien_prix) and ancien_prix > 0:
                ratio = prix / ancien_prix
                if ratio < 0.3:
                    issues.append("Réduction suspecte (>70%)")
                    severity += 1
            
            inconsistencies.append(" | ".join(issues) if issues else "Cohérent")
            severity_levels.append(severity)
        
        self.df['Incoherence_Spec_Prix'] = inconsistencies
        self.df['Severite_Incoherence'] = severity_levels
        
        nb_incoherences = sum(1 for s in severity_levels if s > 0)
        logger.info(f"✓ {nb_incoherences} incohérences détectées")
        
        self.anomalies_detected['inconsistencies'] = nb_incoherences
        
        return self.df
    
    def flag_suspicious_products(self):
        """
        Marque les produits suspects pour révision manuelle
        """
        logger.info("Marquage des produits suspects...")
        
        suspicion_flags = []
        suspicion_reasons = []
        
        for idx, row in self.df.iterrows():
            is_suspicious = False
            reasons = []
            
            # Critère 1: Anomalie ML détectée
            if row.get('Anomalie_ML') == True:
                is_suspicious = True
                reasons.append("Anomalie ML")
            
            # Critère 2: Anomalie prix statistique
            if row.get('Anomalie_Prix_ZScore') == True or row.get('Anomalie_Prix_IQR') == True:
                is_suspicious = True
                reasons.append("Anomalie prix")
            
            # Critère 3: Incohérence sévère
            if row.get('Severite_Incoherence', 0) >= 3:
                is_suspicious = True
                reasons.append("Incohérence majeure")
            
            # Critère 4: Données très incomplètes
            if row.get('Taux_Completude', 100) < 40:
                is_suspicious = True
                reasons.append("Données incomplètes")
            
            # Critère 5: Prix extrême
            prix = row.get('Prix_Actuel_Clean')
            if pd.notna(prix):
                if prix < 500 or prix > 20000:
                    is_suspicious = True
                    reasons.append("Prix extrême")
            
            suspicion_flags.append(is_suspicious)
            suspicion_reasons.append(" + ".join(reasons) if reasons else "OK")
        
        self.df['Produit_Suspect'] = suspicion_flags
        self.df['Raisons_Suspicion'] = suspicion_reasons
        
        nb_suspects = sum(suspicion_flags)
        logger.info(f"✓ {nb_suspects} produits suspects marqués ({nb_suspects/len(self.df)*100:.1f}%)")
        
        self.anomalies_detected['suspects'] = nb_suspects
        
        return self.df
    
    def generate_anomaly_report(self):
        """
        Génère un rapport détaillé sur les anomalies détectées
        """
        logger.info("Génération du rapport d'anomalies...")
        
        has_suspects = 'Produit_Suspect' in self.df.columns
        has_anomaly_score = 'Anomalie_Score_Normalized' in self.df.columns
        
        rapport = f"""
========================================
RAPPORT DE DÉTECTION D'ANOMALIES
========================================

RÉSUMÉ DES ANOMALIES DÉTECTÉES:
- Anomalies prix (statistiques):  {self.anomalies_detected.get('prix_statistical', 0)}
- Anomalies ML (Isolation Forest): {self.anomalies_detected.get('ml', 0)}
- Incohérences specs/prix:         {self.anomalies_detected.get('inconsistencies', 0)}
- Produits suspects (total):       {self.anomalies_detected.get('suspects', 0)}

"""
        
        if has_suspects and self.df['Produit_Suspect'].sum() > 0:
            rapport += f"""PRODUITS LES PLUS SUSPECTS:
{self.df[self.df['Produit_Suspect'] == True][['Titre', 'Prix_Actuel_Clean', 'Raisons_Suspicion']].head(10).to_string()}

STATISTIQUES D'ANOMALIES PAR GAMME:
{self.df.groupby('Gamme')['Produit_Suspect'].sum().to_string()}

"""
        
        if has_anomaly_score:
            rapport += f"""DISTRIBUTION DES SCORES D'ANOMALIE ML:
- Très anormal (<0.2):  {(self.df['Anomalie_Score_Normalized'] < 0.2).sum()}
- Anormal (0.2-0.4):    {((self.df['Anomalie_Score_Normalized'] >= 0.2) & (self.df['Anomalie_Score_Normalized'] < 0.4)).sum()}
- Normal (0.4-0.6):     {((self.df['Anomalie_Score_Normalized'] >= 0.4) & (self.df['Anomalie_Score_Normalized'] < 0.6)).sum()}
- Très normal (>0.6):   {(self.df['Anomalie_Score_Normalized'] >= 0.6).sum()}

"""
        
        rapport += "========================================"
        
        # Sauvegarder
        Path('data/reports').mkdir(parents=True, exist_ok=True)
        with open('data/reports/anomaly_report.txt', 'w', encoding='utf-8') as f:
            f.write(rapport)
        
        logger.info("✓ Rapport d'anomalies généré")
        print(rapport)
        
        return rapport
    
    def execute_full_pipeline(self):
        """
        Exécute toutes les détections d'anomalies
        """
        logger.info("="*60)
        logger.info("PIPELINE DÉTECTION D'ANOMALIES")
        logger.info("="*60)
        
        try:
            self.detect_price_anomalies_statistical()
        except Exception as e:
            logger.error(f"Erreur détection prix: {e}")
            import traceback
            traceback.print_exc()
            # Initialiser quand même les colonnes
            self.df['Anomalie_Prix_ZScore'] = False
            self.df['Anomalie_Prix_IQR'] = False
            self.df['Type_Anomalie_Prix'] = "Normal"
        
        try:
            if SKLEARN_AVAILABLE:
                self.detect_anomalies_isolation_forest()
            else:
                self.df['Anomalie_ML'] = False
                self.df['Anomalie_Score_ML'] = 0.0
                self.df['Anomalie_Score_Normalized'] = 0.5
        except Exception as e:
            logger.error(f"Erreur détection ML: {e}")
            import traceback
            traceback.print_exc()
        
        try:
            self.detect_spec_price_inconsistencies()
        except Exception as e:
            logger.error(f"Erreur détection incohérences: {e}")
            import traceback
            traceback.print_exc()
        
        try:
            self.flag_suspicious_products()
        except Exception as e:
            logger.error(f"Erreur marquage suspects: {e}")
            import traceback
            traceback.print_exc()
        
        try:
            self.generate_anomaly_report()
        except Exception as e:
            logger.error(f"Erreur génération rapport: {e}")
            import traceback
            traceback.print_exc()
        
        logger.info("="*60)
        logger.info("✓ DÉTECTION D'ANOMALIES TERMINÉE")
        logger.info("="*60)
        
        return self.df


def main():
    """Test du module"""
    df = pd.read_csv('data/processed/enriched_data.csv', encoding='utf-8-sig')
    
    detector = AnomalyDetector(df)
    df_with_anomalies = detector.execute_full_pipeline()
    
    df_with_anomalies.to_csv('data/processed/with_anomalies.csv', index=False, encoding='utf-8-sig')
    logger.info(f"✓ Données sauvegardées")


if __name__ == "__main__":
    main()