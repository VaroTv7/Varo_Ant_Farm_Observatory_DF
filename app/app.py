import os
import json
from flask import Flask, render_template, jsonify, request, g
from anthropic import Anthropic
from database import get_db, init_db
from watchdog import watchdog

app = Flask(__name__)

CLAUDE_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
APP_LANG = os.environ.get("APP_LANG", "es")

client = Anthropic(api_key=CLAUDE_API_KEY) if CLAUDE_API_KEY else None

# Inicializar Base de Datos en memoria flash del contenedor / volumen y arrancar watchdog
if not os.path.exists("/data/observatory.db") and os.path.exists("/data"):
    init_db()
watchdog.start()

# ── Translation System ───────────────────────────────────────────────────────

def load_translations(lang):
    try:
        path = f"translations/{lang}.json"
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

translations_cache = {
    "es": load_translations("es"),
    "en": load_translations("en")
}

@app.before_request
def before_request():
    lang = request.args.get("lang", APP_LANG)
    if lang not in translations_cache:
        lang = "en"
    g.lang = lang
    g.t = translations_cache[lang]

@app.context_processor
def inject_translate():
    def t(key, **kwargs):
        text = g.t.get(key, key)
        for k, v in kwargs.items():
            text = text.replace(f"{{{{{k}}}}}", str(v))
        return text
    return dict(t=t, current_lang=g.lang)

# ── Routes & Dashboard ───────────────────────────────────────────────────────

@app.route("/")
def index():
    conn = get_db()
    cursor = conn.cursor()
    
    world = cursor.execute("SELECT * FROM world ORDER BY id DESC LIMIT 1").fetchone()
    if not world:
        return render_template("index.html", world=None)
        
    stats = {
        "civs": cursor.execute("SELECT COUNT(id) FROM civilizations").fetchone()[0],
        "heroes": cursor.execute("SELECT COUNT(id) FROM historical_figures").fetchone()[0],
        "artifacts": cursor.execute("SELECT COUNT(id) FROM artifacts").fetchone()[0],
        "events": cursor.execute("SELECT COUNT(id) FROM events").fetchone()[0]
    }
    
    # Obtener favoritos globales del sistema
    favs_db = cursor.execute("SELECT entity_id, notes FROM favorites WHERE entity_type='figure'").fetchall()
    favorites = []
    for f in favs_db:
        fig = cursor.execute("SELECT id, name, race FROM historical_figures WHERE id=?", (f["entity_id"],)).fetchone()
        if fig:
            favorites.append({"id": fig["id"], "name": fig["name"], "race": fig["race"], "notes": f["notes"]})

    conn.close()
    return render_template("index.html", world=world, stats=stats, favorites=favorites)

@app.route("/api/favorite", methods=["POST"])
def toggle_favorite():
    data = request.json
    e_type = data.get("type")
    e_id = data.get("id")
    
    conn = get_db()
    cursor = conn.cursor()
    exist = cursor.execute("SELECT id FROM favorites WHERE entity_type=? AND entity_id=?", (e_type, e_id)).fetchone()
    
    if exist:
        cursor.execute("DELETE FROM favorites WHERE id=?", (exist["id"],))
        action = "removed"
    else:
        cursor.execute("INSERT INTO favorites (entity_type, entity_id) VALUES (?, ?)", (e_type, e_id))
        action = "added"
    
    conn.commit()
    conn.close()
    return jsonify({"success": True, "action": action})

# ── Claude RAG / Tool Calling ────────────────────────────────────────────────

tools_definition = [
    {
        "name": "buscar_figura",
        "description": "Busca una figura histórica (héroe, animal, demonio) por nombre y devuelve sus datos biográficos.",
        "input_schema": {
            "type": "object",
            "properties": {"nombre": {"type": "string", "description": "Nombre de la figura"}},
            "required": ["nombre"],
        },
    },
    {
        "name": "buscar_civilizacion",
        "description": "Busca una civilización/facción en el mundo por nombre o raza.",
        "input_schema": {
            "type": "object",
            "properties": {"raz_o_nombre": {"type": "string", "description": "Raza (dwarf, elf) o parte del nombre"}},
            "required": ["raz_o_nombre"],
        },
    }
]

def execute_tool(tool_name, tool_input):
    conn = get_db()
    cursor = conn.cursor()
    
    if tool_name == "buscar_figura":
        nombre = tool_input.get("nombre", "")
        # Buscamos con LIKE
        res = cursor.execute("SELECT * FROM historical_figures WHERE name LIKE ? LIMIT 5", (f"%{nombre}%",)).fetchall()
        if not res: return "No se encontraron figuras con ese nombre."
        return str([dict(r) for r in res])
        
    elif tool_name == "buscar_civilizacion":
        query = tool_input.get("raz_o_nombre", "")
        res = cursor.execute("SELECT * FROM civilizations WHERE name LIKE ? OR race LIKE ? LIMIT 5", (f"%{query}%", f"%{query}%")).fetchall()
        if not res: return "No se encontraron civilizaciones."
        return str([dict(r) for r in res])
        
    return "Herramienta no reconocida."

@app.route("/oracle")
def oracle():
    conn = get_db()
    cursor = conn.cursor()
    world = cursor.execute("SELECT * FROM world ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    return render_template("oracle.html", world=world)

@app.route("/api/oracle", methods=["POST"])
def oracle_api():
    if not client:
        return jsonify({"error": "API Key missing"}), 503
    
    data = request.get_json()
    question = data.get("question", "")
    
    conn = get_db()
    cursor = conn.cursor()
    world = cursor.execute("SELECT * FROM world ORDER BY id DESC LIMIT 1").fetchone()
    world_name = world["name"] if world else "Desconocido"
    conn.close()
    
    system_prompt = f"Eres el Cronista Omnisciente de {world_name}. Cuando el usuario pregunte por personajes o lugares específicos, usa las funciones (Tools) para leer la base de datos de Dwarf Fortress."
    
    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1000,
            system=system_prompt,
            tools=tools_definition,
            messages=[{"role": "user", "content": question}]
        )
        
        # Procesar posibles Tool Calls
        messages = [{"role": "user", "content": question}, {"role": "assistant", "content": response.content}]
        while response.stop_reason == "tool_use":
            tool_use = next(block for block in response.content if block.type == "tool_use")
            tool_name = tool_use.name
            tool_input = tool_use.input
            
            tool_result_str = execute_tool(tool_name, tool_input)
            
            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "content": tool_result_str,
                    }
                ]
            })
            
            response = client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=1000,
                system=system_prompt,
                tools=tools_definition,
                messages=messages
            )
            messages.append({"role": "assistant", "content": response.content})
            
        final_text = next(block.text for block in response.content if block.type == "text")
        return jsonify({"answer": final_text})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/heroes")
def heroes():
    conn = get_db()
    cursor = conn.cursor()
    world = cursor.execute("SELECT * FROM world ORDER BY id DESC LIMIT 1").fetchone()
    # Simple pagination placeholder or limit
    heroes_db = cursor.execute("SELECT * FROM historical_figures LIMIT 200").fetchall()
    
    # Check if favorited
    favs = {f["entity_id"] for f in cursor.execute("SELECT entity_id FROM favorites WHERE entity_type='figure'").fetchall()}
    conn.close()
    
    return render_template("heroes.html", world=world, heroes=heroes_db, favs=favs)

@app.route("/civilizations")
def civilizations():
    conn = get_db()
    cursor = conn.cursor()
    world = cursor.execute("SELECT * FROM world ORDER BY id DESC LIMIT 1").fetchone()
    civs = cursor.execute("SELECT * FROM civilizations LIMIT 200").fetchall()
    conn.close()
    return render_template("civilizations.html", world=world, civs=civs)

@app.route("/figure/<int:hf_id>")
def figure_detail(hf_id):
    conn = get_db()
    cursor = conn.cursor()
    world = cursor.execute("SELECT * FROM world ORDER BY id DESC LIMIT 1").fetchone()
    figure = cursor.execute("SELECT * FROM historical_figures WHERE id=?", (hf_id,)).fetchone()
    
    if not figure:
        conn.close()
        return "Figura no encontrada", 404
        
    # Get family
    links = cursor.execute("""
        SELECT l.link_type, f.id, f.name, f.race 
        FROM hf_links l 
        JOIN historical_figures f ON l.target_hf_id = f.id 
        WHERE l.hf_id = ?
    """, (hf_id,)).fetchall()
    
    # Check if favorited
    fav = cursor.execute("SELECT id FROM favorites WHERE entity_type='figure' AND entity_id=?", (hf_id,)).fetchone()
    
    conn.close()
    return render_template("figure_detail.html", world=world, figure=figure, links=links, is_fav=fav is not None)

@app.route("/timeline")
def timeline():
    conn = get_db()
    cursor = conn.cursor()
    world = cursor.execute("SELECT * FROM world ORDER BY id DESC LIMIT 1").fetchone()
    events = cursor.execute("SELECT * FROM events ORDER BY year DESC LIMIT 300").fetchall()
    conn.close()
    return render_template("timeline.html", world=world, events=events)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
