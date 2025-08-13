# main.py
from flask import Flask, request, render_template_string
import random
from datetime import datetime
from urllib.parse import urlencode

app = Flask(__name__)

# Constants
game_name = "Shallow Sea"
bgg_url = "https://boardgamegeek.com/boardgame/428440/shallow-sea"
version = datetime.now().strftime("%Y%m%d%H%M")

# Languages (shortened for brevity)
LANGUAGES = {
    'CAT': {
        'intro_shallow_sea': 'Selecció automàtica de llosetes',
        'language_label': 'Idioma',
        'mode_expansion': 'Usar expansió Nesting Season',
        'players_prompt': 'Nombre de jugadors',
        'tolerance_label': 'Tolerància de balanç',
        'submit_button': 'Seleccionar llosetes',
        'regenerate_button': 'Tornar a generar',
        'reset_button': 'Reiniciar',
        'selected_tiles_label': 'Llosetes seleccionades per una partida a {n} jugadors',
        'distribution_pieces': 'Distribució per llosetes:',
        'distribution_types': 'Distribució per tipus:',
        'copies': 'còpies',
        'types': 'tipus',
        'coral': 'Corall',
        'fish': 'Peix',
        'both': 'Corall i peix',
        'type_diff': 'Diferència de tipus',
        'piece_diff': 'Diferència de llosetes',
        'changelog': 'Novetats',
        'share_link_copied': 'Enllaç copiat!'
    }
    # ES, EN, KO omitted for brevity
}

# Dummy tile data for demonstration
FULL_TILE_GROUPS = list("A1 A2 A3 A4 A5 A6".split())
BASE_TILE_GROUPS = list("A1 A2 A3 A4".split())
COPIES_PER_PLAYER_COUNT = {1: 2, 2: 2, 3: 3, 4: 4}

def select_balanced(players, tg, tr, tol, seed):
    rnd = random.Random(seed)
    while True:
        types = sorted(rnd.sample(tg, 10))
        copies = COPIES_PER_PLAYER_COUNT[players]
        tiles = types * copies
        dist_types = {tr['coral']: 0, tr['fish']: 0, tr['both']: 0}
        for t in types:
            dist_types[classify_tile(t, tr)] += 1
        if abs(dist_types[tr['coral']] - dist_types[tr['fish']]) <= tol:
            return types, tiles

def classify_tile(tile, tr):
    return tr['both']

def get_initial_language():
    return 'CAT'

TEMPLATE = '''
<!doctype html>
<html lang="{{ lang_code }}">
<head><meta charset="utf-8"><title>{{ game_name }} – Tile Selector v{{ version }}</title></head>
<body>
<div style="display:flex;justify-content:space-between;align-items:center;">
 <h1><a href="{{ bgg_url }}" target="_blank">{{ game_name }}</a> – Tile Selector</h1>
 <span>v{{ version }}</span>
</div>
<p>{{ tr['intro_shallow_sea'] }}</p>
<form method=post>
 <label><input type="checkbox" name="expansion" {% if expansion_checked %}checked{% endif %}> {{ tr['mode_expansion'] }}</label><br><br>
 <label>{{ tr['players_prompt'] }}<input type=number name=players min=1 max=4 value="{{ players }}" required></label><br><br>
 <label>{{ tr['tolerance_label'] }}<input type=number name=tolerance min=0 max=5 value="{{ tolerance }}" required></label><br><br>
 <input type="hidden" name="seed" value="{{ seed or '' }}">
 <button type=submit name="action" value="generate">{{ tr['submit_button'] }}</button>
 {% if types %}<button type=submit name="action" value="regenerate">{{ tr['regenerate_button'] }}</button>{% endif %}
 <button type="button" onclick="location.href='/'">{{ tr['reset_button'] }}</button>
</form>
{% if types %}
<h2>{{ tr['selected_tiles_label'].format(n=players) }}</h2>
<div>
 <div>
  <ul>{% for t in types %}<li>{{ t }} ({{ copies }} {{ tr['copies'] }})</li>{% endfor %}</ul>
 </div>
 <div>
  <h3>{{ tr['distribution_pieces'] }}</h3>
  <ul>{% for k,v in dist_pieces.items() %}<li>{{ k }}: {{ v }} {{ tr['copies'] }}</li>{% endfor %}</ul>
  <h3>{{ tr['distribution_types'] }}</h3>
  <ul>{% for k,v in dist_types.items() %}<li>{{ k }}: {{ v }} {{ tr['types'] }}</li>{% endfor %}</ul>
 </div>
</div>
<p>Seed: <code>{{ seed }}</code> · <a href="{{ share_url }}">Share link</a></p>
<p><em>{{ tr['type_diff'] }}:</em> {{ type_diff }} · <em>{{ tr['piece_diff'] }}:</em> {{ piece_diff }}</p>
{% endif %}
</body>
</html>
'''

@app.route('/', methods=['GET','POST'])
def index():
    lang_code = request.values.get('lang', get_initial_language())
    tr = LANGUAGES.get(lang_code, LANGUAGES['CAT'])
    expansion_checked = (request.args.get('expansion') == '1')
    types = tiles = dist_pieces = dist_types = None
    copies = players = type_diff = piece_diff = 0
    tolerance = int(request.values.get('tolerance', 1))
    seed_param = request.values.get('seed')
    seed = int(seed_param) if (seed_param and seed_param.isdigit()) else None

    if request.method == 'POST':
        action = request.form.get('action', 'generate')
        expansion_checked = request.form.get('expansion') == 'on'
        players = int(request.form['players'])
        tolerance = int(request.form['tolerance'])
        seed_post = request.form.get('seed')
        if seed_post and seed_post.isdigit():
            seed = int(seed_post)
        else:
            if seed is None:
                seed = random.randint(0, 2**31 - 1)
        tg = FULL_TILE_GROUPS if expansion_checked else BASE_TILE_GROUPS
        types, tiles = select_balanced(players, tg, tr, tolerance, seed)
        copies = COPIES_PER_PLAYER_COUNT[players]
        dist_pieces = {tr['coral']: 0, tr['fish']: 0, tr['both']: 0}
        for tile in tiles:
            dist_pieces[classify_tile(tile, tr)] += 1
        dist_types = {tr['coral']: 0, tr['fish']: 0, tr['both']: 0}
        for t in types:
            dist_types[classify_tile(t, tr)] += 1
        type_diff = abs(dist_types[tr['coral']] - dist_types[tr['fish']])
        piece_diff = abs(dist_pieces[tr['coral']] - dist_pieces[tr['fish']])

    share_url = ''
    if seed is not None:
        params = {
            'lang': lang_code,
            'players': players or request.args.get('players', ''),
            'tolerance': tolerance,
            'seed': str(seed),
            'expansion': '1' if expansion_checked else '0'
        }
        share_url = request.base_url + '?' + urlencode(params)

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
        game_name=game_name,
        bgg_url=bgg_url,
        version=version,
        seed=seed,
        share_url=share_url,
        expansion_checked=expansion_checked,
        tolerance=tolerance
    )

if __name__ == '__main__':
    app.run(debug=True)
