"""
SmartMarketWatch - Module IA (Data Cleaning & Mining)
=====================================================
Responsable: Équipe IA / Data Science
Description: Nettoyage et enrichissement des données brutes

STATUT: SQUELETTE - À COMPLÉTER PAR L'ÉQUIPE IA

Ce module doit:
1. Lire les données brutes de data/raw/raw_data.csv
2. Nettoyer les prix (enlever "Dhs", convertir en float)
3. Extraire la marque du titre (HP, Dell, Lenovo, etc.)
4. Extraire les specs (CPU, RAM, Stockage) du titre
5. Calculer le % de réduction
6. Sauvegarder dans data/processed/cleaned_data.csv
"""

import re
import pandas as pd
from pathlib import Path

# Import de la configuration
import sys
sys.path.append(str(Path(__file__).parent.parent))
from config import AI_CONFIG, RAW_DATA_FILE, CLEANED_DATA_FILE, setup_directories


class DataCleaner:
    """
    Classe de nettoyage et enrichissement des données.
    À compléter par l'équipe IA.
    """

    def __init__(self):
        self.df = None
        self.marques = AI_CONFIG["marques_connues"]
        self.cpu_patterns = AI_CONFIG["processeurs_patterns"]
        self.ram_patterns = AI_CONFIG["ram_patterns"]
        self.stockage_patterns = AI_CONFIG["stockage_patterns"]

    def charger_donnees(self, filepath=None):
        """Charge les données brutes du CSV."""
        filepath = filepath or RAW_DATA_FILE

        if not Path(filepath).exists():
            raise FileNotFoundError(
                f"Fichier non trouvé: {filepath}\n"
                "L'équipe RPA doit d'abord exécuter le scraper!"
            )

        self.df = pd.read_csv(filepath)
        print(f"Données chargées: {len(self.df)} produits")
        return self.df

    def nettoyer_prix(self, prix_str):
        """
        TODO: Convertit une chaîne de prix en float.
        Exemple: "5,999 Dhs" -> 5999.0

        À IMPLÉMENTER PAR L'ÉQUIPE IA
        """
        if pd.isna(prix_str) or prix_str is None:
            return None

        # TODO: Implémenter la logique de nettoyage
        # Indice: utiliser regex pour extraire les chiffres
        # prix_str = re.sub(r'[^\d,.]', '', str(prix_str))
        # ...

        raise NotImplementedError("À implémenter par l'équipe IA")

    def extraire_marque(self, titre):
        """
        TODO: Extrait la marque du titre du produit.
        Exemple: "HP Laptop 15..." -> "HP"

        À IMPLÉMENTER PAR L'ÉQUIPE IA
        """
        if pd.isna(titre):
            return "Inconnu"

        # TODO: Parcourir self.marques et chercher dans le titre
        # for marque in self.marques:
        #     if marque.lower() in titre.lower():
        #         return marque

        raise NotImplementedError("À implémenter par l'équipe IA")

    def extraire_cpu(self, titre):
        """
        TODO: Extrait le type de processeur du titre.
        Exemple: "...Intel Core i5..." -> "i5"

        À IMPLÉMENTER PAR L'ÉQUIPE IA
        """
        if pd.isna(titre):
            return None

        # TODO: Chercher les patterns CPU dans le titre
        raise NotImplementedError("À implémenter par l'équipe IA")

    def extraire_ram(self, titre):
        """
        TODO: Extrait la RAM du titre.
        Exemple: "...8GB RAM..." -> "8GB"

        À IMPLÉMENTER PAR L'ÉQUIPE IA
        """
        raise NotImplementedError("À implémenter par l'équipe IA")

    def extraire_stockage(self, titre):
        """
        TODO: Extrait le stockage du titre.
        Exemple: "...512GB SSD..." -> "512GB"

        À IMPLÉMENTER PAR L'ÉQUIPE IA
        """
        raise NotImplementedError("À implémenter par l'équipe IA")

    def calculer_reduction(self, prix_actuel, ancien_prix):
        """
        TODO: Calcule le pourcentage de réduction.
        Exemple: prix_actuel=80, ancien_prix=100 -> 20.0 (%)

        À IMPLÉMENTER PAR L'ÉQUIPE IA
        """
        if ancien_prix is None or ancien_prix == 0:
            return 0.0

        # TODO: Formule: ((ancien - actuel) / ancien) * 100
        raise NotImplementedError("À implémenter par l'équipe IA")

    def nettoyer_donnees(self):
        """
        Pipeline principal de nettoyage.
        À COMPLÉTER PAR L'ÉQUIPE IA
        """
        if self.df is None:
            raise ValueError("Aucune donnée chargée. Appelez charger_donnees() d'abord.")

        print("Début du nettoyage des données...")

        # TODO: Appliquer les transformations
        # self.df["Prix_Clean"] = self.df["Prix_Actuel"].apply(self.nettoyer_prix)
        # self.df["Ancien_Prix_Clean"] = self.df["Ancien_Prix"].apply(self.nettoyer_prix)
        # self.df["Marque"] = self.df["Titre"].apply(self.extraire_marque)
        # self.df["CPU"] = self.df["Titre"].apply(self.extraire_cpu)
        # self.df["RAM"] = self.df["Titre"].apply(self.extraire_ram)
        # self.df["Stockage"] = self.df["Titre"].apply(self.extraire_stockage)
        # self.df["Reduction_%"] = self.df.apply(
        #     lambda row: self.calculer_reduction(row["Prix_Clean"], row["Ancien_Prix_Clean"]),
        #     axis=1
        # )

        print("Nettoyage terminé!")
        return self.df

    def sauvegarder(self, filepath=None):
        """Sauvegarde les données nettoyées."""
        filepath = filepath or CLEANED_DATA_FILE
        setup_directories()

        self.df.to_csv(filepath, index=False, encoding="utf-8-sig")
        print(f"Données nettoyées sauvegardées: {filepath}")
        return filepath


def main():
    """Point d'entrée pour le module IA."""
    print("=" * 50)
    print("MODULE IA - Data Cleaning")
    print("=" * 50)

    cleaner = DataCleaner()

    try:
        # Charger les données brutes
        cleaner.charger_donnees()

        # Nettoyer (TODO: à implémenter)
        # cleaner.nettoyer_donnees()

        # Sauvegarder
        # cleaner.sauvegarder()

        print("\n[ÉQUIPE IA] Implémentez les méthodes TODO!")
        print("Fichier source:", RAW_DATA_FILE)
        print("Fichier destination:", CLEANED_DATA_FILE)

    except FileNotFoundError as e:
        print(f"\nERREUR: {e}")
        print("Exécutez d'abord: python src/rpa/scraper.py")


if __name__ == "__main__":
    main()
