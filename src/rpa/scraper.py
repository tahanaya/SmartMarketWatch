"""
SmartMarketWatch - Module RPA (Scraping)
========================================
Responsable: Taha (Collecte de données)
Description: Robot de collecte automatique des données produits depuis Jumia Maroc

Ce script extrait les informations suivantes:
- Titre complet du produit
- Prix actuel
- Ancien prix (promotions)
- URL de l'image
- Note/Rating (si disponible)
"""

import time
import logging
from datetime import datetime
from pathlib import Path

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# Import de la configuration centralisée
import sys
sys.path.append(str(Path(__file__).parent.parent))
from config import RPA_CONFIG, CSS_SELECTORS, RAW_DATA_FILE, LOGS_DIR, setup_directories

# --- CONFIGURATION DU LOGGING ---
setup_directories()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / "scraper.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class JumiaScraper:
    """
    Classe principale pour le scraping de Jumia Maroc.
    Conçue pour être robuste et respectueuse du site cible.
    """

    def __init__(self):
        self.url_base = RPA_CONFIG["url_base"]
        self.pages_a_scraper = RPA_CONFIG["pages_a_scraper"]
        self.delai = RPA_CONFIG["delai_entre_pages"]
        self.headless = RPA_CONFIG["headless"]
        self.retry_count = RPA_CONFIG.get("retry_count", 2)
        self.driver = None
        self.products = []

    def configurer_navigateur(self):
        """Configure et initialise le navigateur Chrome."""
        options = Options()

        if self.headless:
            options.add_argument("--headless")

        # Options pour éviter la détection
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")
        options.add_argument("--lang=fr-FR")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        # User-Agent réaliste
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )

        # Masquer le webdriver
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        logger.info("Navigateur configuré avec succès")
        return self.driver

    def fermer_popup(self):
        """Ferme les popups publicitaires si présentes."""
        try:
            # Popup newsletter/promo courante sur Jumia
            close_buttons = [
                "button.cls",
                "div.overlay button",
                "[data-dismiss='modal']",
                ".close-btn"
            ]
            for selector in close_buttons:
                try:
                    btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                    btn.click()
                    logger.info("Popup fermée")
                    time.sleep(0.5)
                except NoSuchElementException:
                    continue
        except Exception:
            pass  # Pas de popup, on continue

    def extraire_produit(self, article):
        """Extrait les données d'un seul produit."""
        try:
            # TITRE
            try:
                titre = article.find_element(By.CSS_SELECTOR, CSS_SELECTORS["title"]).text.strip()
            except NoSuchElementException:
                titre = None

            # PRIX ACTUEL
            try:
                prix = article.find_element(By.CSS_SELECTOR, CSS_SELECTORS["current_price"]).text.strip()
            except NoSuchElementException:
                prix = None

            # ANCIEN PRIX (promo)
            try:
                ancien_prix = article.find_element(By.CSS_SELECTOR, CSS_SELECTORS["old_price"]).text.strip()
            except NoSuchElementException:
                ancien_prix = None

            # IMAGE URL
            try:
                img_element = article.find_element(By.CSS_SELECTOR, CSS_SELECTORS["image"])
                img_url = img_element.get_attribute("data-src") or img_element.get_attribute("src")
            except NoSuchElementException:
                img_url = None

            # RATING (Note)
            try:
                rating_element = article.find_element(By.CSS_SELECTOR, CSS_SELECTORS["rating"])
                rating = rating_element.text.strip()
            except NoSuchElementException:
                rating = None

            # DISCOUNT (Pourcentage de réduction)
            try:
                discount = article.find_element(By.CSS_SELECTOR, CSS_SELECTORS["discount"]).text.strip()
            except NoSuchElementException:
                discount = None

            # On ne garde que les produits avec au moins un titre et un prix
            if titre and prix:
                return {
                    "Titre": titre,
                    "Prix_Actuel": prix,
                    "Ancien_Prix": ancien_prix,
                    "Discount": discount,
                    "Rating": rating,
                    "Image_URL": img_url,
                    "Source": RPA_CONFIG["source_name"],
                    "Date_Collecte": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
        except Exception as e:
            logger.warning(f"Erreur extraction produit: {e}")

        return None

    def scraper_page(self, page_num):
        """Scrape une page spécifique avec système de retry."""
        # Gestion de l'URL avec pagination (compatible avec URL de recherche)
        if "?" in self.url_base:
            url = f"{self.url_base}&page={page_num}"
        else:
            url = f"{self.url_base}?page={page_num}"

        for attempt in range(1, self.retry_count + 1):
            logger.info(f"Traitement page {page_num} (tentative {attempt}/{self.retry_count}): {url}")

            try:
                self.driver.get(url)
                time.sleep(self.delai)

                # Fermer les popups éventuelles
                self.fermer_popup()

                # Attendre que les produits soient chargés
                try:
                    WebDriverWait(self.driver, RPA_CONFIG["timeout"]).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, CSS_SELECTORS["product_container"]))
                    )
                except TimeoutException:
                    if attempt < self.retry_count:
                        logger.warning(f"Timeout sur la page {page_num}, nouvelle tentative...")
                        time.sleep(2)
                        continue
                    else:
                        logger.warning(f"Timeout final sur la page {page_num}")
                        return []

                # Scroll progressif pour charger les images lazy-loaded
                for scroll_pct in [0.3, 0.5, 0.7, 1.0]:
                    self.driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight * {scroll_pct});")
                    time.sleep(0.5)

                time.sleep(1)

                # Extraction des produits
                articles = self.driver.find_elements(By.CSS_SELECTOR, CSS_SELECTORS["product_container"])
                logger.info(f"  -> {len(articles)} produits trouvés")

                page_products = []
                for article in articles:
                    product = self.extraire_produit(article)
                    if product:
                        page_products.append(product)

                return page_products

            except Exception as e:
                if attempt < self.retry_count:
                    logger.warning(f"Erreur page {page_num}: {e}, nouvelle tentative...")
                    time.sleep(2)
                else:
                    logger.error(f"Erreur finale page {page_num}: {e}")
                    return []

        return []

    def lancer_scraping(self):
        """Lance le processus complet de scraping."""
        logger.info("=" * 50)
        logger.info("DÉMARRAGE DU ROBOT RPA - SmartMarketWatch")
        logger.info("=" * 50)
        logger.info(f"URL cible: {self.url_base}")
        logger.info(f"Pages à scraper: {self.pages_a_scraper}")

        try:
            self.configurer_navigateur()

            for page in range(1, self.pages_a_scraper + 1):
                products = self.scraper_page(page)
                self.products.extend(products)
                logger.info(f"  -> {len(products)} produits extraits de la page {page}")

            logger.info("=" * 50)
            logger.info(f"SCRAPING TERMINÉ: {len(self.products)} produits au total")
            logger.info("=" * 50)

        except Exception as e:
            logger.error(f"Erreur critique: {e}")
            raise
        finally:
            if self.driver:
                self.driver.quit()
                logger.info("Navigateur fermé")

        return self.products

    def sauvegarder_csv(self, filepath=None):
        """Sauvegarde les données en CSV."""
        if not self.products:
            logger.warning("Aucun produit à sauvegarder!")
            return None

        filepath = filepath or RAW_DATA_FILE
        df = pd.DataFrame(self.products)

        # Créer le dossier parent si nécessaire
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

        # Sauvegarder avec encodage UTF-8 BOM pour Excel
        df.to_csv(filepath, index=False, encoding="utf-8-sig")
        logger.info(f"Données sauvegardées: {filepath}")
        logger.info(f"  -> {len(df)} lignes, {len(df.columns)} colonnes")

        return df


def main():
    """Point d'entrée principal du script RPA."""
    scraper = JumiaScraper()

    try:
        # Lancer le scraping
        scraper.lancer_scraping()

        # Sauvegarder les résultats
        df = scraper.sauvegarder_csv()

        if df is not None:
            print("\n" + "=" * 50)
            print("RÉSUMÉ DES DONNÉES COLLECTÉES")
            print("=" * 50)
            print(f"Nombre total de produits: {len(df)}")
            print(f"Colonnes: {list(df.columns)}")
            print("\nAperçu des 5 premiers produits:")
            print(df[["Titre", "Prix_Actuel"]].head().to_string())
            print("\n Fichier prêt pour l'équipe IA!")

    except Exception as e:
        logger.error(f"Erreur lors de l'exécution: {e}")
        raise


if __name__ == "__main__":
    main()
