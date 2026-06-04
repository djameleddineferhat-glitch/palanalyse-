-- ============================================================
-- PALWORLD DATABASE - Création des tables
-- Base : palworld_database
-- ============================================================

CREATE DATABASE IF NOT EXISTS palworld_database
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE palworld_database;

-- Table 1 : Attributs de combat
CREATE TABLE IF NOT EXISTS combat_attribute (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    name             VARCHAR(100) NOT NULL,
    code_name        VARCHAR(100),
    is_pal           BOOLEAN DEFAULT TRUE,
    volume_size      ENUM('XS','S','M','L','XL'),
    rarity           INT,
    element1         VARCHAR(30),
    element2         VARCHAR(30),
    category         VARCHAR(100),
    hp               INT,
    melee_attack     INT,
    remote_attack    INT,
    defense          INT,
    support          INT,
    craft_speed      INT,
    run_speed        FLOAT,
    sprint_speed     FLOAT,
    slow_walk_speed  FLOAT,
    male_probability FLOAT,
    catch_rate       FLOAT,
    exp_multiplier   FLOAT,
    price            INT,
    nocturnal        BOOLEAN DEFAULT FALSE
);

-- Table 2 : Compétences de travail
CREATE TABLE IF NOT EXISTS job_skill (
    id                   INT AUTO_INCREMENT PRIMARY KEY,
    name                 VARCHAR(100) NOT NULL,
    food_intake          INT,
    night_shift          BOOLEAN DEFAULT FALSE,
    total_skills         INT,
    make_fire            INT DEFAULT 0,
    watering             INT DEFAULT 0,
    planting             INT DEFAULT 0,
    electricity          INT DEFAULT 0,
    manual               INT DEFAULT 0,
    collection           INT DEFAULT 0,
    logging              INT DEFAULT 0,
    mining               INT DEFAULT 0,
    pharmaceutical       INT DEFAULT 0,
    cool_down            INT DEFAULT 0,
    pasture              INT DEFAULT 0,
    carry                INT DEFAULT 0,
    work_speed           FLOAT,
    ranch_item           VARCHAR(200),
    pasture_min_output   VARCHAR(100)
);

-- Table 3 : Attributs cachés
CREATE TABLE IF NOT EXISTS hidden_attribute (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    chinese_name     VARCHAR(100),
    english_name     VARCHAR(100),
    code_name        VARCHAR(100),
    is_pal           BOOLEAN,
    is_boss          BOOLEAN DEFAULT FALSE,
    volume_size      VARCHAR(10),
    rarity           INT,
    element1         VARCHAR(30),
    element2         VARCHAR(30),
    category         VARCHAR(100),
    hp               INT,
    melee_attack     INT,
    remote_attack    INT,
    defense          INT,
    support          INT,
    craft_speed      INT,
    nocturnal        BOOLEAN DEFAULT FALSE,
    food_amount      INT,
    male_probability FLOAT,
    capture_rate     FLOAT
);

-- Table 4 : Zones et niveaux d'apparition
CREATE TABLE IF NOT EXISTS refresh_area (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    name         VARCHAR(100),
    min_level    INT,
    max_level    INT,
    area         VARCHAR(200),
    refresh_type VARCHAR(50),
    night_only   BOOLEAN DEFAULT FALSE
);

-- Table 5 : Tower Boss
CREATE TABLE IF NOT EXISTS tower_boss (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    name          VARCHAR(100) NOT NULL,
    element1      VARCHAR(30),
    hp            INT,
    melee_attack  INT,
    remote_attack INT,
    defense       INT,
    run_speed     INT,
    ride_speed    INT,
    support       INT,
    craft_speed   INT
);

-- Table 6 : Ordinary Boss
CREATE TABLE IF NOT EXISTS ordinary_boss (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    boss_name     VARCHAR(100) NOT NULL,
    base_name     VARCHAR(100),
    element1      VARCHAR(30),
    hp            INT,
    melee_attack  INT,
    remote_attack INT,
    defense       INT,
    run_speed     FLOAT
);
