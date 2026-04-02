import os
import json
import xml.etree.ElementTree as ET
from flask import Flask, render_template, jsonify, request, g
from anthropic import Anthropic
from datetime import datetime

app = Flask(__name__)

LEGENDS_PATH = "/data/legends.xml"
CLAUDE_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
APP_LANG = os.environ.get("APP_LANG", "es")

client = Anthropic(api_key=CLAUDE_API_KEY) if CLAUDE_API_KEY else None

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

# ── Legends Parser ──────────────────────────────────────────────────────────

def parse_legends():
    if not os.path.exists(LEGENDS_PATH):
        return None
    try:
        tree = ET.parse(LEGENDS_PATH)
        root = tree.getroot()
    except:
        return None

    world = {
        "name": "Mundo Desconocido" if g.lang == "es" else "Unknown World",
        "civilizations": [],
        "heroes": [],
        "artifacts": [],
        "wars": [],
        "historical_events": [],
        "regions": [],
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    
    name_el = root.find(".//name")
    if name_el is not None and name_el.text:
        world["name"] = name_el.text.title()

    for entity in root.findall(".//entity"):
        civ = {
            "name": entity.findtext("name", "Desconocido").title(),
            "race": entity.findtext("race", "Desconocida").title(),
            "type": entity.findtext("type", ""),
        }
        if civ["name"] != "Desconocido":
            world["civilizations"].append(civ)

    for figure in root.findall(".//historical_figure"):
        name = figure.findtext("name", "")
        if not name: continue
        world["heroes"].append({
            "name": name.title(),
            "race": figure.findtext("race", "Desconocida").title(),
            "active": figure.findtext("death_year", "") == "",
            "birth_year": figure.findtext("birth_year", "?"),
            "death_year": figure.findtext("death_year", ""),
        })

    world["heroes"] = world["heroes"][:200]

    for artifact in root.findall(".//artifact"):
        name = artifact.findtext("name", "")
        if not name: continue
        world["artifacts"].append({
            "name": name.title(),
            "item_type": artifact.findtext("item_type", "Objeto").title(),
        })

    for event in root.findall(".//historical_event"):
        world["historical_events"].append({
            "year": event.findtext("year", "?"),
            "type": event.findtext("type", "evento").replace("_", " ").title(),
        })
    world["historical_events"] = world["historical_events"][-100:]

    return world

# ── Routes ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    world = parse_legends()
    return render_template("index.html", world=world)

@app.route("/oracle")
def oracle():
    world = parse_legends()
    return render_template("oracle.html", world=world)

@app.route("/api/oracle", methods=["POST"])
def oracle_api():
    if not client:
        return jsonify({"error": "API Key missing"}), 503
    
    data = request.get_json()
    question = data.get("question", "")
    world = parse_legends()
    
    # Simple summary for AI context
    summary = f"World: {world['name'] if world else 'Unknown'}. Heroes: {len(world['heroes']) if world else 0}."
    
    system_prompt = f"Eres el Cronista Omnisciente de {world['name'] if world else 'este mundo'}. Responde en {g.lang}."
    
    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1000,
            system=system_prompt,
            messages=[{"role": "user", "content": question}]
        )
        return jsonify({"answer": response.content[0].text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
