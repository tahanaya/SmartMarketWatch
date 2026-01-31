"""
DatabaseManager - Classe pour gérer la base de données SQLite
Author: Membre 3 - Database Architect
"""

import sqlite3
import pandas as pd
from pathlib import Path
from typing import Dict
from datetime import datetime

# ============================================================
# 📌 Détection automatique de la racine du projet
# ============================================================
# Fichier : src/database/db_manager.py
# Racine  : SmartMarketWatch/
BASE_DIR = Path(__file__).resolve().parents[2]


class DatabaseManager:
    """Gestionnaire de la base de données SmartMarketWatch"""

    def __init__(self, db_path: Path | None = None):
        """
        Initialise le gestionnaire de base de données (chemin relatif)
        """
        self.db_path = db_path or (BASE_DIR / "data" / "smartmarketwatch.db")

        # Créer le dossier data/ si inexistant
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.conn = None
        self.cursor = None

        # Dictionnaires pour les mappings d'IDs
        self.marques_dict = {}
        self.sources_dict = {}
        self.dates_dict = {}

    # ============================================================
    # 🔌 Connexion DB
    # ============================================================
    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.cursor = self.conn.cursor()
        print(f"✅ Connecté à {self.db_path}")

    def disconnect(self):
        if self.conn:
            self.conn.commit()
            self.conn.close()
            print("✅ Connexion fermée")

    # ============================================================
    # 🧱 Création du schéma
    # ============================================================
    def create_schema(self, schema_path: Path | None = None):
        schema_path = schema_path or (BASE_DIR / "src" / "database" / "schema.sql")

        print("\n🔧 Création de la structure de la base de données...")

        with open(schema_path, "r", encoding="utf-8") as f:
            schema_sql = f.read()

        self.cursor.executescript(schema_sql)
        self.conn.commit()

        print("✅ Structure créée avec succès")

    # ============================================================
    # 📂 Chargement CSV
    # ============================================================
    def load_csv_data(self, csv_path: Path):
        print(f"\n📂 Chargement du CSV: {csv_path}")

        df = pd.read_csv(csv_path, encoding="utf-8")
        print(f"✅ {len(df)} lignes chargées")

        self._populate_dim_marques(df)
        self._populate_dim_sources(df)
        self._populate_dim_dates(df)

        produits_dict = self._populate_dim_produits(df)
        specs_dict = self._populate_dim_specifications(df)
        qualite_dict = self._populate_dim_qualite(df)

        self._populate_fact_ventes(df, produits_dict, specs_dict, qualite_dict)

        print("\n✅ Données chargées avec succès !")

    # ============================================================
    # 📊 Dimensions
    # ============================================================
    def _populate_dim_marques(self, df):
        print("🔄 Remplissage Dim_Marques...")
        for marque in df["Marque"].dropna().unique():
            self.cursor.execute(
                "INSERT OR IGNORE INTO Dim_Marques (nom_marque) VALUES (?)",
                (marque,),
            )
        self.conn.commit()
        self.cursor.execute("SELECT marque_id, nom_marque FROM Dim_Marques")
        self.marques_dict = {m: i for i, m in self.cursor.fetchall()}
        print(f"✅ {len(self.marques_dict)} marques insérées")

    def _populate_dim_sources(self, df):
        print("🔄 Remplissage Dim_Sources...")
        for source in df["Source"].dropna().unique():
            self.cursor.execute(
                "INSERT OR IGNORE INTO Dim_Sources (nom_source) VALUES (?)",
                (source,),
            )
        self.conn.commit()
        self.cursor.execute("SELECT source_id, nom_source FROM Dim_Sources")
        self.sources_dict = {s: i for i, s in self.cursor.fetchall()}
        print(f"✅ {len(self.sources_dict)} sources insérées")

    def _populate_dim_dates(self, df):
        print("🔄 Remplissage Dim_Dates...")
        jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

        for date in pd.to_datetime(df["Date_Collecte"]).dropna().unique():
            d = pd.Timestamp(date)
            self.cursor.execute(
                """
                INSERT OR IGNORE INTO Dim_Dates
                (date_id, date_complete, annee, mois, jour, trimestre, jour_semaine)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    int(d.strftime("%Y%m%d")),
                    d.strftime("%Y-%m-%d"),
                    d.year,
                    d.month,
                    d.day,
                    (d.month - 1) // 3 + 1,
                    jours[d.dayofweek],
                ),
            )
        self.conn.commit()
        self.cursor.execute("SELECT date_id, date_complete FROM Dim_Dates")
        self.dates_dict = {d: i for i, d in self.cursor.fetchall()}
        print(f"✅ {len(self.dates_dict)} dates insérées")

    def _populate_dim_produits(self, df):
        print("🔄 Remplissage Dim_Produits...")
        mapping = {}
        for idx, row in df.iterrows():
            self.cursor.execute(
                """
                INSERT INTO Dim_Produits (titre, image_url, resume_produit, keywords_tfidf, gamme)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    row.get("Titre", ""),
                    row.get("Image_URL", ""),
                    row.get("Resume_Produit", ""),
                    row.get("Keywords_TFIDF", ""),
                    row.get("Gamme", ""),
                ),
            )
            mapping[idx] = self.cursor.lastrowid
        self.conn.commit()
        print(f"✅ {len(mapping)} produits insérés")
        return mapping

    def _populate_dim_specifications(self, df):
        print("🔄 Remplissage Dim_Specifications...")
        mapping = {}
        for idx, row in df.iterrows():
            self.cursor.execute(
                """
                INSERT INTO Dim_Specifications
                (cpu, generation_cpu, ram_gb, ram_type, ram_frequence,
                 stockage_total_gb, type_stockage, stockage_ssd_gb, stockage_hdd_gb,
                 stockage_nvme, ecran_taille, ecran_resolution_width, ecran_resolution_height,
                 ecran_type, ecran_tactile, gpu_marque, gpu_serie, gpu_modele,
                 wifi_version, bluetooth_version, usb_type, batterie_capacite, batterie_autonomie)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row.get("CPU", ""),
                    row.get("Generation_CPU"),
                    row.get("RAM_GB"),
                    row.get("RAM_Type", ""),
                    row.get("RAM_Frequence"),
                    row.get("Stockage_Total_GB"),
                    row.get("Type_Stockage", ""),
                    row.get("Stockage_SSD_GB"),
                    row.get("Stockage_HDD_GB"),
                    int(bool(row.get("Stockage_NVMe"))),
                    row.get("Ecran_Taille"),
                    row.get("Ecran_Resolution_Width"),
                    row.get("Ecran_Resolution_Height"),
                    row.get("Ecran_Type", ""),
                    int(bool(row.get("Ecran_Tactile"))),
                    row.get("GPU_Marque", ""),
                    row.get("GPU_Serie", ""),
                    row.get("GPU_Modele", ""),
                    row.get("WiFi_Version", ""),
                    row.get("Bluetooth_Version", ""),
                    row.get("USB_Type", ""),
                    row.get("Batterie_Capacite"),
                    row.get("Batterie_Autonomie"),
                ),
            )
            mapping[idx] = self.cursor.lastrowid
        self.conn.commit()
        print(f"✅ {len(mapping)} spécifications insérées")
        return mapping

    def _populate_dim_qualite(self, df):
        print("🔄 Remplissage Dim_Qualite...")
        mapping = {}
        for idx, row in df.iterrows():
            self.cursor.execute(
                """
                INSERT INTO Dim_Qualite
                (etat_produit, taux_completude, sentiment_bert, sentiment_score_bert,
                 anomalie_prix_zscore, anomalie_prix_iqr, type_anomalie_prix,
                 anomalie_ml, produit_suspect, raisons_suspicion, recommandation_achat)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row.get("Etat_Produit", ""),
                    row.get("Taux_Completude"),
                    row.get("Sentiment_BERT", ""),
                    row.get("Sentiment_Score_BERT"),
                    int(bool(row.get("Anomalie_Prix_ZScore"))),
                    int(bool(row.get("Anomalie_Prix_IQR"))),
                    row.get("Type_Anomalie_Prix", ""),
                    int(bool(row.get("Anomalie_ML"))),
                    int(bool(row.get("Produit_Suspect"))),
                    row.get("Raisons_Suspicion", ""),
                    row.get("Recommandation_Achat", ""),
                ),
            )
            mapping[idx] = self.cursor.lastrowid
        self.conn.commit()
        print(f"✅ {len(mapping)} entrées qualité insérées")
        return mapping

    def _populate_fact_ventes(self, df, produits, specs, qualites):
        print("🔄 Remplissage FACT_Ventes...")
        for idx, row in df.iterrows():
            date = pd.to_datetime(row.get("Date_Collecte"))
            date_id = self.dates_dict.get(date.strftime("%Y-%m-%d")) if pd.notna(date) else None

            self.cursor.execute(
                """
                INSERT INTO FACT_Ventes
                (produit_id, marque_id, date_id, source_id, spec_id, qualite_id,
                 prix_actuel, ancien_prix, reduction_reelle, discount_affiche,
                 rating_score, rating_text, sentiment_score,
                 anomalie_score_ml, anomalie_score_normalized,
                 incoherence_spec_prix, severite_incoherence,
                 indice_confiance, score_fiabilite_vendeur, date_collecte)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    produits[idx],
                    self.marques_dict.get(row.get("Marque")),
                    date_id,
                    self.sources_dict.get(row.get("Source")),
                    specs[idx],
                    qualites[idx],
                    row.get("Prix_Actuel_Clean"),
                    row.get("Ancien_Prix_Clean"),
                    row.get("Reduction_Reelle"),
                    row.get("Discount"),
                    row.get("Rating_Clean"),
                    row.get("Rating"),
                    row.get("Sentiment_Score_BERT"),
                    row.get("Anomalie_Score_ML"),
                    row.get("Anomalie_Score_Normalized"),
                    row.get("Incoherence_Spec_Prix"),
                    row.get("Severite_Incoherence"),
                    row.get("Indice_Confiance"),
                    row.get("Score_Fiabilite_Vendeur"),
                    row.get("Date_Collecte"),
                ),
            )
        self.conn.commit()
        print(f"✅ {len(df)} ventes insérées")

    # ============================================================
    # 📈 Stats
    # ============================================================
    def get_statistics(self) -> Dict[str, int]:
        tables = [
            "Dim_Marques",
            "Dim_Sources",
            "Dim_Dates",
            "Dim_Produits",
            "Dim_Specifications",
            "Dim_Qualite",
            "FACT_Ventes",
        ]
        return {
            t: self.cursor.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            for t in tables
        }


# ============================================================
# 🧪 Test direct
# ============================================================
if __name__ == "__main__":
    print("🧪 Test de DatabaseManager")

    db = DatabaseManager()
    db.connect()
    db.create_schema()

    csv_file = BASE_DIR / "data" / "processed" / "ai_advanced_complete.csv"
    db.load_csv_data(csv_file)

    print("\n📊 Statistiques:")
    for table, count in db.get_statistics().items():
        print(f"{table}: {count} lignes")

    db.disconnect()
