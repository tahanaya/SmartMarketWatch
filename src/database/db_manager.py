"""
DatabaseManager - Classe pour gérer la base de données SQLite
Author: Membre 3 - Database Architect
"""

import sqlite3
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime


class DatabaseManager:
    """Gestionnaire de la base de données SmartMarketWatch"""
    
    def __init__(self, db_path: str = "data/smartmarketwatch.db"):
        """
        Initialise le gestionnaire de base de données
        
        Args:
            db_path: Chemin vers le fichier de base de données
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        
        # Dictionnaires pour les mappings d'IDs
        self.marques_dict = {}
        self.sources_dict = {}
        self.dates_dict = {}
    
    def connect(self):
        """Établit la connexion à la base de données"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.cursor = self.conn.cursor()
        print(f"✅ Connecté à {self.db_path}")
    
    def disconnect(self):
        """Ferme la connexion à la base de données"""
        if self.conn:
            self.conn.commit()
            self.conn.close()
            print("✅ Connexion fermée")
    
    def create_schema(self, schema_path: str = "src/database/schema.sql"):
        """
        Crée la structure de la base de données à partir du fichier schema.sql
        
        Args:
            schema_path: Chemin vers le fichier schema.sql
        """
        print(f"\n🔧 Création de la structure de la base de données...")
        
        # Lire le fichier SQL
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Exécuter le script SQL
        self.cursor.executescript(schema_sql)
        self.conn.commit()
        
        print("✅ Structure créée avec succès")
    
    def load_csv_data(self, csv_path: str):
        """
        Charge les données depuis un fichier CSV dans la base de données
        
        Args:
            csv_path: Chemin vers le fichier CSV
        """
        print(f"\n📂 Chargement du CSV: {csv_path}")
        
        # Charger le CSV
        df = pd.read_csv(csv_path, encoding='utf-8')
        print(f"✅ {len(df)} lignes chargées")
        
        # Remplir les dimensions
        self._populate_dim_marques(df)
        self._populate_dim_sources(df)
        self._populate_dim_dates(df)
        produits_dict = self._populate_dim_produits(df)
        specs_dict = self._populate_dim_specifications(df)
        qualite_dict = self._populate_dim_qualite(df)
        
        # Remplir la table de faits
        self._populate_fact_ventes(df, produits_dict, specs_dict, qualite_dict)
        
        print("\n✅ Données chargées avec succès!")
    
    def _populate_dim_marques(self, df: pd.DataFrame):
        """Remplit la table Dim_Marques"""
        print("🔄 Remplissage Dim_Marques...")
        
        marques = df['Marque'].dropna().unique()
        
        for marque in marques:
            self.cursor.execute(
                "INSERT OR IGNORE INTO Dim_Marques (nom_marque) VALUES (?)",
                (marque,)
            )
        
        self.conn.commit()
        
        # Créer le dictionnaire de mapping
        self.cursor.execute("SELECT marque_id, nom_marque FROM Dim_Marques")
        self.marques_dict = {row[1]: row[0] for row in self.cursor.fetchall()}
        
        print(f"✅ {len(self.marques_dict)} marques insérées")
    
    def _populate_dim_sources(self, df: pd.DataFrame):
        """Remplit la table Dim_Sources"""
        print("🔄 Remplissage Dim_Sources...")
        
        sources = df['Source'].dropna().unique()
        
        for source in sources:
            self.cursor.execute(
                "INSERT OR IGNORE INTO Dim_Sources (nom_source) VALUES (?)",
                (source,)
            )
        
        self.conn.commit()
        
        # Créer le dictionnaire de mapping
        self.cursor.execute("SELECT source_id, nom_source FROM Dim_Sources")
        self.sources_dict = {row[1]: row[0] for row in self.cursor.fetchall()}
        
        print(f"✅ {len(self.sources_dict)} sources insérées")
    
    def _populate_dim_dates(self, df: pd.DataFrame):
        """Remplit la table Dim_Dates"""
        print("🔄 Remplissage Dim_Dates...")
        
        dates = pd.to_datetime(df['Date_Collecte']).dropna().unique()
        
        jours_semaine = {
            0: 'Lundi', 1: 'Mardi', 2: 'Mercredi', 3: 'Jeudi',
            4: 'Vendredi', 5: 'Samedi', 6: 'Dimanche'
        }
        
        for date in dates:
            date_obj = pd.Timestamp(date)
            date_id = int(date_obj.strftime('%Y%m%d'))
            
            trimestre = (date_obj.month - 1) // 3 + 1
            jour_semaine = jours_semaine[date_obj.dayofweek]
            
            self.cursor.execute("""
                INSERT OR IGNORE INTO Dim_Dates 
                (date_id, date_complete, annee, mois, jour, trimestre, jour_semaine)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                date_id,
                date_obj.strftime('%Y-%m-%d'),
                date_obj.year,
                date_obj.month,
                date_obj.day,
                trimestre,
                jour_semaine
            ))
        
        self.conn.commit()
        
        # Créer le dictionnaire de mapping
        self.cursor.execute("SELECT date_id, date_complete FROM Dim_Dates")
        self.dates_dict = {row[1]: row[0] for row in self.cursor.fetchall()}
        
        print(f"✅ {len(self.dates_dict)} dates insérées")
    
    def _populate_dim_produits(self, df: pd.DataFrame) -> Dict[int, int]:
        """Remplit la table Dim_Produits"""
        print("🔄 Remplissage Dim_Produits...")
        
        produits_dict = {}
        
        for idx, row in df.iterrows():
            self.cursor.execute("""
                INSERT INTO Dim_Produits 
                (titre, image_url, resume_produit, keywords_tfidf, gamme)
                VALUES (?, ?, ?, ?, ?)
            """, (
                row.get('Titre', ''),
                row.get('Image_URL', ''),
                row.get('Resume_Produit', ''),
                row.get('Keywords_TFIDF', ''),
                row.get('Gamme', '')
            ))
            
            produits_dict[idx] = self.cursor.lastrowid
        
        self.conn.commit()
        print(f"✅ {len(produits_dict)} produits insérés")
        
        return produits_dict
    
    def _populate_dim_specifications(self, df: pd.DataFrame) -> Dict[int, int]:
        """Remplit la table Dim_Specifications"""
        print("🔄 Remplissage Dim_Specifications...")
        
        specs_dict = {}
        
        for idx, row in df.iterrows():
            self.cursor.execute("""
                INSERT INTO Dim_Specifications 
                (cpu, generation_cpu, ram_gb, ram_type, ram_frequence,
                 stockage_total_gb, type_stockage, stockage_ssd_gb, stockage_hdd_gb,
                 stockage_nvme, ecran_taille, ecran_resolution_width, ecran_resolution_height,
                 ecran_type, ecran_tactile, gpu_marque, gpu_serie, gpu_modele,
                 wifi_version, bluetooth_version, usb_type, batterie_capacite, batterie_autonomie)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row.get('CPU', ''),
                row.get('Generation_CPU', None),
                row.get('RAM_GB', None),
                row.get('RAM_Type', ''),
                row.get('RAM_Frequence', None),
                row.get('Stockage_Total_GB', None),
                row.get('Type_Stockage', ''),
                row.get('Stockage_SSD_GB', None),
                row.get('Stockage_HDD_GB', None),
                1 if row.get('Stockage_NVMe', False) else 0,
                row.get('Ecran_Taille', None),
                row.get('Ecran_Resolution_Width', None),
                row.get('Ecran_Resolution_Height', None),
                row.get('Ecran_Type', ''),
                1 if row.get('Ecran_Tactile', False) else 0,
                row.get('GPU_Marque', ''),
                row.get('GPU_Serie', ''),
                row.get('GPU_Modele', ''),
                row.get('WiFi_Version', ''),
                row.get('Bluetooth_Version', ''),
                row.get('USB_Type', ''),
                row.get('Batterie_Capacite', None),
                row.get('Batterie_Autonomie', None)
            ))
            
            specs_dict[idx] = self.cursor.lastrowid
        
        self.conn.commit()
        print(f"✅ {len(specs_dict)} spécifications insérées")
        
        return specs_dict
    
    def _populate_dim_qualite(self, df: pd.DataFrame) -> Dict[int, int]:
        """Remplit la table Dim_Qualite"""
        print("🔄 Remplissage Dim_Qualite...")
        
        qualite_dict = {}
        
        for idx, row in df.iterrows():
            self.cursor.execute("""
                INSERT INTO Dim_Qualite 
                (etat_produit, taux_completude, sentiment_bert, sentiment_score_bert,
                 anomalie_prix_zscore, anomalie_prix_iqr, type_anomalie_prix,
                 anomalie_ml, produit_suspect, raisons_suspicion, recommandation_achat)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row.get('Etat_Produit', ''),
                row.get('Taux_Completude', None),
                row.get('Sentiment_BERT', ''),
                row.get('Sentiment_Score_BERT', None),
                1 if row.get('Anomalie_Prix_ZScore', False) else 0,
                1 if row.get('Anomalie_Prix_IQR', False) else 0,
                row.get('Type_Anomalie_Prix', ''),
                1 if row.get('Anomalie_ML', False) else 0,
                1 if row.get('Produit_Suspect', False) else 0,
                row.get('Raisons_Suspicion', ''),
                row.get('Recommandation_Achat', '')
            ))
            
            qualite_dict[idx] = self.cursor.lastrowid
        
        self.conn.commit()
        print(f"✅ {len(qualite_dict)} entrées qualité insérées")
        
        return qualite_dict
    
    def _populate_fact_ventes(self, df: pd.DataFrame, produits_dict: Dict, 
                             specs_dict: Dict, qualite_dict: Dict):
        """Remplit la table FACT_Ventes"""
        print("🔄 Remplissage FACT_Ventes...")
        
        for idx, row in df.iterrows():
            # Récupérer les IDs des dimensions
            marque_id = self.marques_dict.get(row.get('Marque', ''), None)
            source_id = self.sources_dict.get(row.get('Source', ''), None)
            
            date_collecte = pd.to_datetime(row.get('Date_Collecte', None))
            if pd.notna(date_collecte):
                date_str = date_collecte.strftime('%Y-%m-%d')
                date_id = self.dates_dict.get(date_str, None)
            else:
                date_id = None
            
            produit_id = produits_dict.get(idx, None)
            spec_id = specs_dict.get(idx, None)
            qualite_id = qualite_dict.get(idx, None)
            
            # Insérer dans la table de faits
            self.cursor.execute("""
                INSERT INTO FACT_Ventes 
                (produit_id, marque_id, date_id, source_id, spec_id, qualite_id,
                 prix_actuel, ancien_prix, reduction_reelle, discount_affiche,
                 rating_score, rating_text, sentiment_score,
                 anomalie_score_ml, anomalie_score_normalized,
                 incoherence_spec_prix, severite_incoherence,
                 indice_confiance, score_fiabilite_vendeur, date_collecte)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                produit_id,
                marque_id,
                date_id,
                source_id,
                spec_id,
                qualite_id,
                row.get('Prix_Actuel_Clean', None),
                row.get('Ancien_Prix_Clean', None),
                row.get('Reduction_Reelle', None),
                row.get('Discount', ''),
                row.get('Rating_Clean', None),
                row.get('Rating', ''),
                row.get('Sentiment_Score_BERT', None),
                row.get('Anomalie_Score_ML', None),
                row.get('Anomalie_Score_Normalized', None),
                row.get('Incoherence_Spec_Prix', ''),
                row.get('Severite_Incoherence', None),
                row.get('Indice_Confiance', None),
                row.get('Score_Fiabilite_Vendeur', None),
                row.get('Date_Collecte', '')
            ))
        
        self.conn.commit()
        print(f"✅ {len(df)} ventes insérées")
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """
        Exécute une requête SQL et retourne les résultats
        
        Args:
            query: Requête SQL à exécuter
            
        Returns:
            DataFrame avec les résultats
        """
        return pd.read_sql_query(query, self.conn)
    
    def get_statistics(self) -> Dict[str, int]:
        """
        Retourne les statistiques de la base de données
        
        Returns:
            Dictionnaire avec le nombre de lignes par table
        """
        tables = [
            'Dim_Marques', 'Dim_Sources', 'Dim_Dates',
            'Dim_Produits', 'Dim_Specifications', 'Dim_Qualite',
            'FACT_Ventes'
        ]
        
        stats = {}
        for table in tables:
            self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
            stats[table] = self.cursor.fetchone()[0]
        
        return stats


if __name__ == "__main__":
    # Test de la classe
    print("🧪 Test de DatabaseManager")
    
    db = DatabaseManager()
    db.connect()
    
    # Créer le schéma
    db.create_schema()
    
    # Afficher les statistiques
    stats = db.get_statistics()
    print("\n📊 Statistiques:")
    for table, count in stats.items():
        print(f"{table}: {count} lignes")
    
    db.disconnect()