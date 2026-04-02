import xml.etree.ElementTree as ET
import os
import datetime
from database import get_db, init_db, clear_parsed_data

LEGENDS_PATH = "/df-data/legends.xml"
BATCH_SIZE = 500

def parse_legends_file():
    if not os.path.exists(LEGENDS_PATH):
        print(f"[Parser] Archivo {LEGENDS_PATH} no encontrado.")
        return False

    print(f"[Parser] Iniciando parseo masivo de {LEGENDS_PATH}...")
    init_db()
    clear_parsed_data()
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Añadir metadata del mundo
    cursor.execute("INSERT INTO world (name, last_updated) VALUES (?, ?)", 
                   ("Mundo en procesamiento...", datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
    
    context = ET.iterparse(LEGENDS_PATH, events=("end",))
    
    civs_batch = []
    hf_batch = []
    hf_links_batch = []
    arts_batch = []
    events_batch = []
    
    world_name = "Mundo Desconocido"
    
    for event, elem in context:
        if elem.tag == "name" and elem.getparent() and elem.getparent().tag == "df_world":
            world_name = elem.text.title() if elem.text else world_name
            
        elif elem.tag == "entity":
            try:
                e_id = int(elem.findtext("id", "-1"))
                e_name = elem.findtext("name", "Desconocido").title()
                e_race = elem.findtext("race", "Desconocida").title()
                e_type = elem.findtext("type", "")
                if e_id != -1 and e_name != "Desconocido":
                    civs_batch.append((e_id, e_name, e_race, e_type))
            except: pass
            
        elif elem.tag == "historical_figure":
            try:
                hf_id = int(elem.findtext("id", "-1"))
                hf_name = elem.findtext("name", "Sin nombre").title()
                hf_race = elem.findtext("race", "Desconocida").title()
                hf_caste = elem.findtext("caste", "").title()
                hf_birth = int(elem.findtext("birth_year", "-1"))
                d_year = elem.findtext("death_year", "")
                hf_death = int(d_year) if d_year else None
                hf_active = d_year == ""
                
                if hf_id != -1:
                    hf_batch.append((hf_id, hf_name, hf_race, hf_caste, hf_birth, hf_death, hf_active))
                    
                    # Parsear los links (familia)
                    for link in elem.findall("hf_link"):
                        link_type = link.findtext("link_type", "")
                        target_id = int(link.findtext("target_hf", "-1"))
                        if target_id != -1 and link_type:
                            hf_links_batch.append((hf_id, link_type, target_id))
            except: pass
            
        elif elem.tag == "artifact":
            try:
                a_id = int(elem.findtext("id", "-1"))
                a_name = elem.findtext("name", "Sin nombre").title()
                a_type = elem.findtext("item_type", "Objeto").title()
                a_mat = elem.findtext("mat_state", "").title()
                if a_id != -1:
                    arts_batch.append((a_id, a_name, a_type, a_mat))
            except: pass
            
        elif elem.tag == "historical_event":
            try:
                ev_id = int(elem.findtext("id", "-1"))
                ev_year = int(elem.findtext("year", "-1"))
                ev_type = elem.findtext("type", "evento").replace("_", " ").title()
                # We could capture event descriptions here if available in XML, or format the type.
                if ev_id != -1:
                    events_batch.append((ev_id, ev_year, ev_type, ""))
            except: pass
            
        # Liberar memoria procesando batches y limpiando el nodo DOM
        if len(hf_batch) >= BATCH_SIZE:
            cursor.executemany("INSERT OR REPLACE INTO civilizations VALUES (?, ?, ?, ?)", civs_batch)
            cursor.executemany("INSERT OR REPLACE INTO historical_figures VALUES (?, ?, ?, ?, ?, ?, ?)", hf_batch)
            cursor.executemany("INSERT INTO hf_links (hf_id, link_type, target_hf_id) VALUES (?, ?, ?)", hf_links_batch)
            cursor.executemany("INSERT OR REPLACE INTO artifacts VALUES (?, ?, ?, ?)", arts_batch)
            cursor.executemany("INSERT OR REPLACE INTO events VALUES (?, ?, ?, ?)", events_batch)
            conn.commit()
            
            civs_batch.clear()
            hf_batch.clear()
            hf_links_batch.clear()
            arts_batch.clear()
            events_batch.clear()
            
        # Esta es la magia que evita el OOM Kill: limpiar el elemento para que garbage collector actúe
        elem.clear()

    # Flush final
    cursor.executemany("INSERT OR REPLACE INTO civilizations VALUES (?, ?, ?, ?)", civs_batch)
    cursor.executemany("INSERT OR REPLACE INTO historical_figures VALUES (?, ?, ?, ?, ?, ?, ?)", hf_batch)
    cursor.executemany("INSERT INTO hf_links (hf_id, link_type, target_hf_id) VALUES (?, ?, ?)", hf_links_batch)
    cursor.executemany("INSERT OR REPLACE INTO artifacts VALUES (?, ?, ?, ?)", arts_batch)
    cursor.executemany("INSERT OR REPLACE INTO events VALUES (?, ?, ?, ?)", events_batch)
    
    # Actualizar nombre final del mundo
    cursor.execute("UPDATE world SET name = ? WHERE id = (SELECT max(id) FROM world)", (world_name,))
    conn.commit()
    conn.close()
    
    print(f"[Parser] Terminado con éxito. Mundo: {world_name}")
    return True

if __name__ == "__main__":
    parse_legends_file()
