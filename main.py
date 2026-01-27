"""
SmartMarketWatch - Point d'entrée principal
============================================
Solution de veille concurrentielle automatisée

Ce script orchestre le pipeline complet:
1. RPA: Collecte des données (scraper.py)
2. IA: Nettoyage et analyse (data_cleaner.py)
3. BI: Génération du dashboard (dashboard.py)

Usage:
    python main.py --all          # Exécute tout le pipeline
    python main.py --scrape       # Seulement le scraping
    python main.py --clean        # Seulement le nettoyage
    python main.py --dashboard    # Lance le dashboard
"""

import argparse
import sys
from pathlib import Path

# Ajouter src au path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import setup_directories, RAW_DATA_FILE, CLEANED_DATA_FILE


def run_scraper():
    """Exécute le module RPA (scraping)."""
    print("\n" + "=" * 60)
    print("ÉTAPE 1/3 - MODULE RPA (Collecte de données)")
    print("=" * 60)

    from rpa.scraper import JumiaScraper

    scraper = JumiaScraper()
    scraper.lancer_scraping()
    scraper.sauvegarder_csv()

    print(f"\nFichier généré: {RAW_DATA_FILE}")


def run_cleaner():
    """Exécute le module IA (nettoyage)."""
    print("\n" + "=" * 60)
    print("ÉTAPE 2/3 - MODULE IA (Nettoyage & Analyse)")
    print("=" * 60)

    from ai.data_cleaner import DataCleaner

    cleaner = DataCleaner()

    try:
        cleaner.charger_donnees()
        # cleaner.nettoyer_donnees()  # TODO: À implémenter
        # cleaner.sauvegarder()
        print("\n[INFO] Module IA en attente d'implémentation")
        print("Les méthodes TODO doivent être complétées par l'équipe IA")
    except FileNotFoundError as e:
        print(f"\n[ERREUR] {e}")
        print("Exécutez d'abord: python main.py --scrape")


def run_dashboard():
    """Exécute le module BI (dashboard)."""
    print("\n" + "=" * 60)
    print("ÉTAPE 3/3 - MODULE BI (Dashboard)")
    print("=" * 60)

    from bi.dashboard import Dashboard

    dashboard = Dashboard()

    try:
        dashboard.charger_donnees()
        kpis = dashboard.calculer_kpis()
        print("\nKPIs calculés:")
        for k, v in kpis.items():
            print(f"  - {k}: {v}")
        print("\n[INFO] Pour le dashboard interactif: streamlit run src/bi/dashboard.py")
    except FileNotFoundError as e:
        print(f"\n[ERREUR] {e}")
        print("Exécutez d'abord le pipeline complet")


def run_full_pipeline():
    """Exécute le pipeline complet."""
    print("\n" + "=" * 60)
    print("SMARTMARKETWATCH - PIPELINE COMPLET")
    print("=" * 60)

    run_scraper()
    run_cleaner()
    run_dashboard()

    print("\n" + "=" * 60)
    print("PIPELINE TERMINÉ")
    print("=" * 60)


def main():
    """Point d'entrée principal avec gestion des arguments."""
    setup_directories()

    parser = argparse.ArgumentParser(
        description="SmartMarketWatch - Veille concurrentielle automatisée",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python main.py --scrape       Collecte les données de Jumia
  python main.py --clean        Nettoie les données (requiert --scrape)
  python main.py --dashboard    Affiche le dashboard (requiert --clean)
  python main.py --all          Exécute tout le pipeline
        """
    )

    parser.add_argument("--scrape", action="store_true", help="Lancer le scraping RPA")
    parser.add_argument("--clean", action="store_true", help="Lancer le nettoyage IA")
    parser.add_argument("--dashboard", action="store_true", help="Lancer le dashboard BI")
    parser.add_argument("--all", action="store_true", help="Exécuter tout le pipeline")

    args = parser.parse_args()

    # Si aucun argument, afficher l'aide
    if not any([args.scrape, args.clean, args.dashboard, args.all]):
        parser.print_help()
        print("\n[INFO] Structure du projet:")
        print("  data/raw/          <- Données brutes (RPA)")
        print("  data/processed/    <- Données nettoyées (IA)")
        print("  data/reports/      <- Rapports d'analyse")
        print("  src/rpa/           <- Module scraping")
        print("  src/ai/            <- Module data mining")
        print("  src/bi/            <- Module dashboard")
        return

    if args.all:
        run_full_pipeline()
    else:
        if args.scrape:
            run_scraper()
        if args.clean:
            run_cleaner()
        if args.dashboard:
            run_dashboard()


if __name__ == "__main__":
    main()
