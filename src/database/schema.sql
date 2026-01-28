-- ============================================
-- SMART MARKET WATCH - DATABASE SCHEMA
-- Author: Ouaail El AOUAD - Database Architect
-- ============================================

-- Enable foreign keys
PRAGMA foreign_keys = ON;

-- ============================================
-- DIMENSION TABLES
-- ============================================

-- Dimension: Marques (Brands)
DROP TABLE IF EXISTS Dim_Marques;
CREATE TABLE Dim_Marques (
    marque_id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_marque TEXT NOT NULL UNIQUE
);
CREATE INDEX idx_marque_nom ON Dim_Marques(nom_marque);

-- Dimension: Sources (E-commerce sites)
DROP TABLE IF EXISTS Dim_Sources;
CREATE TABLE Dim_Sources (
    source_id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_source TEXT NOT NULL UNIQUE
);
CREATE INDEX idx_source_nom ON Dim_Sources(nom_source);

-- Dimension: Dates (Time dimension)
DROP TABLE IF EXISTS Dim_Dates;
CREATE TABLE Dim_Dates (
    date_id INTEGER PRIMARY KEY,
    date_complete TEXT NOT NULL UNIQUE,
    annee INTEGER NOT NULL,
    mois INTEGER NOT NULL,
    jour INTEGER NOT NULL,
    trimestre INTEGER NOT NULL,
    jour_semaine TEXT NOT NULL
);
CREATE INDEX idx_date_complete ON Dim_Dates(date_complete);
CREATE INDEX idx_annee_mois ON Dim_Dates(annee, mois);

-- Dimension: Produits (Products)
DROP TABLE IF EXISTS Dim_Produits;
CREATE TABLE Dim_Produits (
    produit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    titre TEXT NOT NULL,
    image_url TEXT,
    resume_produit TEXT,
    keywords_tfidf TEXT,
    gamme TEXT
);
CREATE INDEX idx_gamme ON Dim_Produits(gamme);

-- Dimension: Specifications (Technical specs)
DROP TABLE IF EXISTS Dim_Specifications;
CREATE TABLE Dim_Specifications (
    spec_id INTEGER PRIMARY KEY AUTOINCREMENT,
    cpu TEXT,
    generation_cpu REAL,
    ram_gb REAL,
    ram_type TEXT,
    ram_frequence REAL,
    stockage_total_gb REAL,
    type_stockage TEXT,
    stockage_ssd_gb REAL,
    stockage_hdd_gb REAL,
    stockage_nvme INTEGER,
    ecran_taille REAL,
    ecran_resolution_width INTEGER,
    ecran_resolution_height INTEGER,
    ecran_type TEXT,
    ecran_tactile INTEGER,
    gpu_marque TEXT,
    gpu_serie TEXT,
    gpu_modele TEXT,
    wifi_version TEXT,
    bluetooth_version TEXT,
    usb_type TEXT,
    batterie_capacite REAL,
    batterie_autonomie REAL
);
CREATE INDEX idx_cpu ON Dim_Specifications(cpu);
CREATE INDEX idx_ram ON Dim_Specifications(ram_gb);

-- Dimension: Qualite (Quality assessment)
DROP TABLE IF EXISTS Dim_Qualite;
CREATE TABLE Dim_Qualite (
    qualite_id INTEGER PRIMARY KEY AUTOINCREMENT,
    etat_produit TEXT,
    taux_completude REAL,
    sentiment_bert TEXT,
    sentiment_score_bert REAL,
    anomalie_prix_zscore INTEGER,
    anomalie_prix_iqr INTEGER,
    type_anomalie_prix TEXT,
    anomalie_ml INTEGER,
    produit_suspect INTEGER,
    raisons_suspicion TEXT,
    recommandation_achat TEXT
);
CREATE INDEX idx_etat ON Dim_Qualite(etat_produit);
CREATE INDEX idx_sentiment ON Dim_Qualite(sentiment_bert);

-- ============================================
-- FACT TABLE (Central table)
-- ============================================

DROP TABLE IF EXISTS FACT_Ventes;
CREATE TABLE FACT_Ventes (
    vente_id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Foreign Keys
    produit_id INTEGER NOT NULL,
    marque_id INTEGER NOT NULL,
    date_id INTEGER NOT NULL,
    source_id INTEGER NOT NULL,
    spec_id INTEGER,
    qualite_id INTEGER,
    
    -- Price metrics
    prix_actuel REAL,
    ancien_prix REAL,
    reduction_reelle REAL,
    discount_affiche TEXT,
    
    -- Quality metrics
    rating_score REAL,
    rating_text TEXT,
    sentiment_score REAL,
    
    -- Anomaly metrics
    anomalie_score_ml REAL,
    anomalie_score_normalized REAL,
    incoherence_spec_prix TEXT,
    severite_incoherence INTEGER,
    
    -- Confidence metrics
    indice_confiance REAL,
    score_fiabilite_vendeur REAL,
    
    -- Timestamp
    date_collecte TEXT,
    
    -- Foreign key constraints
    FOREIGN KEY (produit_id) REFERENCES Dim_Produits(produit_id) ON DELETE CASCADE,
    FOREIGN KEY (marque_id) REFERENCES Dim_Marques(marque_id) ON DELETE CASCADE,
    FOREIGN KEY (date_id) REFERENCES Dim_Dates(date_id) ON DELETE CASCADE,
    FOREIGN KEY (source_id) REFERENCES Dim_Sources(source_id) ON DELETE CASCADE,
    FOREIGN KEY (spec_id) REFERENCES Dim_Specifications(spec_id) ON DELETE SET NULL,
    FOREIGN KEY (qualite_id) REFERENCES Dim_Qualite(qualite_id) ON DELETE SET NULL
);

-- Indexes for performance
CREATE INDEX idx_prix ON FACT_Ventes(prix_actuel);
CREATE INDEX idx_rating ON FACT_Ventes(rating_score);
CREATE INDEX idx_marque ON FACT_Ventes(marque_id);
CREATE INDEX idx_date ON FACT_Ventes(date_id);

-- ============================================
-- VIEWS FOR BI
-- ============================================

-- Complete analysis view
DROP VIEW IF EXISTS V_Analyse_Complete;
CREATE VIEW V_Analyse_Complete AS
SELECT 
    f.vente_id,
    p.titre,
    p.gamme,
    m.nom_marque,
    s.nom_source,
    d.date_complete,
    d.annee,
    d.mois,
    f.prix_actuel,
    f.ancien_prix,
    f.reduction_reelle,
    f.rating_score,
    sp.cpu,
    sp.ram_gb,
    sp.stockage_total_gb,
    q.sentiment_bert,
    q.recommandation_achat,
    f.indice_confiance
FROM FACT_Ventes f
LEFT JOIN Dim_Produits p ON f.produit_id = p.produit_id
LEFT JOIN Dim_Marques m ON f.marque_id = m.marque_id
LEFT JOIN Dim_Sources s ON f.source_id = s.source_id
LEFT JOIN Dim_Dates d ON f.date_id = d.date_id
LEFT JOIN Dim_Specifications sp ON f.spec_id = sp.spec_id
LEFT JOIN Dim_Qualite q ON f.qualite_id = q.qualite_id;

-- KPI: Price by brand
DROP VIEW IF EXISTS V_KPI_Prix_Marque;
CREATE VIEW V_KPI_Prix_Marque AS
SELECT 
    m.nom_marque,
    COUNT(*) as nombre_produits,
    ROUND(AVG(f.prix_actuel), 2) as prix_moyen,
    ROUND(MIN(f.prix_actuel), 2) as prix_min,
    ROUND(MAX(f.prix_actuel), 2) as prix_max
FROM FACT_Ventes f
JOIN Dim_Marques m ON f.marque_id = m.marque_id
WHERE f.prix_actuel IS NOT NULL
GROUP BY m.nom_marque;

-- KPI: Sentiment distribution
DROP VIEW IF EXISTS V_KPI_Sentiment;
CREATE VIEW V_KPI_Sentiment AS
SELECT 
    q.sentiment_bert,
    COUNT(*) as total_produits,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM FACT_Ventes), 2) as pourcentage
FROM FACT_Ventes f
JOIN Dim_Qualite q ON f.qualite_id = q.qualite_id
WHERE q.sentiment_bert IS NOT NULL
GROUP BY q.sentiment_bert;