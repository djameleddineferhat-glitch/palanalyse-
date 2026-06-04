-- ============================================================
-- PALWORLD DATABASE - Nettoyage et normalisation
-- ============================================================

USE palworld_database;

-- 1. Uniformiser les noms d'éléments (generally → Normal)
UPDATE combat_attribute SET element1 = 'Normal'   WHERE element1 = 'generally';
UPDATE combat_attribute SET element1 = 'Feu'      WHERE element1 = 'fire';
UPDATE combat_attribute SET element1 = 'Eau'      WHERE element1 = 'water';
UPDATE combat_attribute SET element1 = 'Plante'   WHERE element1 IN ('Wood','wood');
UPDATE combat_attribute SET element1 = 'Ténèbres' WHERE element1 = 'dark';
UPDATE combat_attribute SET element1 = 'Glace'    WHERE element1 = 'ice';
UPDATE combat_attribute SET element1 = 'Dragon'   WHERE element1 = 'dragon';
UPDATE combat_attribute SET element1 = 'Électricité' WHERE element1 = 'electricity';
UPDATE combat_attribute SET element1 = 'Terre'    WHERE element1 = 'land';

-- 2. Supprimer les doublons sur le nom
DELETE t1 FROM combat_attribute t1
INNER JOIN combat_attribute t2
WHERE t1.id > t2.id AND t1.name = t2.name;

DELETE t1 FROM job_skill t1
INNER JOIN job_skill t2
WHERE t1.id > t2.id AND t1.name = t2.name;

-- 3. Remplir les NULL numériques par 0
UPDATE combat_attribute SET melee_attack  = 0 WHERE melee_attack  IS NULL;
UPDATE combat_attribute SET remote_attack = 0 WHERE remote_attack IS NULL;
UPDATE combat_attribute SET defense       = 0 WHERE defense       IS NULL;
UPDATE combat_attribute SET hp            = 0 WHERE hp            IS NULL;
UPDATE combat_attribute SET craft_speed   = 0 WHERE craft_speed   IS NULL;

UPDATE job_skill SET make_fire      = 0 WHERE make_fire      IS NULL;
UPDATE job_skill SET watering       = 0 WHERE watering       IS NULL;
UPDATE job_skill SET planting       = 0 WHERE planting       IS NULL;
UPDATE job_skill SET electricity    = 0 WHERE electricity    IS NULL;
UPDATE job_skill SET manual         = 0 WHERE manual         IS NULL;
UPDATE job_skill SET collection     = 0 WHERE collection     IS NULL;
UPDATE job_skill SET logging        = 0 WHERE logging        IS NULL;
UPDATE job_skill SET mining         = 0 WHERE mining         IS NULL;
UPDATE job_skill SET pharmaceutical = 0 WHERE pharmaceutical IS NULL;
UPDATE job_skill SET cool_down      = 0 WHERE cool_down      IS NULL;
UPDATE job_skill SET pasture        = 0 WHERE pasture        IS NULL;
UPDATE job_skill SET carry          = 0 WHERE carry          IS NULL;
UPDATE job_skill SET night_shift    = FALSE WHERE night_shift IS NULL;

-- 4. Supprimer les Pals inexistants dans le jeu (hidden_attribute)
DELETE FROM hidden_attribute
WHERE english_name LIKE '%does not appear%'
   OR english_name IS NULL;

-- 5. Vérification
SELECT 'Doublons restants combat_attribute' AS check_name,
       COUNT(*) - COUNT(DISTINCT name) AS nb
FROM combat_attribute
UNION ALL
SELECT 'NULL hp restants', SUM(CASE WHEN hp IS NULL THEN 1 ELSE 0 END)
FROM combat_attribute
UNION ALL
SELECT 'NULL attack restants', SUM(CASE WHEN melee_attack IS NULL THEN 1 ELSE 0 END)
FROM combat_attribute;
