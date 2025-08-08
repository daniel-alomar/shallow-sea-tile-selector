# Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)
# Author: Daniel Alomar
# Web application for balanced tile selection for Shallow Sea.

from flask import Flask, request, render_template_string
import random
from datetime import datetime

app = Flask(__name__)

# Application version based on current timestamp
VERSION = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Multilanguage strings (CAT/ES/EN)
LANGUAGES = {
    "CAT": {
        "intro_shallow_sea": "Aquest programa realitza la selecció automàtica i balancejada de llosetes per al joc Shallow Sea.",
        "mode_prompt": "Tipus de joc:",
        "players_prompt": "Nombre de jugadors (1-4):",
        "tolerance_label": "Tolerància (diferència tipus):",
        "selected_tiles_label": "Llosetes seleccionades per a {n} jugadors:",
        "copies": "còpies",
        "coral": "Corall",
        "fish": "Peix",
        "both": "Corall i peix",
        "distribution_pieces": "Distribució peces:",
        "distribution_types": "Distribució tipus:",
        "types": "tipus",
        "submit_button": "Generar selecció",
        "language_label": "Idioma"
    },
    "ES": {
        "intro_shallow_sea": "Este programa realiza la selección automática y balanceada de losetas para el juego Shallow Sea.",
        "mode_prompt": "Tipo de juego:",
        "players_prompt": "Número de jugadores (1-4):",
        "tolerance_label": "Tolerancia (diferencia tipos):",
        "selected_tiles_label": "Losetas seleccionadas para {n} jugadores:",
        "copies": "copias",
        "coral": "Coral",
        "fish": "Pez",
        "both": "Coral y pez",
        "distribution_pieces": "Distribución (losetas):",
        "distribution_types": "Distribución (tipos):",
        "types": "tipos",
        "submit_button": "Generar selección",
        "language_label": "Idioma"
    },
    "EN": {
        "intro_shallow_sea": "This program performs automatic balanced tile selection for Shallow Sea.",
        "mode_prompt": "Game mode:",
        "players_prompt": "Number of players (1-4):",
        "tolerance_label": "Tolerance (type diff):",
        "selected_tiles_label": "Selected tiles for {n} players:",
        "copies": "copies",
        "coral": "Coral",
        "fish": "Fish",
        "both": "Coral and fish",
        "distribution_pieces": "Distribution (pieces):",
        "distribution_types": "Distribution (types):",
        "types": "types",
        "submit_button": "Generate selection",
        "language_label": "Language"
    }
}

# Tile groups
BASE_TILE_GROUPS = {g: [f"{g}{i}" for i in range(1, max + 1)] for g, max in zip(["A","B","C","D","E","F"],[4,4,4,4,4,2])}
FULL_TILE_GROUPS = {g: [f"{g}{i}" for i in range(1, max + 1)] for g, max in zip(["A","B","C","D","E","F"],[6,8,8,6,10,4])}

# Coral-only and fish-only
CORAL_TILES = {"A1","A2","A5","B1","B3","B5","B7","C1","C2","C3","D1","D2","E1","E2","E9","F1","F2"}
FISH_TILES = {"A3","A4","B2","B4","B6","B8","C4","C5","C6","D3","D4","E3","E4","E10","F3","F4"}

# Number of copies per player
COPIES_PER_PLAYER_COUNT = {1: 2, 2: 2, 3: 3, 4: 4}

# Determine initial language from browser

def get_initial_language():
    accept = request.headers.get('Accept-Language', '')
    if accept:
        primary = accept.split(',')[0].split('-')[0].lower()
        if primary == 'ca': return 'CAT'
        if primary == 'es': return 'ES'
    return 'EN'

# Classify tile to category

def classify_tile(tile, tr):
    if tile in CORAL_TILES: return tr['coral']
    if tile in FISH_TILES: return tr['fish']
    return tr['both']

# Select 10 distinct tile types respecting group limits

def select_10_tile_types(tile_groups):
    sel=[]
    pick=lambda grp,n: random.sample(tile_groups[grp],n)
    sel+=pick('A',2)+pick('B',2)+pick('C',3)
    sel+=pick('D',2)+pick('E',3)+pick('F',1)
    f=next(t for t in sel if t.startswith('F'))
    others=[t for t in sel if t!=f]
    return random.sample(others,9)+[f]

# Build full tile list with copies and shuffle

def build_tile_list(types, copies):
    lst=[]
    for t in types: lst.extend([t]*copies)
    random.shuffle(lst)
    return lst

# Repeat until type balance within tolerance

def select_balanced(num_players, tile_groups, tr, tol):
    copies=COPIES_PER_PLAYER_COUNT[num_players]
    while True:
        types=select_10_tile_types(tile_groups)
        counts={tr['coral']:0, tr['fish']:0, tr['both']:0}
        for t in types: counts[classify_tile(t,tr)]+=1
        if abs(counts[tr['coral']]-counts[tr['fish']])<=tol:
            return sorted(types), build_tile_list(types,copies)

# HTML template with version, persisted inputs via localStorage
TEMPLATE='''
<!doctype html>
<html lang="{{ lang_code }}">
<head><meta charset="utf-8"><title>Shallow Sea Tile Selector v{{ version }}</title>
<style>
 body{font-family:sans-serif;margin:2rem;background-color:#001f3f;color:#fff}
 .lang-switch{position:absolute;top:10px;right:10px}
 .version{position:absolute;top:10px;left:10px;font-size:0.9rem;color:#ff7f50}
 .grid{display:flex;gap:2rem;margin-top:1rem}
 .col{flex:1;background:rgba(255,255,255,0.1);padding:1rem;border-radius:8px}
 button{background:#ff7f50;color:#001f3f;border:none;padding:0.5rem 1rem;border-radius:4px;cursor:pointer}
 button:hover{opacity:0.9}
 input,select{padding:0.4rem;border-radius:4px;border:none}
</style>
<script>
function switchLang(sel){var p=new URLSearchParams(location.search);p.set('lang',sel.value);location.search=p}
window.addEventListener('DOMContentLoaded',()=>{['mode','players','tolerance','lang'].forEach(field=>{let e=document.querySelector(`[name="${field}"]`);if(e){let v=localStorage.getItem(field);if(v!=null) e.value=v; e.addEventListener('change',()=>localStorage.setItem(field,e.value));}});});
</script>
</head>
<body>
<div class="version">v{{ version }}</div>
<div class="lang-switch">
  <label>{{ tr['language_label'] }}:</label>
  <select onchange="switchLang(this)" value="{{ lang_code }}">
    <option value="CAT" {% if lang_code=='CAT' %}selected{% endif %}>CAT</option>
    <option value="ES" {% if lang_code=='ES' %}selected{% endif %}>ESP</option>
    <option value="EN" {% if lang_code=='EN' %}selected{% endif %}>ENG</option>
  </select>
</div>
<h1>{{ tr['intro_shallow_sea'] }}</h1>
<form method=post>
 <label>{{ tr['mode_prompt'] }}<select name=mode><option value="1">Base</option><option value="2">Base+Expansion</option></select></label><br><br>
 <label>{{ tr['players_prompt'] }}<input type=number name=players min=1 max=4 required></label><br><br>
 <label>{{ tr['tolerance_label'] }}<input type=number name=tolerance min=0 max=5 value=1 required></label><br><br>
 <button type=submit>{{ tr['submit_button'] }}</button>
</form>
{% if types %}
<h2>{{ tr['selected_tiles_label'].format(n=players) }}</h2>
<div class="grid">
 <div class="col">
  <ul>{% for t in types %}<li>{{ t }} ({{ copies }} {{ tr['copies'] }})</li>{% endfor %}</ul>
 </div>
 <div class="col">
  <h3>{{ tr['distribution_pieces'] }}</h3>
  <ul>{% for k,v in dist_pieces.items() %}<li>{{ k }}: {{ v }} {{ tr['copies'] }}</li>{% endfor %}</ul>
  <h3>{{ tr['distribution_types'] }}</h3>
  <ul>{% for k,v in dist_types.items() %}<li>{{ k }}: {{ v }} {{ tr['types'] }}</li>{% endfor %}</ul>
 </div>
</div>
{% endif %}
</body>
</html>
'''
@app.route('/',methods=['GET','POST'])
def index():
    # initial language or override
    lang_code = request.values.get('lang', get_initial_language())
    tr = LANGUAGES.get(lang_code, LANGUAGES['EN'])
    types=tiles=dist_pieces=dist_types=None
    copies=players=0
    if request.method=='POST':
        mode,players, tol = request.form['mode'], int(request.form['players']), int(request.form['tolerance'])
        tg = FULL_TILE_GROUPS if mode=='2' else BASE_TILE_GROUPS
        types, tiles = select_balanced(players, tg, tr, tol)
        copies = COPIES_PER_PLAYER_COUNT[players]
        dist_pieces={tr['coral']:0,tr['fish']:0,tr['both']:0}
        for tile in tiles: dist_pieces[classify_tile(tile,tr)]+=1
        dist_types={tr['coral']:0,tr['fish']:0,tr['both']:0}
        for t in types: dist_types[classify_tile(t,tr)]+=1
    return render_template_string(TEMPLATE, tr=tr, lang_code=lang_code, types=types, players=players, copies=copies, dist_pieces=dist_pieces, dist_types=dist_types, version=VERSION)

if __name__=='__main__':
    app.run(debug=True,host='0.0.0.0')
