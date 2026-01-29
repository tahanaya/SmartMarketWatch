"""
SmartMarketWatch - Pipeline Principal
======================================
Orchestrateur du projet ETL complet

Pipeline en 3 étapes:
    1. RPA    : Collecte des données (scraper.py)
    2. IA     : Nettoyage et NLP (data_cleaner.py, feature_extractor.py)
    3. BI/BDD : Stockage et visualisation

Usage:
    python main.py              # Pipeline complet par défaut
    python main.py --scrape     # Scraping uniquement
    python main.py --clean      # Nettoyage uniquement
    python main.py --enrich     # Enrichissement uniquement
    python main.py --advanced   # IA avancée (optionnel)
    python main.py --help       # Aide
"""

import argparse
import sys
import time
from pathlib import Path
from datetime import datetime

# Import des modules
from src.rpa.scraper import main as scraper_main
from src.ai.data_cleaner import DataCleaner
from src.ai.feature_extractor import FeatureExtractor


# ============================================
# FONCTIONS UTILITAIRES
# ============================================

def print_banner(text, char="="):
    """Affiche un bandeau formaté."""
    print("\n" + char * 70)
    print(text.center(70))
    print(char * 70)


def print_step(step_num, total_steps, title):
    """Affiche le numéro d'étape."""
    print(f"\n[ÉTAPE {step_num}/{total_steps}] {title}")
    print("-" * 70)


# ============================================
# FONCTIONS PAR ÉTAPE
# ============================================

def etape_1_collecte():
    """ÉTAPE 1/3 : Collecte des données (RPA)"""
    print_step(1, 3, "COLLECTE DES DONNÉES (RPA)")
    
    try:
        scraper_main()
        print("✓ Collecte terminée avec succès")
        print("  Fichier généré: data/raw/raw_data.csv")
        return True
    except Exception as e:
        print(f"✗ Erreur lors de la collecte: {e}")
        import traceback
        traceback.print_exc()
        return False


def etape_2a_nettoyage():
    """ÉTAPE 2A/3 : Nettoyage des données (IA)"""
    print_step("2A", 3, "NETTOYAGE DES DONNÉES (IA)")
    
    try:
        cleaner = DataCleaner()
        if not cleaner.executer_pipeline_complet():
            print("✗ Erreur lors du nettoyage")
            return False
        
        print("✓ Nettoyage terminé avec succès")
        print("  Fichier généré: data/processed/cleaned_data.csv")
        print("  Rapport: data/reports/quality_report.txt")
        return True
    except FileNotFoundError:
        print("✗ Fichier raw_data.csv introuvable")
        print("  Exécutez d'abord: python main.py --scrape")
        return False
    except Exception as e:
        print(f"✗ Erreur lors du nettoyage: {e}")
        import traceback
        traceback.print_exc()
        return False


def etape_2b_enrichissement():
    """ÉTAPE 2B/3 : Enrichissement des données (IA)"""
    print_step("2B", 3, "ENRICHISSEMENT DES DONNÉES (IA)")
    
    try:
        extractor = FeatureExtractor()
        if not extractor.executer_pipeline_complet():
            print("✗ Erreur lors de l'enrichissement")
            return False
        
        print("✓ Enrichissement terminé avec succès")
        print("  Fichier généré: data/processed/enriched_data.csv")
        return True
    except FileNotFoundError:
        print("✗ Fichier cleaned_data.csv introuvable")
        print("  Exécutez d'abord: python main.py --clean")
        return False
    except Exception as e:
        print(f"✗ Erreur lors de l'enrichissement: {e}")
        import traceback
        traceback.print_exc()
        return False


def etape_2c_ia_avancee():
    """ÉTAPE 2C/3 : IA Avancée - NLP et Détection d'Anomalies (Optionnel)"""
    print_step("2C", 3, "IA AVANCÉE - NLP ET DÉTECTION D'ANOMALIES (Optionnel)")
    
    # Vérifier que le fichier enrichi existe
    enriched_file = Path('data/processed/enriched_data.csv')
    if not enriched_file.exists():
        print("✗ Fichier enriched_data.csv introuvable")
        print("  Exécutez d'abord: python main.py --enrich")
        return False
    
    # Vérifier que le module avancé existe
    advanced_module = Path('src/ai/advanced/pipeline_master.py')
    if not advanced_module.exists():
        print("⚠️  Module IA avancé non trouvé")
        print("\n  Pour l'installer:")
        print("    1. Créez le dossier: src/ai/advanced/")
        print("    2. Copiez les fichiers:")
        print("       - nlp_analyzer.py")
        print("       - anomaly_detector.py")
        print("       - pipeline_master.py")
        print("    3. Installez les dépendances:")
        print("       pip install scikit-learn scipy textblob")
        print("\n  Le pipeline continue sans ce module.")
        return False
    
    try:
        # Import dynamique pour éviter l'erreur si le module n'existe pas
        sys.path.insert(0, 'src/ai/advanced')
        from pipeline_master import AdvancedAIPipeline
        
        print("🧠 Lancement de l'analyse NLP et détection d'anomalies ML...")
        pipeline = AdvancedAIPipeline(input_file='data/processed/enriched_data.csv')
        
        if pipeline.execute_full_pipeline():
            print("✓ IA avancée terminée avec succès")
            print("  Fichier généré: data/processed/ai_advanced_complete.csv")
            print("  Rapports:")
            print("    - data/reports/ai_advanced_report.txt")
            print("    - data/reports/anomaly_report.txt")
            return True
        else:
            print("✗ Erreur lors de l'IA avancée")
            return False
            
    except ImportError as e:
        print(f"⚠️  Impossible d'importer le module IA avancé: {e}")
        print("  Le pipeline continue sans ce module.")
        return False
    except Exception as e:
        print(f"✗ Erreur lors de l'IA avancée: {e}")
        import traceback
        traceback.print_exc()
        return False


def etape_3_stockage_visualisation():
    """ÉTAPE 3/3 : Stockage (BDD) et Visualisation (BI)"""
    print_step(3, 3, "STOCKAGE (BDD) ET VISUALISATION (BI)")
    
    print("⚠️  Module BDD/BI non encore implémenté")
    print("\n  Prochaines étapes:")
    print("    1. Créer le schéma de la base de données (SQLite/MySQL)")
    print("    2. Importer les données depuis enriched_data.csv")
    print("    3. Créer le dashboard de visualisation (Streamlit/Power BI)")
    print("\n  Fichiers à créer:")
    print("    - src/bdd/schema.sql")
    print("    - src/bdd/importer.py")
    print("    - src/bi/dashboard.py")
    
    return True


# ============================================
# PIPELINE COMPLET
# ============================================

def executer_pipeline_complet():
    """Exécute le pipeline ETL complet avec toutes les étapes"""
    print_banner("🚀 SMARTMARKETWATCH - PIPELINE COMPLET ETL 🚀")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📦 Version: 2.0 (avec IA avancée optionnelle)")
    
    start_time = time.time()
    results = {}
    
    # ÉTAPE 1: Collecte des données (RPA)
    results['scraping'] = etape_1_collecte()
    if not results['scraping']:
        print("\n❌ Pipeline arrêté - Échec du scraping")
        return False
    
    # ÉTAPE 2A: Nettoyage (IA)
    results['nettoyage'] = etape_2a_nettoyage()
    if not results['nettoyage']:
        print("\n⚠️  Pipeline continue malgré l'échec du nettoyage")
    
    # ÉTAPE 2B: Enrichissement (IA)
    if results['nettoyage']:
        results['enrichissement'] = etape_2b_enrichissement()
    else:
        results['enrichissement'] = False
    
    # ÉTAPE 2C: IA Avancée (Optionnel)
    if results['enrichissement']:
        print("\n" + "="*70)
        print("🤖 IA AVANCÉE DISPONIBLE (Optionnel)")
        print("="*70)
        print("L'IA avancée ajoute:")
        print("  • Extraction de 40+ caractéristiques techniques")
        print("  • Analyse de sentiment avec NLP")
        print("  • Détection d'anomalies avec Machine Learning")
        print("  • Scoring de confiance et recommandations")
        print("\nDurée estimée: 30-60 secondes supplémentaires")
        print("-"*70)
        
        # Pour une démo automatique, lancer directement
        # Pour une interaction, demander confirmation ici
        results['ia_avancee'] = etape_2c_ia_avancee()
    else:
        results['ia_avancee'] = False
    
    # ÉTAPE 3: BDD et BI
    results['bdd_bi'] = etape_3_stockage_visualisation()
    
    # RÉSUMÉ FINAL
    duration = time.time() - start_time
    
    print_banner("📋 RÉSUMÉ DU PIPELINE 📋")
    print(f"⏱️  Durée totale: {duration:.2f} secondes ({duration/60:.1f} minutes)")
    
    print(f"\n✅ Modules exécutés:")
    status_icons = {True: "✓", False: "✗"}
    for module, success in results.items():
        icon = status_icons[success]
        module_name = module.replace('_', ' ').title()
        print(f"  {icon} {module_name}")
    
    print(f"\n📁 Fichiers générés:")
    output_files = [
        ("Données brutes", "data/raw/raw_data.csv"),
        ("Données nettoyées", "data/processed/cleaned_data.csv"),
        ("Données enrichies", "data/processed/enriched_data.csv"),
        ("Analyse IA avancée", "data/processed/ai_advanced_complete.csv"),
        ("Rapport qualité", "data/reports/quality_report.txt"),
        ("Rapport anomalies", "data/reports/anomaly_report.txt"),
        ("Rapport IA complet", "data/reports/ai_advanced_report.txt"),
    ]
    
    for name, path in output_files:
        if Path(path).exists():
            size = Path(path).stat().st_size / 1024
            print(f"  ✓ {name}: {path} ({size:.1f} KB)")
    
    print(f"\n🎯 Prochaines étapes:")
    print(f"  1. Créer le schéma BDD (src/bdd/schema.sql)")
    print(f"  2. Importer les données dans la BDD (src/bdd/importer.py)")
    print(f"  3. Créer le dashboard (src/bi/dashboard.py)")
    print(f"  4. Soutenance: Présenter le pipeline ETL complet")
    
    print_banner("✅ PIPELINE TERMINÉ AVEC SUCCÈS ✅")
    
    return True


# ============================================
# MAIN - GESTION DES ARGUMENTS
# ============================================

def main():
    """Point d'entrée principal avec gestion des arguments"""
    
    parser = argparse.ArgumentParser(
        description="SmartMarketWatch - Pipeline ETL de veille concurrentielle",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:

  PIPELINE COMPLET (Recommandé):
    python main.py
    python main.py --all

  ÉTAPES INDIVIDUELLES:
    python main.py --scrape       # Étape 1: Collecte RPA
    python main.py --clean        # Étape 2A: Nettoyage IA
    python main.py --enrich       # Étape 2B: Enrichissement IA
    python main.py --advanced     # Étape 2C: IA avancée (optionnel)

  COMBINAISONS:
    python main.py --clean --enrich              # IA complète
    python main.py --scrape --clean --enrich     # Pipeline sans IA avancée

Modules disponibles:
  • RPA: Scraping automatique de Jumia (Selenium)
  • IA Base: Nettoyage + Extraction de features
  • IA Pro: NLP + Détection d'anomalies ML (optionnel)
  • BDD/BI: Stockage et visualisation (à implémenter)
        """
    )

    parser.add_argument(
        "--scrape", 
        action="store_true", 
        help="Étape 1: Collecte des données (RPA)"
    )
    parser.add_argument(
        "--clean", 
        action="store_true", 
        help="Étape 2A: Nettoyage des données (IA)"
    )
    parser.add_argument(
        "--enrich", 
        action="store_true", 
        help="Étape 2B: Enrichissement des données (IA)"
    )
    parser.add_argument(
        "--advanced", 
        action="store_true", 
        help="Étape 2C: IA avancée - NLP et ML (optionnel)"
    )
    parser.add_argument(
        "--all", 
        action="store_true", 
        help="Exécuter le pipeline complet (toutes les étapes)"
    )

    args = parser.parse_args()

    # Si aucun argument, exécuter le pipeline complet par défaut
    if not any([args.scrape, args.clean, args.enrich, args.advanced, args.all]):
        args.all = True

    try:
        # Pipeline complet
        if args.all:
            executer_pipeline_complet()
        
        # Exécution individuelle ou combinée
        else:
            if args.scrape:
                etape_1_collecte()
            
            if args.clean:
                etape_2a_nettoyage()
            
            if args.enrich:
                etape_2b_enrichissement()
            
            if args.advanced:
                etape_2c_ia_avancee()

    except KeyboardInterrupt:
        print("\n\n⚠️  Interruption utilisateur (Ctrl+C)")
        print("Pipeline arrêté")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
