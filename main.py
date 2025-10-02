# main.py
from flask import Flask, request, render_template_string
import random
from urllib.parse import urlencode

app = Flask(__name__)

# App constants
GAME_NAME = "Shallow Sea"
BGG_URL = "https://boardgamegeek.com/boardgame/428440/shallow-sea"
# Fixed version string (release date)
VERSION = "2025-10-02a"

# =============================
# i18n: FULL dictionaries (CAT/ES/EN/KO)
# =============================
LANGUAGES = {
    "CAT": {
        "intro_shallow_sea": "Aquest programa realitza la selecció automàtica i balancejada de llosetes per al joc Shallow Sea.",
        "language_label": "Idioma",
        "expansion_label": "Fer servir l'expansió 'Nesting Season'",
        "players_prompt": "Nombre de jugadors (1-4):",
        "tolerance_label": "Tolerància (diferència tipus):",
        "tolerance_mark": "ⓘ",
        "tolerance_explain_title": "Què és la tolerància?",
        "tolerance_explain_body": "La tolerància estableix la diferència màxima permesa entre el nombre de TIPUS de llosetes que necessiten Corall i el nombre de TIPUS que necessiten Peix. El programa fa intents fins que la diferència entre Corall i Peix en NOMBRE DE TIPUS sigui menor o igual que la tolerància pels TIPUS. La distribució per llosetes (peces totals) no està restringida directament, però sol quedar força equilibrada.",
        "submit_button": "Generar selecció",
        "regenerate_button": "Tornar a generar",
        "reset_button": "Reiniciar",
        "selected_tiles_label": "Llosetes seleccionades per a {n} jugadors:",
        "distribution_pieces": "Distribució per llosetes:",
        "distribution_types": "Distribució per tipus:",
        "copies": "còpies",
        "types": "tipus",
        "coral": "Corall",
        "fish": "Peix",
        "both": "Corall i peix",
        "type_diff": "Diferència de tipus",
        "piece_diff": "Diferència per llosetes",
        "changelog": "Registre de canvis",
        "share_link_copied": "Enllaç copiat!"
    },
    "ES": {
        "intro_shallow_sea": "Este programa realiza la selección automática y balanceada de losetas para el juego Shallow Sea.",
        "language_label": "Idioma",
        "expansion_label": "Usar la expansión 'Nesting Season'",
        "players_prompt": "Número de jugadores (1-4):",
        "tolerance_label": "Tolerancia (diferencia tipos):",
        "tolerance_mark": "ⓘ",
        "tolerance_explain_title": "¿Qué es la tolerancia?",
        "tolerance_explain_body": "La tolerancia fija la diferencia máxima permitida entre el número de TIPOS de losetas que requieren Coral y el número de TIPOS que requieren Pez. El programa repite hasta que la diferencia entre Coral y Pez en NÚMERO DE TIPOS sea menor o igual que la tolerancia para TIPOS. La distribución por losetas (piezas totales) no se restringe directamente, aunque suele quedar bastante equilibrada.",
        "submit_button": "Generar selección",
        "regenerate_button": "Volver a generar",
        "reset_button": "Reiniciar",
        "selected_tiles_label": "Losetas seleccionadas para {n} jugadores:",
        "distribution_pieces": "Distribución losetas:",
        "distribution_types": "Distribución por tipos:",
        "copies": "copias",
        "types": "tipos",
        "coral": "Coral",
        "fish": "Pez",
        "both": "Coral y pez",
        "type_diff": "Diferencia de tipos",
        "piece_diff": "Diferencia por losetas",
        "changelog": "Registro de cambios",
        "share_link_copied": "¡Enlace copiado!"
    },
    "EN": {
        "intro_shallow_sea": "This program performs automatic balanced tile selection for Shallow Sea.",
        "language_label": "Language",
        "expansion_label": "Use 'Nesting Season' expansion",
        "players_prompt": "Number of players (1-4):",
        "tolerance_label": "Tolerance (type diff):",
        "tolerance_mark": "ⓘ",
        "tolerance_explain_title": "What is tolerance?",
        "tolerance_explain_body": "Tolerance sets the maximum allowed difference between the number of tile TYPES that require Coral and the number of TYPES that require Fish. The selector retries until the difference between Coral and Fish in NUMBER OF TYPES is less than or equal to the tolerance for TYPES. Piece distribution (total tiles) is not directly constrained, though it usually ends up fairly even.",
        "submit_button": "Generate selection",
        "regenerate_button": "Regenerate",
        "reset_button": "Reset",
        "selected_tiles_label": "Selected tiles for {n} players:",
        "distribution_pieces": "Distribution by pieces:",
        "distribution_types": "Distribution by types:",
        "copies": "copies",
        "types": "types",
        "coral": "Coral",
        "fish": "Fish",
        "both": "Coral and fish",
        "type_diff": "Type diff",
        "piece_diff": "Piece diff",
        "changelog": "Changelog",
        "share_link_copied": "Link copied!"
    },
    "KO": {
        "intro_shallow_sea": "이 프로그램은 Shallow Sea 게임을 위한 자동 균형 타일 선택을 수행합니다.",
        "language_label": "언어",
        "expansion_label": "'Nesting Season' 확장 사용",
        "players_prompt": "플레이어 수 (1-4):",
        "tolerance_label": "허용 편차(유형 차이):",
        "tolerance_mark": "ⓘ",
        "tolerance_explain_title": "허용 편차란?",
        "tolerance_explain_body": "허용 편차는 산호가 필요한 타일 유형 수와 물고기가 필요한 타일 유형 수의 차이에 대한 최대 허용치를 의미합니다. 선택기는 산호와 물고기 유형 수의 차이가 허용 편차보다 작거나 같을 때(유형 기준)가 될 때까지 다시 시도합니다. 총 타일 수(피스) 분포는 직접적으로 제한하지 않지만 보통 비슷하게 맞춰집니다.",
        "submit_button": "선택 생성",
        "regenerate_button": "다시 생성",
        "reset_button": "초기화",
        "selected_tiles_label": "{n}인 게임을 위한 선택된 타일:",
        "distribution_pieces": "타일 수 기준 분포:",
        "distribution_types": "유형 기준 분포:",
        "copies": "개",
        "types": "유형",
        "coral": "산호",
        "fish": "물고기",
        "both": "산호 및 물고기",
        "type_diff": "유형 차이",
        "piece_diff": "타일 수 차이",
        "changelog": "변경 기록",
        "share_link_copied": "링크가 복사되었습니다!"
    }
}

# =============================
# Tile sets
# =============================
# Full game (base + expansion)
FULL_TILE_GROUPS = {
    'A': [f"A{i}" for i in range(1, 6+1)],        # A1–A6
    'B': [f"B{i}" for i in range(1, 8+1)],        # B1–B8
    'C': [f"C{i}" for i in range(1, 8+1)],        # C1–C8
    'D': [f"D{i}" for i in range(1, 6+1)],        # D1–D6
    'E': [f"E{i}" for i in range(1, 10+1)],       # E1–E10
    'F': [f"F{i}" for i in range(1, 4+1)],        # F1–F4
}
# Base game only
BASE_TILE_GROUPS = {
    'A': [f"A{i}" for i in range(1, 4+1)],        # A1–A4
    'B': [f"B{i}" for i in range(1, 4+1)],        # B1–B4
    'C': [f"C{i}" for i in range(1, 4+1)],        # C1–C4
    'D': [f"D{i}" for i in range(1, 4+1)],        # D1–D4
    'E': [f"E{i}" for i in range(1, 4+1)],        # E1–E4
    'F': [f"F{i}" for i in range(1, 2+1)],        # F1–F2
}

# Classification by resource
CORAL_TILES = {"A1","A2","A5","B1","B3","B5","B7","C1","C2","C3","D1","D2","E1","E2","E9","F1","F2"}
FISH_TILES  = {"A3","A4","B2","B4","B6","B8","C4","C5","C6","D3","D4","E3","E4","E10","F3","F4"}

# Copies per player count (2 copies for 1–2p, 3 for 3p, 4 for 4p)
COPIES_PER_PLAYER_COUNT = {1:2, 2:2, 3:3, 4:4}

# =============================
# Helpers
# =============================
def get_initial_language():
    accept = request.headers.get('Accept-Language', '')
    if accept:
        primary = accept.split(',')[0].split('-')[0].lower()
        if primary == 'ca': return 'CAT'
        if primary == 'es': return 'ES'
        if primary == 'ko': return 'KO'
    return 'EN'

def classify_tile(tile, tr):
    if tile in CORAL_TILES: return tr['coral']
    if tile in FISH_TILES:  return tr['fish']
    return tr['both']

def select_10_tile_types(tile_groups, rnd):
    """Pick exactly 10 distinct types with constraints:
    - A,B,D: up to 2 each
    - C,E: up to 3 each
    - F: exactly 1
    Then ensure exactly 10 keeping the F tile.
    """
    picks = []
    # Exactly 1 from F
    f_pick = rnd.choice(tile_groups['F'])
    # Up-to quotas for others
    for g, cap in [('A',2),('B',2),('C',3),('D',2),('E',3)]:
        pool = tile_groups[g]
        take = min(cap, len(pool))
        picks += rnd.sample(pool, take)
    picks.append(f_pick)
    # Downsample to 10 preserving the F tile
    while len(picks) > 10:
        non_f = [t for t in picks if not t.startswith('F')]
        t = rnd.choice(non_f)
        picks.remove(t)
    # Safety top-up if <10 (should be rare)
    while len(picks) < 10:
        for g, cap in [('C',3),('E',3),('A',2),('B',2),('D',2)]:
            avail = [t for t in tile_groups[g] if t not in picks]
            if avail:
                picks.append(rnd.choice(avail))
                break
        if len(picks) >= 10:
            break
    return sorted(picks)

def build_tile_list(types, copies, rnd):
    tiles = []
    for t in types:
        tiles.extend([t]*copies)
    rnd.shuffle(tiles)
    return tiles

def select_balanced(num_players, tile_groups, tr, tol, seed=None, max_tries=5000):
    rnd = random.Random(seed) if seed is not None else random
    copies = COPIES_PER_PLAYER_COUNT[num_players]
    last_types = None
    for _ in range(max_tries):
        types = select_10_tile_types(tile_groups, rnd)
        last_types = types
        counts = {tr['coral']:0, tr['fish']:0, tr['both']:0}
        for t in types:
            counts[classify_tile(t, tr)] += 1
        if abs(counts[tr['coral']] - counts[tr['fish']]) <= tol:
            return types, build_tile_list(types, copies, rnd)
    # Fallback (rare)
    return last_types or [], build_tile_list(last_types or [], copies, rnd)

# =============================
# Template
# =============================
TEMPLATE = '''
<!doctype html>
<html lang="{{ lang_code }}">
<head>
  <meta charset="utf-8">
  <title>{{ game_name }} – Tile Selector v{{ version }}</title>
  <style>
    body{font-family:sans-serif;margin:2rem;background:#001f3f;color:#fff}
    a{color:#ffcc80}
    .topbar{display:flex;justify-content:space-between;align-items:flex-start;gap:1rem}
    .lefthead h1{margin:0;font-size:1.6rem}
    .desc{opacity:.9;margin-top:.25rem}
    .righthead{display:flex;flex-direction:column;align-items:flex-end;gap:.25rem}
    .version{font-size:.9rem;color:#ffcc80}
    .lang-switch{display:flex;gap:.5rem;align-items:center}
    .grid{display:flex;gap:2rem;margin-top:1rem}
    .col{flex:1;background:rgba(255,255,255,.1);padding:1rem;border-radius:8px}
    button{background:#ff7f50;color:#001f3f;border:none;padding:.5rem 1rem;border-radius:4px;cursor:pointer}
    button:hover{opacity:.9}
    input,select{padding:.4rem;border-radius:4px;border:none}
    @media(max-width:700px){.grid{flex-direction:column}}
    /* changelog bubble */
    details.changelog{position:fixed;bottom:16px;right:16px;background:rgba(255,255,255,0.08);padding:.5rem .75rem;border-radius:999px} details.help{position:static}
    details.changelog summary{list-style:none;cursor:pointer}
    details.changelog[open]{border-radius:12px}
    details.changelog .panel{max-height:40vh;overflow:auto;margin-top:.5rem}
  </style>
  <script>
    function switchLang(sel){
      var p=new URLSearchParams(location.search);
      p.set('lang', sel.value);
      location.search=p.toString();
    }
    function resetForm(){ localStorage.clear(); location.href='/?lang={{ lang_code }}'; }
    function copyShare(url){ navigator.clipboard.writeText(url).then(()=>{ alert('{{ tr['share_link_copied'] }}'); }); }
    window.addEventListener('DOMContentLoaded', ()=>{
      const params = new URLSearchParams(location.search);
      const urlExp = params.get('expansion'); // '1' | '0' | null
      const fields = ['expansion','players','tolerance','lang','seed'];
      fields.forEach(name=>{
        const el = document.querySelector(`[name="${name}"]`);
        if(!el) return;
        const saved = localStorage.getItem(name);
        if(saved!=null){
          if(name==='expansion' && urlExp!==null){ /* respect URL state */ }
          else if(el.type==='checkbox') el.checked = (saved==='1');
          else el.value = saved;
        }
        el.addEventListener('change', ()=>{
          localStorage.setItem(name, el.type==='checkbox' ? (el.checked?'1':'0') : el.value);
        });
      });
    });
  </script>
</head>
<body>
  <div class="topbar">
    <div class="lefthead">
      <div>
        <h1><a href="{{ bgg_url }}" target="_blank" rel="noopener">{{ game_name }}</a> – Tile Selector</h1>
        <div class="desc">{{ tr['intro_shallow_sea'] }}</div>
      </div>
    </div>
    <div class="righthead">
      <div class="version">v{{ version }}</div>
      <div class="lang-switch">
        <label>{{ tr['language_label'] }}:</label>
        <select onchange="switchLang(this)" name="lang" value="{{ lang_code }}">
          <option value="CAT" {% if lang_code=='CAT' %}selected{% endif %}>CAT</option>
          <option value="ES"  {% if lang_code=='ES'  %}selected{% endif %}>ESP</option>
          <option value="EN"  {% if lang_code=='EN'  %}selected{% endif %}>ENG</option>
          <option value="KO"  {% if lang_code=='KO'  %}selected{% endif %}>KOR</option>
        </select>
      </div>
    </div>
  </div>

  <form method="post">
    <label><input type="checkbox" name="expansion" {% if expansion_checked %}checked{% endif %}> {{ tr['expansion_label'] }}</label><br><br>
    <label>{{ tr['players_prompt'] }} <input type="number" name="players" min="1" max="4" value="{{ players }}" required></label><br><br>
    <label>{{ tr['tolerance_label'] }} <sup title="{{ tr['tolerance_explain_title'] }}">{{ tr['tolerance_mark'] }}</sup> <input type="number" name="tolerance" min="0" max="5" value="{{ tolerance }}" required></label>
    <input type="hidden" name="seed" value="{{ seed or '' }}">
    <div style="margin-top:12px; display:flex; gap:.5rem; flex-wrap:wrap;">
      <button type="submit" name="action" value="generate">{{ tr['submit_button'] }}</button>
      <button type="button" onclick="resetForm();">{{ tr['reset_button'] }}</button>
    </div>

    <!-- Tolerance help panel shown from the start -->
    <details class="help" open style="margin-top:10px;background:rgba(255,255,255,.08);padding:.75rem 1rem;border-radius:8px;">
      <summary style="cursor:pointer;"><strong>{{ tr['tolerance_explain_title'] }}</strong></summary>
      <div style="margin-top:.5rem;">{{ tr['tolerance_explain_body'] }}</div>
    </details>
  </form>

  {% if types %}
  <h2>{{ tr['selected_tiles_label'].format(n=players) }}</h2>
  <div class="grid">
    <div class="col">
      <ul>
        {% for t in types %}<li>{{ t }} ({{ copies }} {{ tr['copies'] }})</li>{% endfor %}
      </ul>
    </div>
    <div class="col">
      <h3>{{ tr['distribution_pieces'] }}</h3>
      <ul>
        {% for k,v in dist_pieces.items() %}<li>{{ k }}: {{ v }} {{ tr['copies'] }}</li>{% endfor %}
      </ul>
      <h3>{{ tr['distribution_types'] }}</h3>
      <ul>
        {% for k,v in dist_types.items() %}<li>{{ k }}: {{ v }} {{ tr['types'] }}</li>{% endfor %}
      </ul>
    </div>
  </div>
  <p style="margin-top:.5rem; opacity:.9;">Seed: <code>{{ seed }}</code> · <a href="#" onclick="copyShare('{{ share_url }}'); return false;">Copy share link</a></p>
  <p><em>{{ tr['type_diff'] }}:</em> {{ type_diff }} · <em>{{ tr['piece_diff'] }}:</em> {{ piece_diff }}</p>
  {% endif %}

  <details class="changelog">
    <summary>🛈 {{ tr['changelog'] }}</summary>
    <div class="panel">
      <ul>
        <li><strong>2025-10-02</strong>
          <ul>
            <li>Fixed version date; tolerance help; expansion + seed + tolerance in share URL.</li>
            <li>Languages: CAT/ES/EN/KO. BGG title link. Balanced selection with type diff.</li>
          </ul>
        </li>
      </ul>
    </div>
  </details>
</body>
</html>
'''

# =============================
# Routes
# =============================
@app.route('/', methods=['GET','POST'])
def index():
    # Language
    lang_code = request.values.get('lang', get_initial_language())
    tr = LANGUAGES.get(lang_code, LANGUAGES['EN'])

    # Inputs (GET defaults)
    players = int(request.values.get('players', 2))
    tolerance = int(request.values.get('tolerance', 1))
    expansion_checked = (request.values.get('expansion') == '1')
    seed_param = request.values.get('seed')
    seed = int(seed_param) if (seed_param and seed_param.isdigit()) else None

    types = tiles = dist_pieces = dist_types = None
    copies = type_diff = piece_diff = 0

    if request.method == 'POST':
        # Read POST
        players = int(request.form['players'])
        tolerance = int(request.form['tolerance'])
        expansion_checked = (request.form.get('expansion') == 'on')
        seed_post = request.form.get('seed')
        if seed_post and seed_post.isdigit():
            seed = int(seed_post)
        else:
            if seed is None:
                seed = random.randint(0, 2**31 - 1)
        # Choose tile universe
        tile_groups = FULL_TILE_GROUPS if expansion_checked else BASE_TILE_GROUPS
        # Select
        types, tiles = select_balanced(players, tile_groups, tr, tolerance, seed)
        copies = COPIES_PER_PLAYER_COUNT[players]
        # Distributions
        dist_pieces = {tr['coral']:0, tr['fish']:0, tr['both']:0}
        for tile in tiles:
            dist_pieces[classify_tile(tile, tr)] += 1
        dist_types = {tr['coral']:0, tr['fish']:0, tr['both']:0}
        for t in types:
            dist_types[classify_tile(t, tr)] += 1
        type_diff = abs(dist_types[tr['coral']] - dist_types[tr['fish']])
        piece_diff = abs(dist_pieces[tr['coral']] - dist_pieces[tr['fish']])

    # Share URL (only meaningful if seed exists)
    share_url = ''
    if seed is not None:
        params = {
            'lang': lang_code,
            'players': str(players),
            'tolerance': str(tolerance),
            'seed': str(seed),
            'expansion': '1' if expansion_checked else '0'
        }
        share_url = request.base_url + '?' + urlencode(params)

    return render_template_string(
        TEMPLATE,
        tr=tr,
        lang_code=lang_code,
        game_name=GAME_NAME,
        bgg_url=BGG_URL,
        version=VERSION,
        players=players,
        tolerance=tolerance,
        expansion_checked=expansion_checked,
        seed=seed,
        types=types,
        tiles=tiles,
        copies=copies,
        dist_pieces=dist_pieces,
        dist_types=dist_types,
        type_diff=type_diff,
        piece_diff=piece_diff,
        share_url=share_url,
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
