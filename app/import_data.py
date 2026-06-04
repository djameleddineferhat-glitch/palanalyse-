"""
import_data.py — Import automatisé des 6 CSV dans MariaDB/MySQL
Usage : python import_data.py
"""

import pandas as pd
import sqlalchemy
import os
import sys

# ── Configuration ──────────────────────────────────────────────────────────
DB_USER     = "root"
DB_PASSWORD = "r3dgh0st!"   # ← à remplacer
DB_HOST     = "localhost"
DB_PORT     = 3306
DB_NAME     = "palworld_database"
DATA_DIR    = os.path.join(os.path.dirname(__file__), "..", "data")

# ── Connexion ──────────────────────────────────────────────────────────────
def get_engine():
    url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return sqlalchemy.create_engine(url)

# ── Nettoyage générique ────────────────────────────────────────────────────
def clean_df(df):
    """Renommer colonnes, convertir types, nettoyer strings."""
    df.columns = [c.strip().replace(' ', '_').replace('(', '').replace(')', '')
                  .replace('/', '_').lower() for c in df.columns]
    # Convertir colonnes % en float
    for col in df.columns:
        if df[col].dtype == object:
            sample = df[col].dropna().head(5).astype(str)
            if sample.str.endswith('%').any():
                df[col] = df[col].astype(str).str.replace('%', '', regex=False)
                df[col] = pd.to_numeric(df[col], errors='coerce')
    # Remplir NaN string
    df = df.fillna({col: '' for col in df.select_dtypes(include='object').columns})
    return df

# ── Import de chaque table ─────────────────────────────────────────────────
def import_tables(engine):
    tables = {
        "combat_attribute": {
            "file": "Palworld_Data--Palu_combat_attribute_table.csv",
            "skiprows": 1
        },
        "job_skill": {
            "file": "Palworld_Data-Palu_Job_Skills_Table.csv",
            "skiprows": 1
        },
        "hidden_attribute": {
            "file": "Palworld_Data-hide_pallu_attributes.csv",
            "skiprows": 0
        },
        "refresh_area": {
            "file": "Palworld_Data--Palu_refresh_level.csv",
            "skiprows": 1
        },
        "tower_boss": {
            "file": "Palworld_Data-Tower_BOSS_attribute_comparison.csv",
            "skiprows": 0
        },
        "ordinary_boss": {
            "file": "Palworld_Data-comparison_of_ordinary_BOSS_attributes.csv",
            "skiprows": 3
        },
    }

    for table_name, cfg in tables.items():
        filepath = os.path.join(DATA_DIR, cfg["file"])
        if not os.path.exists(filepath):
            print(f"⚠️  Fichier introuvable : {filepath}")
            continue
        try:
            df = pd.read_csv(filepath, skiprows=cfg["skiprows"], encoding='utf-8',
                             on_bad_lines='skip')
            df = clean_df(df)
            df.to_sql(table_name, engine, if_exists="replace", index=False)
            print(f"✅  {table_name:<25} → {len(df):>4} lignes importées")
        except Exception as e:
            print(f"❌  {table_name}: {e}")

if __name__ == "__main__":
    print("🎮 Palworld Database — Import des données\n")
    try:
        engine = get_engine()
        import_tables(engine)
        print("\n✅ Import terminé !")
    except Exception as e:
        print(f"❌ Erreur de connexion : {e}")
        print("   → Vérifiez DB_PASSWORD et que MariaDB est démarré.")
        sys.exit(1)
