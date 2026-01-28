"""
Script de test pour vérifier que la base de données fonctionne correctement
"""

import sys
import os

# Ajouter le dossier parent au path pour pouvoir importer
sys.path.insert(0, os.path.abspath('.'))

from src.database.db_manager import DatabaseManager


def test_database():
    """Teste la création et le chargement de la base de données"""
    
    print("\n" + "="*70)
    print("     TEST DE LA BASE DE DONNÉES")
    print("="*70)
    
    # Initialiser le gestionnaire de base de données
    db = DatabaseManager("data/smartmarketwatch.db")
    
    # Connecter
    db.connect()
    
    # Créer le schéma
    print("\n📋 Étape 1: Création du schéma...")
    db.create_schema("src/database/schema.sql")
    
    # Charger les données
    print("\n📋 Étape 2: Chargement des données...")
    csv_path = "data/processed/ai_advanced_complete.csv"
    
    if not os.path.exists(csv_path):
        print(f"\n⚠️  ATTENTION: Le fichier CSV n'existe pas encore: {csv_path}")
        print("Vous devez d'abord exécuter le script de Membre 2 (IA) pour générer ce fichier.")
        print("\nStructure attendue:")
        print("  data/")
        print("    processed/")
        print("      ai_advanced_complete.csv")
    else:
        db.load_csv_data(csv_path)
        
        # Afficher les statistiques
        print("\n📊 Étape 3: Vérification des données...")
        stats = db.get_statistics()
        
        print("\n" + "-"*70)
        for table, count in stats.items():
            print(f"{table:30} : {count:>6} lignes")
        print("-"*70)
        
        # Tester une requête
        print("\n🔍 Étape 4: Test d'une requête...")
        query = """
        SELECT 
            m.nom_marque,
            COUNT(*) as nombre_produits,
            ROUND(AVG(f.prix_actuel), 2) as prix_moyen
        FROM FACT_Ventes f
        JOIN Dim_Marques m ON f.marque_id = m.marque_id
        WHERE f.prix_actuel IS NOT NULL
        GROUP BY m.nom_marque
        ORDER BY prix_moyen DESC
        LIMIT 5;
        """
        
        results = db.execute_query(query)
        print("\nTop 5 marques par prix moyen:")
        print(results.to_string(index=False))
    
    # Déconnecter
    db.disconnect()
    
    print("\n" + "="*70)
    print("✅ TEST TERMINÉ")
    print("="*70)


if __name__ == "__main__":
    test_database()