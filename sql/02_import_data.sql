-- ============================================================
-- PALWORLD DATABASE - Import des données depuis CSV
-- Utiliser après avoir copié les CSV dans le dossier MySQL secure_file_priv
-- OU utiliser le script Python import_data.py
-- ============================================================

USE palworld_database;

-- Option A : LOAD DATA INFILE (adapter le chemin)
-- LOAD DATA INFILE '/path/to/Palworld_Data--Palu_combat_attribute_table.csv'
-- INTO TABLE combat_attribute
-- FIELDS TERMINATED BY ',' ENCLOSED BY '"'
-- LINES TERMINATED BY '\n'
-- IGNORE 2 ROWS;

-- Option B (recommandée) : utiliser le script Python
-- python import_data.py

-- Vérification post-import
SELECT 'combat_attribute' AS table_name, COUNT(*) AS nb_rows FROM combat_attribute
UNION ALL
SELECT 'job_skill', COUNT(*) FROM job_skill
UNION ALL
SELECT 'hidden_attribute', COUNT(*) FROM hidden_attribute
UNION ALL
SELECT 'refresh_area', COUNT(*) FROM refresh_area
UNION ALL
SELECT 'tower_boss', COUNT(*) FROM tower_boss
UNION ALL
SELECT 'ordinary_boss', COUNT(*) FROM ordinary_boss;
