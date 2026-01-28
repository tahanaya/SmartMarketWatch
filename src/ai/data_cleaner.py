"""
Module de Nettoyage des Données - SmartMarketWatch
Responsable: Équipe IA (Membre 2)
Description: Nettoyage et standardisation des données brutes collectées par le module RPA
"""

import pandas as pd
import re
import logging
from datetime import datetime
from pathlib import Path

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/data_cleaner.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DataCleaner:
    """Classe principale pour le nettoyage des données"""
    
    def __init__(self, input_file='data/raw/raw_data.csv'):
        """
        Initialisation du nettoyeur
        
        Args:
            input_file (str): Chemin vers le fichier CSV brut
        """
        self.input_file = input_file
        self.df = None
        self.stats = {
            'produits_initiaux': 0,
            'doublons_supprimes': 0,
            'accessoires_filtres': 0,
            'valeurs_manquantes_traitees': 0,
            'produits_finaux': 0
        }
        
    def charger_donnees(self):
        """Charge les données brutes depuis le CSV"""
        try:
            logger.info(f"Chargement des données depuis {self.input_file}")
            self.df = pd.read_csv(self.input_file, encoding='utf-8-sig')
            self.stats['produits_initiaux'] = len(self.df)
            logger.info(f"✓ {self.stats['produits_initiaux']} produits chargés")
            return True
        except Exception as e:
            logger.error(f"✗ Erreur lors du chargement: {e}")
            return False
    
    def nettoyer_prix(self):
        """
        Convertit les prix du format '1,389.00 Dhs' en nombres décimaux
        Crée deux nouvelles colonnes: Prix_Actuel_Clean et Ancien_Prix_Clean
        """
        logger.info("Nettoyage des prix...")
        
        def extraire_prix(prix_str):
            """Extrait le nombre d'une chaîne de prix"""
            if pd.isna(prix_str) or prix_str == '':
                return None
            try:
                # Supprime tout sauf les chiffres, virgules et points
                prix_clean = re.sub(r'[^\d,.]', '', str(prix_str))
                # Remplace la virgule par rien (format français: 1,389.00 → 1389.00)
                prix_clean = prix_clean.replace(',', '')
                return float(prix_clean)
            except:
                return None
        
        # Nettoyage du prix actuel
        self.df['Prix_Actuel_Clean'] = self.df['Prix_Actuel'].apply(extraire_prix)
        
        # Nettoyage de l'ancien prix
        self.df['Ancien_Prix_Clean'] = self.df['Ancien_Prix'].apply(extraire_prix)
        
        # Calcul de la réduction réelle - CORRECTION
        def calculer_reduction(row):
            """Calcule le pourcentage de réduction"""
            ancien = row['Ancien_Prix_Clean']
            actuel = row['Prix_Actuel_Clean']
            
            if pd.isna(ancien) or pd.isna(actuel) or ancien <= 0:
                return 0.0
            
            reduction = ((ancien - actuel) / ancien) * 100
            return round(reduction, 2)
        
        self.df['Reduction_Reelle'] = self.df.apply(calculer_reduction, axis=1)
        
        logger.info(f"✓ Prix nettoyés - Moyenne: {self.df['Prix_Actuel_Clean'].mean():.2f} Dhs")
        
    def nettoyer_rating(self):
        """
        Convertit les ratings du format '4.5 out of 5' en nombres décimaux
        Crée la colonne: Rating_Clean
        """
        logger.info("Nettoyage des ratings...")
        
        def extraire_rating(rating_str):
            """Extrait la note numérique"""
            if pd.isna(rating_str) or rating_str == '':
                return None
            try:
                # Cherche un pattern comme "4.5 out of 5" ou "4 out of 5"
                match = re.search(r'(\d+\.?\d*)\s*out of', str(rating_str))
                if match:
                    return float(match.group(1))
                return None
            except:
                return None
        
        self.df['Rating_Clean'] = self.df['Rating'].apply(extraire_rating)
        
        # Statistiques
        ratings_disponibles = self.df['Rating_Clean'].notna().sum()
        logger.info(f"✓ Ratings nettoyés - {ratings_disponibles} notes disponibles")
        
    def extraire_marque(self):
        """
        Extrait la marque du produit depuis le titre
        Crée la colonne: Marque
        """
        logger.info("Extraction des marques...")
        
        marques_connues = [
            'HP', 'DELL', 'LENOVO', 'ASUS', 'ACER', 'APPLE', 'SAMSUNG', 
            'MSI', 'TOSHIBA', 'HUAWEI', 'XIAOMI', 'MICROSOFT', 'LOGITECH'
        ]
        
        def detecter_marque(titre):
            """Détecte la marque dans le titre"""
            titre_upper = str(titre).upper()
            for marque in marques_connues:
                if marque in titre_upper:
                    return marque.title()
            return 'Autre'
        
        self.df['Marque'] = self.df['Titre'].apply(detecter_marque)
        
        # Statistiques par marque
        repartition = self.df['Marque'].value_counts()
        logger.info(f"✓ Marques extraites - Top 3: {repartition.head(3).to_dict()}")
        
    def extraire_specs_techniques(self):
        """
        Extrait les spécifications techniques depuis le titre
        Crée les colonnes: CPU, Generation_CPU, RAM_GB, Stockage_GB, Type_Stockage
        """
        logger.info("Extraction des spécifications techniques...")
        
        # Extraction du CPU
        def extraire_cpu(titre):
            """Détecte le type de processeur"""
            titre_upper = str(titre).upper()
            if 'I9' in titre_upper or 'CORE I9' in titre_upper:
                return 'i9'
            elif 'I7' in titre_upper or 'CORE I7' in titre_upper:
                return 'i7'
            elif 'I5' in titre_upper or 'CORE I5' in titre_upper:
                return 'i5'
            elif 'I3' in titre_upper or 'CORE I3' in titre_upper:
                return 'i3'
            elif 'RYZEN 9' in titre_upper:
                return 'Ryzen 9'
            elif 'RYZEN 7' in titre_upper:
                return 'Ryzen 7'
            elif 'RYZEN 5' in titre_upper:
                return 'Ryzen 5'
            elif 'RYZEN 3' in titre_upper:
                return 'Ryzen 3'
            elif 'CELERON' in titre_upper:
                return 'Celeron'
            elif 'PENTIUM' in titre_upper:
                return 'Pentium'
            return 'Autre'
        
        # Extraction de la génération CPU
        def extraire_generation(titre):
            """Détecte la génération du processeur"""
            match = re.search(r'(\d+)[èeÈE]?[mM]?[eE]?\s*[Gg](?:[éeÉE]n(?:[éeÉE]ration)?)?', str(titre))
            if match:
                return int(match.group(1))
            return None
        
        # Extraction de la RAM
        def extraire_ram(titre):
            """Détecte la capacité RAM en GB"""
            match = re.search(r'(\d+)\s*[Gg][Bb]?\s*(?:RAM|DDR)', str(titre), re.IGNORECASE)
            if match:
                return int(match.group(1))
            return None
        
        # Extraction du stockage
        def extraire_stockage(titre):
            """Détecte la capacité et le type de stockage"""
            # Cherche SSD
            ssd_match = re.search(r'(\d+)\s*[Gg][Bb]?\s*SSD', str(titre), re.IGNORECASE)
            if ssd_match:
                return int(ssd_match.group(1)), 'SSD'
            
            # Cherche HDD
            hdd_match = re.search(r'(\d+)\s*[Gg][Bb]?\s*(?:HDD|GO)', str(titre), re.IGNORECASE)
            if hdd_match:
                return int(hdd_match.group(1)), 'HDD'
            
            # Cherche format "500Go" ou "1TB"
            storage_match = re.search(r'(\d+)\s*(?:GB|Go|TB|To)', str(titre), re.IGNORECASE)
            if storage_match:
                capacite = int(storage_match.group(1))
                if 'TB' in str(titre).upper() or 'TO' in str(titre).upper():
                    capacite *= 1024  # Convertir TB en GB
                return capacite, 'Inconnu'
            
            return None, None
        
        # Application des fonctions
        self.df['CPU'] = self.df['Titre'].apply(extraire_cpu)
        self.df['Generation_CPU'] = self.df['Titre'].apply(extraire_generation)
        self.df['RAM_GB'] = self.df['Titre'].apply(extraire_ram)
        
        stockage_data = self.df['Titre'].apply(extraire_stockage)
        self.df['Stockage_GB'] = stockage_data.apply(lambda x: x[0] if x[0] is not None else None)
        self.df['Type_Stockage'] = stockage_data.apply(lambda x: x[1] if x[1] is not None else None)
        
        logger.info(f"✓ Spécifications extraites")
        
    def detecter_etat_produit(self):
        """
        Détecte l'état du produit (Neuf, Remis à neuf, Occasion)
        Crée la colonne: Etat_Produit
        """
        logger.info("Détection de l'état des produits...")
        
        def classifier_etat(titre):
            """Classifie l'état du produit"""
            titre_lower = str(titre).lower()
            if 'remis' in titre_lower or 'reconditionn' in titre_lower or 'refurbished' in titre_lower:
                return 'Remis à neuf'
            elif 'occasion' in titre_lower or 'used' in titre_lower:
                return 'Occasion'
            elif 'neuf' in titre_lower or 'new' in titre_lower:
                return 'Neuf'
            return 'Non spécifié'
        
        self.df['Etat_Produit'] = self.df['Titre'].apply(classifier_etat)
        
        repartition = self.df['Etat_Produit'].value_counts()
        logger.info(f"✓ États détectés: {repartition.to_dict()}")
        
    def filtrer_accessoires(self):
        """
        Filtre les accessoires pour ne garder que les PC portables
        """
        logger.info("Filtrage des accessoires...")
        
        mots_cles_accessoires = [
            'souris', 'clavier', 'sac', 'sacoche', 'cartable', 'support', 
            'tapis', 'chargeur', 'câble', 'adaptateur', 'écran', 'moniteur',
            'enceinte', 'haut-parleur', 'casque', 'webcam', 'hub', 'station',
            'refroidisseur', 'ventilateur', 'lampe', 'stickers', 'autocollant'
        ]
        
        def est_accessoire(titre):
            """Vérifie si le produit est un accessoire"""
            titre_lower = str(titre).lower()
            return any(mot in titre_lower for mot in mots_cles_accessoires)
        
        accessoires = self.df[self.df['Titre'].apply(est_accessoire)]
        self.stats['accessoires_filtres'] = len(accessoires)
        
        self.df = self.df[~self.df['Titre'].apply(est_accessoire)]
        
        logger.info(f"✓ {self.stats['accessoires_filtres']} accessoires filtrés")
        
    def supprimer_doublons(self):
        """
        Supprime les doublons basés sur l'URL de l'image
        """
        logger.info("Suppression des doublons...")
        
        nb_avant = len(self.df)
        self.df = self.df.drop_duplicates(subset=['Image_URL'], keep='first')
        nb_apres = len(self.df)
        
        self.stats['doublons_supprimes'] = nb_avant - nb_apres
        logger.info(f"✓ {self.stats['doublons_supprimes']} doublons supprimés")
        
    def calculer_completude(self):
        """
        Calcule un score de complétude pour chaque produit
        Crée la colonne: Taux_Completude
        """
        logger.info("Calcul de la complétude des données...")
        
        colonnes_importantes = [
            'Prix_Actuel_Clean', 'Marque', 'CPU', 'RAM_GB', 
            'Stockage_GB', 'Rating_Clean'
        ]
        
        def calculer_score(row):
            """Calcule le % de champs remplis"""
            remplis = sum(1 for col in colonnes_importantes if pd.notna(row[col]))
            return round((remplis / len(colonnes_importantes)) * 100, 1)
        
        self.df['Taux_Completude'] = self.df.apply(calculer_score, axis=1)
        
        moyenne_completude = self.df['Taux_Completude'].mean()
        logger.info(f"✓ Complétude moyenne: {moyenne_completude:.1f}%")
        
    def classifier_par_gamme(self):
        """
        Classifie les produits par gamme (Entrée, Milieu, Haut de gamme)
        Crée la colonne: Gamme
        """
        logger.info("Classification par gamme...")
        
        def determiner_gamme(row):
            """Détermine la gamme du produit"""
            prix = row['Prix_Actuel_Clean']
            cpu = row['CPU']
            ram = row['RAM_GB']
            
            # Si données manquantes, classification par prix uniquement
            if pd.isna(prix):
                return 'Non classé'
            
            # Haut de gamme
            if prix > 5000 or cpu in ['i7', 'i9', 'Ryzen 7', 'Ryzen 9'] or (pd.notna(ram) and ram >= 16):
                return 'Haut de gamme'
            
            # Entrée de gamme
            elif prix < 2500 or cpu in ['Celeron', 'Pentium', 'i3'] or (pd.notna(ram) and ram <= 4):
                return 'Entrée de gamme'
            
            # Milieu de gamme
            else:
                return 'Milieu de gamme'
        
        self.df['Gamme'] = self.df.apply(determiner_gamme, axis=1)
        
        repartition = self.df['Gamme'].value_counts()
        logger.info(f"✓ Gammes: {repartition.to_dict()}")
        
    def generer_rapport_qualite(self):
        """
        Génère un rapport détaillé sur la qualité des données
        """
        logger.info("Génération du rapport de qualité...")
        
        rapport = f"""
========================================
RAPPORT DE QUALITÉ DES DONNÉES
========================================
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

STATISTIQUES GÉNÉRALES:
- Produits initiaux:        {self.stats['produits_initiaux']}
- Doublons supprimés:        {self.stats['doublons_supprimes']}
- Accessoires filtrés:       {self.stats['accessoires_filtres']}
- Produits finaux:           {len(self.df)}

COMPLÉTUDE DES DONNÉES:
- Prix:                      {self.df['Prix_Actuel_Clean'].notna().sum()} / {len(self.df)} ({self.df['Prix_Actuel_Clean'].notna().sum()/len(self.df)*100:.1f}%)
- Marque:                    {(self.df['Marque'] != 'Autre').sum()} / {len(self.df)} ({(self.df['Marque'] != 'Autre').sum()/len(self.df)*100:.1f}%)
- CPU:                       {(self.df['CPU'] != 'Autre').sum()} / {len(self.df)} ({(self.df['CPU'] != 'Autre').sum()/len(self.df)*100:.1f}%)
- RAM:                       {self.df['RAM_GB'].notna().sum()} / {len(self.df)} ({self.df['RAM_GB'].notna().sum()/len(self.df)*100:.1f}%)
- Stockage:                  {self.df['Stockage_GB'].notna().sum()} / {len(self.df)} ({self.df['Stockage_GB'].notna().sum()/len(self.df)*100:.1f}%)
- Rating:                    {self.df['Rating_Clean'].notna().sum()} / {len(self.df)} ({self.df['Rating_Clean'].notna().sum()/len(self.df)*100:.1f}%)

STATISTIQUES PRIX:
- Prix moyen:                {self.df['Prix_Actuel_Clean'].mean():.2f} Dhs
- Prix minimum:              {self.df['Prix_Actuel_Clean'].min():.2f} Dhs
- Prix maximum:              {self.df['Prix_Actuel_Clean'].max():.2f} Dhs
- Réduction moyenne:         {self.df['Reduction_Reelle'].mean():.1f}%

RÉPARTITION PAR MARQUE:
{self.df['Marque'].value_counts().to_string()}

RÉPARTITION PAR GAMME:
{self.df['Gamme'].value_counts().to_string()}

RÉPARTITION PAR ÉTAT:
{self.df['Etat_Produit'].value_counts().to_string()}

========================================
"""
        
        # Sauvegarde du rapport
        Path('data/reports').mkdir(parents=True, exist_ok=True)
        with open('data/reports/quality_report.txt', 'w', encoding='utf-8') as f:
            f.write(rapport)
        
        logger.info("✓ Rapport de qualité généré dans data/reports/quality_report.txt")
        print(rapport)
        
    def sauvegarder_donnees_nettoyees(self, output_file='data/processed/cleaned_data.csv'):
        """
        Sauvegarde les données nettoyées dans un nouveau fichier CSV
        
        Args:
            output_file (str): Chemin du fichier de sortie
        """
        logger.info(f"Sauvegarde des données nettoyées...")
        
        # Créer le dossier si nécessaire
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Sauvegarder
        self.df.to_csv(output_file, index=False, encoding='utf-8-sig')
        self.stats['produits_finaux'] = len(self.df)
        
        logger.info(f"✓ {len(self.df)} produits sauvegardés dans {output_file}")
        
    def executer_pipeline_complet(self):
        """
        Exécute toutes les étapes de nettoyage dans l'ordre
        """
        logger.info("="*60)
        logger.info("DÉMARRAGE DU PIPELINE DE NETTOYAGE")
        logger.info("="*60)
        
        etapes = [
            ("Chargement des données", self.charger_donnees),
            ("Nettoyage des prix", self.nettoyer_prix),
            ("Nettoyage des ratings", self.nettoyer_rating),
            ("Extraction des marques", self.extraire_marque),
            ("Extraction des spécifications", self.extraire_specs_techniques),
            ("Détection de l'état", self.detecter_etat_produit),
            ("Filtrage des accessoires", self.filtrer_accessoires),
            ("Suppression des doublons", self.supprimer_doublons),
            ("Calcul de la complétude", self.calculer_completude),
            ("Classification par gamme", self.classifier_par_gamme),
            ("Sauvegarde des données", self.sauvegarder_donnees_nettoyees),
            ("Génération du rapport", self.generer_rapport_qualite)
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
        logger.info("✓ PIPELINE TERMINÉ AVEC SUCCÈS")
        logger.info("="*60)
        return True


# Fonction principale
def main():
    """Point d'entrée principal du script"""
    cleaner = DataCleaner()
    cleaner.executer_pipeline_complet()


if __name__ == "__main__":
    main()