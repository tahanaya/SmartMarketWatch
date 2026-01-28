"""
SmartMarketWatch - Pipeline Principal
Orchestrateur du projet ETL complet
"""

import argparse
import sys
from pathlib import Path

# Import des modules
from src.rpa.scraper import main as scraper_main
from src.ai.data_cleaner import DataCleaner
from src.ai.feature_extractor import FeatureExtractor


def executer_pipeline_complet():
    """Exécute le pipeline ETL complet"""
    print("\n" + "="*70)
    print("SMARTMARKETWATCH - PIPELINE COMPLET ETL")
    print("="*70)
    
    # Étape 1: RPA - Collecte des données
    print("\n[ÉTAPE 1/3] COLLECTE DES DONNÉES (RPA)")
    print("-" * 70)
    try:
        scraper_main()
        print("✓ Collecte terminée")
    except Exception as e:
        print(f"✗ Erreur lors de la collecte: {e}")
        return False
    
    # Étape 2a: IA - Nettoyage des données
    print("\n[ÉTAPE 2A/3] NETTOYAGE DES DONNÉES (IA)")
    print("-" * 70)
    try:
        cleaner = DataCleaner()
        if not cleaner.executer_pipeline_complet():
            print("✗ Erreur lors du nettoyage")
            return False
        print("✓ Nettoyage terminé")
    except Exception as e:
        print(f"✗ Erreur lors du nettoyage: {e}")
        return False
    
    # Étape 2b: IA - Enrichissement des données
    print("\n[ÉTAPE 2B/3] ENRICHISSEMENT DES DONNÉES (IA)")
    print("-" * 70)
    try:
        extractor = FeatureExtractor()
        if not extractor.executer_pipeline_complet():
            print("✗ Erreur lors de l'enrichissement")
            return False
        print("✓ Enrichissement terminé")
    except Exception as e:
        print(f"✗ Erreur lors de l'enrichissement: {e}")
        return False
    
    # Étape 3: BI - Visualisation (à implémenter)
    print("\n[ÉTAPE 3/3] VISUALISATION (BI)")
    print("-" * 70)
    print("⚠ Module BI non encore implémenté")
    print("→ Fichier à compléter: src/bi/dashboard.py")
    
    print("\n" + "="*70)
    print("✓ PIPELINE COMPLET TERMINÉ AVEC SUCCÈS")
    print("="*70)
    print(f"\nFichiers générés:")
    print(f"  - data/raw/raw_data.csv")
    print(f"  - data/processed/cleaned_data.csv")
    print(f"  - data/processed/enriched_data.csv")
    print(f"  - data/reports/quality_report.txt")
    print(f"\nProchaine étape: Créer le dashboard BI")
    
    return True


def main():
    """Point d'entrée principal avec arguments"""
    parser = argparse.ArgumentParser(description='SmartMarketWatch - Pipeline ETL')
    parser.add_argument('--all', action='store_true', help='Exécuter le pipeline complet')
    parser.add_argument('--scrape', action='store_true', help='Scraping uniquement')
    parser.add_argument('--clean', action='store_true', help='Nettoyage uniquement')
    parser.add_argument('--enrich', action='store_true', help='Enrichissement uniquement')
    
    args = parser.parse_args()
    
    # Si aucun argument, exécuter tout
    if not any([args.all, args.scrape, args.clean, args.enrich]):
        args.all = True
    
    try:
        if args.all:
            executer_pipeline_complet()
        
        elif args.scrape:
            print("\n[SCRAPING UNIQUEMENT]")
            scraper_main()
        
        elif args.clean:
            print("\n[NETTOYAGE UNIQUEMENT]")
            cleaner = DataCleaner()
            cleaner.executer_pipeline_complet()
        
        elif args.enrich:
            print("\n[ENRICHISSEMENT UNIQUEMENT]")
            extractor = FeatureExtractor()
            extractor.executer_pipeline_complet()
    
    except KeyboardInterrupt:
        print("\n\n⚠ Interruption utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Erreur fatale: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()