"""
Configuration centrale du projet SmartMarketWatch
=================================================
Ce fichier contient toutes les configurations partagées entre les différents modules.
"""

import os
from pathlib import Path

# --- CHEMINS DU PROJET ---
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
REPORTS_DIR = DATA_DIR / "reports"
LOGS_DIR = PROJECT_ROOT / "logs"

# --- FICHIERS DE DONNÉES ---
RAW_DATA_FILE = RAW_DATA_DIR / "raw_data.csv"
CLEANED_DATA_FILE = PROCESSED_DATA_DIR / "cleaned_data.csv"
ANALYSIS_REPORT_FILE = REPORTS_DIR / "analysis_report.csv"

# --- CONFIGURATION RPA (SCRAPING) ---
RPA_CONFIG = {
    "url_base": "https://www.jumia.ma/catalog/?q=ordinateur+portable",
    "pages_a_scraper": 5,  # Nombre de pages à parcourir (plus de volume)
    "delai_entre_pages": 4,  # Secondes entre chaque page (plus respectueux)
    "timeout": 20,  # Timeout augmenté pour éviter les échecs
    "retry_count": 2,  # Nombre de tentatives par page
    "headless": False,  # True = navigateur invisible, False = visible pour debug
    "source_name": "Jumia"
}

# --- CONFIGURATION IA (DATA MINING) ---
AI_CONFIG = {
    "marques_connues": ["HP", "Dell", "Lenovo", "Asus", "Acer", "Apple", "Samsung", "MSI", "Toshiba", "Huawei"],
    "processeurs_patterns": ["i3", "i5", "i7", "i9", "Ryzen 3", "Ryzen 5", "Ryzen 7", "Celeron", "Pentium", "M1", "M2"],
    "ram_patterns": ["4GB", "8GB", "16GB", "32GB", "4 GB", "8 GB", "16 GB", "32 GB"],
    "stockage_patterns": ["128GB", "256GB", "512GB", "1TB", "2TB", "128 GB", "256 GB", "512 GB", "1 TB"]
}

# --- CONFIGURATION BI (DASHBOARD) ---
BI_CONFIG = {
    "dashboard_title": "SmartMarketWatch - Veille Concurrentielle",
    "currency": "DHS",
    "date_format": "%Y-%m-%d %H:%M:%S"
}

# --- SÉLECTEURS CSS JUMIA (à mettre à jour si le site change) ---
CSS_SELECTORS = {
    "product_container": "article.prd",
    "title": "h3.name",
    "current_price": "div.prc",
    "old_price": "div.old",
    "image": "img.img",
    "rating": "div.stars._s",
    "discount": "div.bdg._dsct"
}

# Création automatique des dossiers nécessaires
def setup_directories():
    """Crée tous les dossiers nécessaires s'ils n'existent pas."""
    for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, REPORTS_DIR, LOGS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

if __name__ == "__main__":
    setup_directories()
    print("Configuration chargée avec succès!")
    print(f"Dossier projet: {PROJECT_ROOT}")
