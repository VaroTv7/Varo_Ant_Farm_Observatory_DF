import sqlite3
import os

DB_PATH = "/data/observatory.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # World Info
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS world (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        last_updated TEXT
    )""")
    
    # Civilizations (Entities)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS civilizations (
        id INTEGER PRIMARY KEY,
        name TEXT,
        race TEXT,
        type TEXT
    )""")
    
    # Historical Figures (Dwarves, Elves, Animals, etc.)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS historical_figures (
        id INTEGER PRIMARY KEY,
        name TEXT,
        race TEXT,
        caste TEXT,
        birth_year INTEGER,
        death_year INTEGER,
        active BOOLEAN
    )""")
    
    # Relationships for family trees (Parent-Child, Spouse)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS hf_links (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hf_id INTEGER,
        link_type TEXT,
        target_hf_id INTEGER,
        FOREIGN KEY(hf_id) REFERENCES historical_figures(id),
        FOREIGN KEY(target_hf_id) REFERENCES historical_figures(id)
    )""")
    
    # Artifacts
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS artifacts (
        id INTEGER PRIMARY KEY,
        name TEXT,
        item_type TEXT,
        material TEXT
    )""")
    
    # Events
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY,
        year INTEGER,
        type TEXT,
        description TEXT
    )""")
    
    # Favorites / Tracking (user watchlists)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS favorites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entity_type TEXT, -- 'figure', 'civilization', 'artifact'
        entity_id INTEGER,
        notes TEXT,
        UNIQUE(entity_type, entity_id)
    )""")
    
    conn.commit()
    conn.close()

def clear_parsed_data():
    conn = get_db()
    cursor = conn.cursor()
    # Limpiamos todo menos las preferencias del usuario (favorites)
    cursor.execute("DELETE FROM world")
    cursor.execute("DELETE FROM civilizations")
    cursor.execute("DELETE FROM historical_figures")
    cursor.execute("DELETE FROM hf_links")
    cursor.execute("DELETE FROM artifacts")
    cursor.execute("DELETE FROM events")
    conn.commit()
    conn.close()

if not os.path.exists(DB_PATH) and os.path.exists("/data"):
    init_db()
