"""
SmartMarketWatch - Pipeline Principal COMPLET
==============================================
Orchestrateur du projet ETL complet avec Database

Pipeline en 4 étapes:
    1. RPA       : Collecte des données (scraper.py)
    2. IA        : Nettoyage et NLP (data_cleaner.py, feature_extractor.py)
    3. IA Avancée: NLP + ML (advanced - optionnel)
    4. BDD       : Stockage SQLite (db_manager.py)

Usage:
    python main.py              # Pipeline complet
    python main.py --scrape     # Scraping uniquement
    python main.py --clean      # Nettoyage uniquement
    python main.py --enrich     # Enrichissement uniquement
    python main.py --advanced   # IA avancée (optionnel)
    python main.py --database   # Création BDD uniquement
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


def get_latest_data_file():
    """Retourne le fichier de données le plus complet disponible"""
    files = [
        'data/processed/ai_advanced_complete.csv',
        'data/processed/enriched_data.csv',
        'data/processed/cleaned_data.csv',
    ]
    for f in files:
        if Path(f).exists():
            return Path(f)
    return None


# ============================================
# ÉTAPE 1 : RPA
# ============================================

def etape_1_collecte():
    """ÉTAPE 1/4 : Collecte des données (RPA)"""
    print_step(1, 4, "COLLECTE DES DONNÉES (RPA)")
    
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


# ============================================
# ÉTAPE 2A : IA - NETTOYAGE
# ============================================

def etape_2a_nettoyage():
    """ÉTAPE 2A/4 : Nettoyage des données (IA)"""
    print_step("2A", 4, "NETTOYAGE DES DONNÉES (IA)")
    
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


# ============================================
# ÉTAPE 2B : IA - ENRICHISSEMENT
# ============================================

def etape_2b_enrichissement():
    """ÉTAPE 2B/4 : Enrichissement des données (IA)"""
    print_step("2B", 4, "ENRICHISSEMENT DES DONNÉES (IA)")
    
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


# ============================================
# ÉTAPE 2C : IA AVANCÉE (OPTIONNEL)
# ============================================

def etape_2c_ia_avancee():
    """ÉTAPE 2C/4 : IA Avancée - NLP et Détection d'Anomalies (Optionnel)"""
    print_step("2C", 4, "IA AVANCÉE - NLP ET DÉTECTION D'ANOMALIES (Optionnel)")
    
    enriched_file = Path('data/processed/enriched_data.csv')
    if not enriched_file.exists():
        print("✗ Fichier enriched_data.csv introuvable")
        print("  Exécutez d'abord: python main.py --enrich")
        return False
    
    advanced_module = Path('src/ai/advanced/pipeline_master.py')
    if not advanced_module.exists():
        print("⚠️  Module IA avancé non trouvé")
        print("\n  Installation:")
        print("    1. mkdir -p src/ai/advanced")
        print("    2. Copier les fichiers: nlp_analyzer.py, anomaly_detector.py, pipeline_master.py")
        print("    3. pip install scikit-learn scipy textblob")
        print("\n  Le pipeline continue sans ce module.")
        return False
    
    try:
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


# ============================================
# ÉTAPE 3 : BASE DE DONNÉES
# ============================================

def etape_3_base_de_donnees():
    """ÉTAPE 3/4 : Création de la base de données SQLite"""
    print_step(3, 4, "CRÉATION DE LA BASE DE DONNÉES (SQLite)")
    
    # Vérifier les fichiers requis
    db_manager_file = Path('src/database/db_manager.py')
    schema_file = Path('src/database/schema.sql')
    
    if not db_manager_file.exists() or not schema_file.exists():
        print("✗ Module Database non trouvé")
        print("\n  Fichiers requis:")
        print("    - src/database/db_manager.py")
        print("    - src/database/schema.sql")
        print("\n  Installation:")
        print("    1. mkdir -p src/database")
        print("    2. touch src/database/__init__.py")
        print("    3. Copier db_manager.py et schema.sql dans src/database/")
        return False
    
    # Trouver le fichier de données le plus complet
    data_file = get_latest_data_file()
    
    if not data_file:
        print("✗ Aucun fichier de données trouvé")
        print("  Exécutez d'abord: python main.py --scrape --clean --enrich")
        return False
    
    print(f"📂 Utilisation des données: {data_file}")
    
    try:
        # Import du DatabaseManager
        sys.path.insert(0, 'src/database')
        from db_manager import DatabaseManager
        
        print("\n🗄️  Initialisation de la base de données...")
        
        # Créer l'instance
        db = DatabaseManager()
        
        # Connexion
        db.connect()
        
        # Créer le schéma
        print("🔧 Création du schéma...")
        db.create_schema()
        
        # Charger les données
        print("📥 Chargement des données...")
        db.load_csv_data(data_file)
        
        # Afficher les statistiques
        print("\n📊 Statistiques de la base de données:")
        stats = db.get_statistics()
        total_lignes = 0
        for table, count in stats.items():
            print(f"  • {table:<25} {count:>6} lignes")
            total_lignes += count
        
        print(f"\n  TOTAL: {total_lignes} lignes insérées")
        
        # Déconnexion
        db.disconnect()
        
        # Afficher info fichier
        db_path = Path('data/smartmarketwatch.db')
        if db_path.exists():
            size_kb = db_path.stat().st_size / 1024
            print(f"\n✓ Base de données créée avec succès")
            print(f"  Fichier: {db_path}")
            print(f"  Taille: {size_kb:.1f} KB")
        
        return True
        
    except ImportError as e:
        print(f"✗ Erreur d'import du module Database: {e}")
        print("\n  Vérifiez que les fichiers sont bien dans src/database/:")
        print("    - db_manager.py")
        print("    - schema.sql")
        print("    - __init__.py")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"✗ Erreur lors de la création de la BDD: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================
# ÉTAPE 4 : BI / VISUALISATION
# ============================================

def etape_4_visualisation():
    """ÉTAPE 4/4 : Dashboard de visualisation (BI)"""
    print_step(4, 4, "DASHBOARD DE VISUALISATION (BI)")
    
    db_file = Path('data/smartmarketwatch.db')
    
    if db_file.exists():
        print("✓ Base de données détectée")
        print(f"  Fichier: {db_file}")
        
        print("\n💡 Requêtes SQL disponibles:")
        print("  sqlite3 data/smartmarketwatch.db")
        print("  > SELECT * FROM V_KPI_Prix_Marque;")
        print("  > SELECT * FROM V_KPI_Sentiment;")
        print("  > SELECT * FROM V_Analyse_Complete LIMIT 10;")
    else:
        print("⚠️  Base de données non trouvée")
        print("  Exécutez d'abord: python main.py --database")
    
    dashboard_file = Path('src/bi/dashboard.py')
    
    if dashboard_file.exists():
        print("\n✓ Module dashboard détecté")
        print("\n  Pour lancer le dashboard interactif:")
        print("    streamlit run src/bi/dashboard.py")
    else:
        print("\n⚠️  Module dashboard non encore implémenté")
        print("\n  Prochaines étapes (Équipe BI):")
        print("    1. Créer src/bi/dashboard.py")
        print("    2. Utiliser Streamlit ou Power BI")
        print("    3. Se connecter à data/smartmarketwatch.db")
        print("    4. Créer les visualisations:")
        print("       • Prix moyen par marque")
        print("       • Distribution des sentiments")
        print("       • Top 10 meilleures affaires")
        print("       • Détection des anomalies")
    
    return True


# ============================================
# PIPELINE COMPLET
# ============================================

def executer_pipeline_complet():
    """Exécute le pipeline ETL complet avec toutes les étapes"""
    print_banner("🚀 SMARTMARKETWATCH - PIPELINE COMPLET ETL 🚀")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📦 Version: 2.1 (avec Database SQLite)")
    
    start_time = time.time()
    results = {}
    
    # ÉTAPE 1: Collecte
    results['scraping'] = etape_1_collecte()
    if not results['scraping']:
        print("\n❌ Pipeline arrêté - Échec du scraping")
        return False
    
    # ÉTAPE 2A: Nettoyage
    results['nettoyage'] = etape_2a_nettoyage()
    if not results['nettoyage']:
        print("\n⚠️  Pipeline continue malgré l'échec du nettoyage")
    
    # ÉTAPE 2B: Enrichissement
    if results['nettoyage']:
        results['enrichissement'] = etape_2b_enrichissement()
    else:
        results['enrichissement'] = False
    
    # ÉTAPE 2C: IA Avancée (Optionnel)
    if results['enrichissement']:
        print("\n" + "="*70)
        print("🤖 IA AVANCÉE DISPONIBLE (Optionnel)")
        print("="*70)
        print("Ajoute: NLP, ML, Sentiment Analysis, Détection d'anomalies")
        print("Durée estimée: 30-60 secondes supplémentaires")
        print("-"*70)
        
        results['ia_avancee'] = etape_2c_ia_avancee()
    else:
        results['ia_avancee'] = False
    
    # ÉTAPE 3: Base de données
    if results['nettoyage']:
        results['database'] = etape_3_base_de_donnees()
    else:
        results['database'] = False
    
    # ÉTAPE 4: Visualisation
    results['visualisation'] = etape_4_visualisation()
    
    # RÉSUMÉ FINAL
    duration = time.time() - start_time
    
    print_banner("📋 RÉSUMÉ DU PIPELINE 📋")
    print(f"⏱️  Durée totale: {duration:.2f} secondes ({duration/60:.1f} minutes)")
    
    print(f"\n✅ Modules exécutés:")
    status_icons = {True: "✓", False: "✗"}
    modules = {
        'scraping': 'Scraping RPA',
        'nettoyage': 'Nettoyage IA',
        'enrichissement': 'Enrichissement IA',
        'ia_avancee': 'IA Avancée (NLP+ML)',
        'database': 'Base de Données SQLite',
        'visualisation': 'Dashboard BI'
    }
    
    for key, label in modules.items():
        icon = status_icons[results.get(key, False)]
        print(f"  {icon} {label}")
    
    print(f"\n📁 Fichiers générés:")
    files = [
        ("Données brutes", "data/raw/raw_data.csv"),
        ("Données nettoyées", "data/processed/cleaned_data.csv"),
        ("Données enrichies", "data/processed/enriched_data.csv"),
        ("Analyse IA avancée", "data/processed/ai_advanced_complete.csv"),
        ("Base de données", "data/smartmarketwatch.db"),
        ("Rapport qualité", "data/reports/quality_report.txt"),
        ("Rapport anomalies", "data/reports/anomaly_report.txt"),
        ("Rapport IA complet", "data/reports/ai_advanced_report.txt"),
    ]
    
    for name, path in files:
        if Path(path).exists():
            size = Path(path).stat().st_size / 1024
            print(f"  ✓ {name:<25} {path} ({size:.1f} KB)")
    
    print(f"\n🎯 Prochaines étapes:")
    print(f"  1. Requêtes SQL: sqlite3 data/smartmarketwatch.db")
    print(f"  2. Créer dashboard: src/bi/dashboard.py")
    print(f"  3. Préparer la soutenance")
    
    print_banner("✅ PIPELINE COMPLET TERMINÉ AVEC SUCCÈS ✅")
    
    return True


# ============================================
# MAIN
# ============================================

def main():
    """Point d'entrée principal avec gestion des arguments"""
    
    parser = argparse.ArgumentParser(
        description="SmartMarketWatch - Pipeline ETL complet",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python main.py                # Pipeline complet
  python main.py --all          # Pipeline complet
  python main.py --scrape       # Scraping uniquement
  python main.py --clean        # Nettoyage uniquement
  python main.py --enrich       # Enrichissement uniquement
  python main.py --advanced     # IA avancée uniquement
  python main.py --database     # Création BDD uniquement
  
  python main.py --clean --enrich --database    # IA + BDD
        """
    )

    parser.add_argument("--scrape", action="store_true", help="Collecte RPA")
    parser.add_argument("--clean", action="store_true", help="Nettoyage IA")
    parser.add_argument("--enrich", action="store_true", help="Enrichissement IA")
    parser.add_argument("--advanced", action="store_true", help="IA avancée (NLP+ML)")
    parser.add_argument("--database", action="store_true", help="Création BDD SQLite")
    parser.add_argument("--all", action="store_true", help="Pipeline complet")

    args = parser.parse_args()

    # Si aucun argument, exécuter tout
    if not any([args.scrape, args.clean, args.enrich, args.advanced, args.database, args.all]):
        args.all = True

    try:
        if args.all:
            executer_pipeline_complet()
        else:
            if args.scrape:
                etape_1_collecte()
            if args.clean:
                etape_2a_nettoyage()
            if args.enrich:
                etape_2b_enrichissement()
            if args.advanced:
                etape_2c_ia_avancee()
            if args.database:
                etape_3_base_de_donnees()

    except KeyboardInterrupt:
        print("\n\n⚠️  Interruption utilisateur (Ctrl+C)")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()