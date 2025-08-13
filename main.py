# Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)
# Author: Daniel Alomar
# Web application for balanced tile selection for Shallow Sea.

from flask import Flask, request, render_template_string
import random
from datetime import datetime

app = Flask(__name__)

# Application version based on current timestamp
VERSION = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
BGG_URL = "https://boardgamegeek.com/boardgame/"  # Replace with exact game URL if known
GAME_NAME = "Shallow Sea"

# Multilanguage strings (CAT/ES/EN/KO)
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
        "distribution_pieces": "Distribució per llosetes:",
        "distribution_types": "Distribució per tipus:",
        "types": "tipus",
        "submit_button": "Generar selecció",
        "regenerate_button": "Tornar a generar",
        "reset_button": "Reiniciar",
        "language_label": "Idioma",
        "mode_base": "Base",
        "mode_full": "Base+Expansió",
        "type_diff": "Diferència de tipus",
        "piece_diff": "Diferència per llosetes",
        "bgg_link": f"{GAME_NAME} a la BGG",
        "changelog": "Registre de canvis"
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
        "distribution_pieces": "Distribución losetas:",
        "distribution_types": "Distribución por tipos:",
        "types": "tipos",
        "submit_button": "Generar selección",
        "regenerate_button": "Volver a generar",
        "reset_button": "Reiniciar",
        "language_label": "Idioma",
        "mode_base": "Base",
        "mode_full": "Base+Expansión",
        "type_diff": "Diferencia de tipos",
        "piece_diff": "Diferencia por losetas",
        "bgg_link": f"{GAME_NAME} en BGG",
        "changelog": "Registro de cambios"
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
        "distribution_pieces": "Distribution by pieces:",
        "distribution_types": "Distribution by types:",
        "types": "types",
        "submit_button": "Generate selection",
        "regenerate_button": "Regenerate",
        "reset_button": "Reset",
        "language_label": "Language",
        "mode_base": "Base",
        "mode_full": "Base+Expansion",
        "type_diff": "Type diff",
        "piece_diff": "Piece diff",
        "bgg_link": f"{GAME_NAME} on BGG",
        "changelog": "Changelog"
    },
    "KO": {
        "intro_shallow_sea": "이 프로그램은 Shallow Sea 게임을 위한 자동 균형 타일 선택을 수행합니다.",
        "mode_prompt": "게임 모드:",
        "players_prompt": "플레이어 수 (1-4):",
        "tolerance_label": "허용 편차(타입 차이):",
        "selected_tiles_label": "{n}인 게임을 위한 선택된 타일:",
        "copies": "개",
        "coral": "산호",
        "fish": "물고기",
        "both": "산호 및 물고기",
        "distribution_pieces": "타일 수 기준 분포:",
        "distribution_types": "유형 기준 분포:",
        "types": "유형",
        "submit_button": "선택 생성",
        "regenerate_button": "다시 생성",
        "reset_button": "초기화",
        "language_label": "언어",
        "mode_base": "기본",
        "mode_full": "기본+확장",
        "type_diff": "유형 차이",
        "piece_diff": "타일 수 차이",
        "bgg_link": f"BGG의 {GAME_NAME}",
        "changelog": "변경 기록"
    }
}

# Simple changelog entries (English-only notes for now)
CHANGELOG = [
    ("2025-08-13", [
        "Added KO language.",
        "Regenerate button to roll a new set with the same parameters.",
        "Localized Base / Base+Expansion options.",
        "Show type and piece balance diffs.",
        "BGG link near the title.",
    ]),
]

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
        if primary == 'ko': return 'KO'
    return 'EN'

# Classify tile to category

def classify_tile(tile, tr):
    if tile in CORAL_TILES: return tr['coral']
    if tile in FISH_TILES: return tr['fish']
    return tr['both']

# Select 10 distinct tile types respecting group limits

def select_10_tile_types(tile_groups, rnd):
    sel=[]
    pick=lambda grp,n: rnd.sample(tile_groups[grp],n)
    sel+=pick('A',2)+pick('B',2)+pick('C',3)
    sel+=pick('D',2)+pick('E',3)+pick('F',1)
    f=next(t for t in sel if t.startswith('F'))
    others=[t for t in sel if t!=f]
    return rnd.sample(others,9)+[f]

# Build full tile list with copies and shuffle

def build_tile_list(types, copies):
    lst=[]
    for t in types: lst.extend([t]*copies)
    random.shuffle(lst)
    return lst

# Repeat until type balance within tolerance

def select_balanced(num_players, tile_groups, tr, tol, seed=None, max_tries=5000):
    rnd = random.Random(seed) if seed is not None else random
    copies=COPIES_PER_PLAYER_COUNT[num_players]
    for _ in range(max_tries):
        types=select_10_tile_types(tile_groups, rnd)
        counts={tr['coral']:0,tr['fish']:0,tr['both']:0}
        for t in types: counts[classify_tile(t,tr)]+=1
        if abs(counts[tr['coral']] - counts[tr['fish']]) <= tol:
            return sorted(types), build_tile_list(types, copies)
    # Fallback (should rarely happen): return last attempt
    return sorted(types), build_tile_list(types, copies)

# HTML template updated with BGG link, regenerate, localized options, diffs, and changelog
TEMPLATE='''
<!doctype html>
<html lang="{{ lang_code }}">
<head><meta charset="utf-8"><title>{{ game_name }} – Tile Selector v{{ version }}</title>
<style>
 body{font-family:sans-serif;margin:2rem;background-color:#001f3f;color:#fff}
 .topbar{display:flex;justify-content:space-between;align-items:center}
 .lang-switch{display:flex;gap:.5rem;align-items:center}
 .version{font-size:0.9rem;color:#ff7f50}
 .grid{display:flex;gap:2rem;margin-top:1rem}
 .col{flex:1;background:rgba(255,255,255,0.1);padding:1rem;border-radius:8px}
 button{background:#ff7f50;color:#001f3f;border:none;padding:0.5rem 1rem;border-radius:4px;cursor:pointer}
 button:hover{opacity:0.9}
 input,select{padding:0.4rem;border-radius:4px;border:none}
 a{color:#ffcc80}
 @media(max-width:700px){.grid{flex-direction:column}}
</style>
<script>
function switchLang(sel){var p=new URLSearchParams(location.search);p.set('lang',sel.value);location.search=p}
window.addEventListener('DOMContentLoaded',()=>{
  const remember=true; // always remember basic prefs
  ['mode','players','tolerance','lang'].forEach(field=>{
    let e=document.querySelector(`[name="${field}"]`);
    if(e){let v=localStorage.getItem(field);if(v!=null) e.value=v; e.addEventListener('change',()=>localStorage.setItem(field,e.value));}
  });
});
function resetForm(){localStorage.clear();location.reload();}
</script>
</head>
<body>
<div class="topbar">
  <div>
    <div class="version">v{{ version }}</div>
    <h1>{{ game_name }} – Tile Selector</h1>
    <div><a href="{{ bgg_url }}" target="_blank" rel="noopener">{{ tr['bgg_link'] }}</a></div>
  </div>
  <div class="lang-switch">
    <label>{{ tr['language_label'] }}:</label>
    <select onchange="switchLang(this)" name="lang" value="{{ lang_code }}">
      <option value="CAT" {% if lang_code=='CAT' %}selected{% endif %}>CAT</option>
      <option value="ES" {% if lang_code=='ES' %}selected{% endif %}>ESP</option>
      <option value="EN" {% if lang_code=='EN' %}selected{% endif %}>ENG</option>
      <option value="KO" {% if lang_code=='KO' %}selected{% endif %}>KOR</option>
    </select>
  </div>
</div>
<p>{{ tr['intro_shallow_sea'] }}</p>
<form method=post>
 <label>{{ tr['mode_prompt'] }}
   <select name=mode>
     <option value="1">{{ tr['mode_base'] }}</option>
     <option value="2">{{ tr['mode_full'] }}</option>
   </select>
 </label><br><br>
 <label>{{ tr['players_prompt'] }}<input type=number name=players min=1 max=4 required></label><br><br>
 <label>{{ tr['tolerance_label'] }}<input type=number name=tolerance min=0 max=5 value=1 required></label><br><br>
 <button type=submit name="action" value="generate">{{ tr['submit_button'] }}</button>
 <button type=submit name="action" value="regenerate">🔁 {{ tr['regenerate_button'] }}</button>
 <button type="button" onclick="resetForm();">{{ tr['reset_button'] }}</button>
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
  <p><em>{{ tr['type_diff'] }}:</em> {{ type_diff }} · <em>{{ tr['piece_diff'] }}:</em> {{ piece_diff }}</p>
  <ul>{% for k,v in dist_types.items() %}<li>{{ k }}: {{ v }} {{ tr['types'] }}</li>{% endfor %}</ul>
 </div>
</div>
{% endif %}

<h3>{{ tr['changelog'] }}</h3>
<ul>
{% for date, notes in changelog %}
  <li><strong>{{ date }}</strong>
    <ul>
    {% for n in notes %}<li>{{ n }}</li>{% endfor %}
    </ul>
  </li>
{% endfor %}
</ul>

</body>
</html>
'''

@app.route('/',methods=['GET','POST'])
def index():
    lang_code=request.values.get('lang',get_initial_language())
    tr=LANGUAGES.get(lang_code,LANGUAGES['EN'])
    types=tiles=dist_pieces=dist_types=None
    copies=players=type_diff=piece_diff=0

    if request.method=='POST':
        action = request.form.get('action','generate')
        mode = request.form['mode']
        players = int(request.form['players'])
        tol = int(request.form['tolerance'])
        tg = FULL_TILE_GROUPS if mode=='2' else BASE_TILE_GROUPS
        # Optional seed (could be extended later)
        seed = None
        types,tiles=select_balanced(players,tg,tr,tol,seed)
        copies=COPIES_PER_PLAYER_COUNT[players]
        dist_pieces={tr['coral']:0,tr['fish']:0,tr['both']:0}
        for tile in tiles: dist_pieces[classify_tile(tile,tr)]+=1
        dist_types={tr['coral']:0,tr['fish']:0,tr['both']:0}
        for t in types: dist_types[classify_tile(t,tr)]+=1
        type_diff = abs(dist_types[tr['coral']] - dist_types[tr['fish']])
        piece_diff = abs(dist_pieces[tr['coral']] - dist_pieces[tr['fish']])

    return render_template_string(
        TEMPLATE,
        tr=tr,
        lang_code=lang_code,
        types=types,
        players=players,
        copies=copies,
        dist_pieces=dist_pieces,
        dist_types=dist_types,
        type_diff=type_diff,
        piece_diff=piece_diff,
        game_name=GAME_NAME,
        bgg_url=BGG_URL,
        changelog=CHANGELOG,
        version=VERSION
    )

if __name__=='__main__':
    app.run(debug=True,host='0.0.0.0')
