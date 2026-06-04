-- ============================================================
-- PALWORLD DATABASE - Requêtes d'analyse exploratoire
-- ============================================================

USE palworld_database;

-- ── (a) Distribution de la taille ──────────────────────────────────────
SELECT volume_size,
       COUNT(*) AS nb_pals,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM combat_attribute), 1) AS pct
FROM combat_attribute
GROUP BY volume_size
ORDER BY nb_pals DESC;

-- ── (b) Distribution des éléments ─────────────────────────────────────
SELECT element1, COUNT(*) AS nb_pals
FROM combat_attribute
GROUP BY element1
ORDER BY nb_pals DESC;

-- ── (c) Distribution des HP ────────────────────────────────────────────
SELECT MIN(hp) AS hp_min, ROUND(AVG(hp),1) AS hp_moyen,
       ROUND(STDDEV(hp),1) AS hp_ecart_type, MAX(hp) AS hp_max
FROM combat_attribute;

-- ── (d) Distribution de la rareté ─────────────────────────────────────
SELECT rarity, COUNT(*) AS nb_pals,
       GROUP_CONCAT(name ORDER BY name SEPARATOR ', ') AS pals
FROM combat_attribute
GROUP BY rarity
ORDER BY rarity;

-- ── (e) Consommation alimentaire ───────────────────────────────────────
SELECT food_intake, COUNT(*) AS nb_pals
FROM job_skill
WHERE food_intake IS NOT NULL
GROUP BY food_intake
ORDER BY food_intake;

-- ── (f) Pals productifs au ranch ──────────────────────────────────────
SELECT name, ranch_item, pasture_min_output
FROM job_skill
WHERE ranch_item IS NOT NULL
ORDER BY name;

-- ── (g) Top 10 Pals les plus puissants ────────────────────────────────
SELECT name, hp, melee_attack, remote_attack, defense, rarity, volume_size,
       (hp + melee_attack * 2 + defense) AS combat_score
FROM combat_attribute
ORDER BY combat_score DESC
LIMIT 10;

-- ── (h) Corrélation attaque / défense (approx SQL) ────────────────────
SELECT ROUND(AVG(melee_attack),1) AS avg_atk,
       ROUND(AVG(defense),1) AS avg_def,
       ROUND(AVG(hp),1) AS avg_hp,
       ROUND(AVG(craft_speed),1) AS avg_craft
FROM combat_attribute;

-- ── (i) Rareté vs attributs ────────────────────────────────────────────
SELECT rarity,
       ROUND(AVG(hp),1) AS avg_hp,
       ROUND(AVG(melee_attack),1) AS avg_attack,
       ROUND(AVG(defense),1) AS avg_defense,
       COUNT(*) AS nb_pals
FROM combat_attribute
GROUP BY rarity
ORDER BY rarity;

-- ── (j) Rareté moyenne des Pals à attaque max ─────────────────────────
SELECT AVG(rarity) AS rarete_moyenne, COUNT(*) AS nb,
       GROUP_CONCAT(name ORDER BY name) AS pals_concernes
FROM combat_attribute
WHERE melee_attack = (SELECT MAX(melee_attack) FROM combat_attribute);

-- ── (k) Taille vs performance au combat ───────────────────────────────
SELECT volume_size,
       ROUND(AVG(hp),1) AS avg_hp,
       ROUND(AVG(melee_attack),1) AS avg_attack,
       ROUND(AVG(defense),1) AS avg_defense,
       ROUND(AVG(hp + melee_attack*2 + defense),1) AS avg_score,
       COUNT(*) AS nb_pals
FROM combat_attribute
GROUP BY volume_size
ORDER BY avg_score DESC;

-- ── (l) Vitesse vs efficacité au combat ───────────────────────────────
SELECT name, run_speed,
       (melee_attack + defense) AS combat_power,
       (hp + melee_attack*2 + defense) AS combat_score
FROM combat_attribute
WHERE run_speed IS NOT NULL
ORDER BY run_speed DESC
LIMIT 15;

-- ── (m) Équipe équilibrée de 5 Pals ───────────────────────────────────
-- Tank
SELECT 'Tank' AS role, name, hp AS stat_cle FROM combat_attribute ORDER BY hp DESC LIMIT 1;
-- Attaquant
SELECT 'Attaquant', name, melee_attack FROM combat_attribute ORDER BY melee_attack DESC LIMIT 1;
-- Défenseur
SELECT 'Défenseur', name, defense FROM combat_attribute ORDER BY defense DESC LIMIT 1;
-- Rapide
SELECT 'Rapide', name, run_speed FROM combat_attribute ORDER BY run_speed DESC LIMIT 1;
-- Polyvalent
SELECT 'Polyvalent', name, (hp+melee_attack*2+defense) FROM combat_attribute
ORDER BY (hp+melee_attack*2+defense) DESC LIMIT 1;

-- ── (n) Compétences les plus répandues ────────────────────────────────
SELECT 'Allumer feu'   AS competence, SUM(make_fire)      AS total FROM job_skill UNION ALL
SELECT 'Arrosage',      SUM(watering)       FROM job_skill UNION ALL
SELECT 'Plantation',    SUM(planting)       FROM job_skill UNION ALL
SELECT 'Électricité',   SUM(electricity)    FROM job_skill UNION ALL
SELECT 'Travail manuel',SUM(manual)         FROM job_skill UNION ALL
SELECT 'Collecte',      SUM(collection)     FROM job_skill UNION ALL
SELECT 'Abattage',      SUM(logging)        FROM job_skill UNION ALL
SELECT 'Minage',        SUM(mining)         FROM job_skill UNION ALL
SELECT 'Pharmacie',     SUM(pharmaceutical) FROM job_skill UNION ALL
SELECT 'Refroidissement',SUM(cool_down)     FROM job_skill UNION ALL
SELECT 'Élevage',       SUM(pasture)        FROM job_skill UNION ALL
SELECT 'Transport',     SUM(carry)          FROM job_skill
ORDER BY total DESC;

-- ── (p) Nombre de Pals pour le travail de nuit ────────────────────────
SELECT COUNT(*) AS nb_pals_nuit FROM job_skill WHERE night_shift = TRUE;

-- ── (q) Caractéristiques des Pals nocturnes ───────────────────────────
SELECT js.name, ca.rarity, ca.volume_size, ca.element1,
       ca.hp, ca.melee_attack, ca.defense, js.total_skills
FROM job_skill js
JOIN combat_attribute ca ON js.name = ca.name
WHERE js.night_shift = TRUE
ORDER BY ca.rarity DESC;

-- ── (r) Rareté moyenne vs nb compétences ──────────────────────────────
SELECT js.total_skills,
       ROUND(AVG(ca.rarity),1) AS avg_rarity,
       COUNT(*) AS nb_pals
FROM job_skill js
JOIN combat_attribute ca ON js.name = ca.name
WHERE js.total_skills IS NOT NULL
GROUP BY js.total_skills
ORDER BY js.total_skills DESC;

-- ── (s) Top 10 vitesse de travail ─────────────────────────────────────
SELECT name, work_speed, total_skills
FROM job_skill
WHERE work_speed IS NOT NULL
ORDER BY work_speed DESC
LIMIT 10;

-- ── (t) Top 15 taux de capture ────────────────────────────────────────
SELECT name, catch_rate, rarity
FROM combat_attribute
WHERE catch_rate IS NOT NULL
ORDER BY catch_rate DESC
LIMIT 15;

-- ── (u) Boss avec le score le plus élevé ──────────────────────────────
SELECT name, hp, melee_attack, defense,
       (hp + melee_attack * 2 + defense) AS combat_score,
       'Tower Boss' AS boss_type
FROM tower_boss
UNION ALL
SELECT boss_name, hp, melee_attack, defense,
       (hp + melee_attack * 2 + defense),
       'Ordinary Boss'
FROM ordinary_boss
ORDER BY combat_score DESC
LIMIT 10;

-- ── (v) Répartition des niveaux d'apparition ──────────────────────────
SELECT
    CASE
        WHEN min_level <= 10 THEN 'Niveau 1-10 (Débutant)'
        WHEN min_level <= 20 THEN 'Niveau 11-20 (Intermédiaire)'
        WHEN min_level <= 30 THEN 'Niveau 21-30 (Avancé)'
        ELSE 'Niveau 31+ (Expert)'
    END AS tranche,
    COUNT(*) AS nb_pals
FROM refresh_area
WHERE min_level IS NOT NULL
GROUP BY tranche
ORDER BY MIN(min_level);

-- ── (w) Répartition des zones d'apparition ────────────────────────────
SELECT area, COUNT(*) AS nb_pals,
       MIN(min_level) AS lv_min,
       MAX(max_level) AS lv_max
FROM refresh_area
WHERE area IS NOT NULL
GROUP BY area
ORDER BY nb_pals DESC;
