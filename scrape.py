import json
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

def iegut_rimi():
    import rimi
    return rimi.aprekinat_vertibas(rimi.visi_produkti)

def iegut_barboru():
    import barbora
    return barbora.aprekinat_vertibas(barbora.visi_produkti)

with ThreadPoolExecutor(max_workers=2) as executor:
    rimi_future    = executor.submit(iegut_rimi)
    barbora_future = executor.submit(iegut_barboru)
    visi = rimi_future.result() + barbora_future.result()

laiks = datetime.now().strftime("%d.%m.%Y %H:%M")

labakais = sorted(
    [v for v in visi if v['vertiba'] > 0],
    key=lambda x: x['vertiba'],
    reverse=True
)

RIMI_LOGO   = 'https://upload.wikimedia.org/wikipedia/lv/thumb/c/c7/Rimi_Baltic_Logo.svg/1280px-Rimi_Baltic_Logo.svg.png'
MAXIMA_LOGO = 'https://www.maxima.lv/images/front/logos/maxima.svg'

KATEGORIJAS = [
    (['kokteilis', 'cocktail', 'spritz', 'lode ', 'shake club'],                                                        '#c03060'),
    (['sarkanv', 'merlot', 'cabernet', 'shiraz', 'malbec', 'chianti', 'rioja', 'pinot noir', 'tempranillo', 'sangiovese'], '#7a1520'),
    (['rozē', 'rose', 'rosé', 'rožu', 'blush'],                                                                           '#c96080'),
    (['baltv', 'chardonnay', 'riesling', 'sauvignon', 'pinot gris', 'moscato', 'viognier'],                               '#a08010'),
    (['šampanietis', 'champagne', 'prosecco', 'cava', 'cremant', 'dzirkst', 'frizzante', 'sekt'],                        '#c8a020'),
    (['degvīns', 'vodka', 'absolut', 'finlandia', 'smirnoff', 'nemiroff'],                                                '#3050c0'),
    (['viskijs', 'whisky', 'whiskey', 'bourbon', 'scotch', 'jameson', 'jack daniel', 'glenfiddich', 'tullamore'],         '#a04808'),
    (['rums', 'bacardi', 'captain morgan', 'havana', 'kraken', 'stroh'],                                                  '#6a2818'),
    (['džins', ' gin ', 'beefeater', 'tanqueray', 'hendricks', 'bombay'],                                                '#1a6840'),
    (['konjaks', 'cognac', 'hennessy', 'martell', 'remy martin'],                                                        '#8b4800'),
    (['brendijs', 'brandy', 'armanjaks', 'calvados', 'torres', 'ararat'],                                                '#7a3c00'),
    (['tequila', 'tekila', 'mezcal'],                                                                                    '#d4a020'),
    (['liķieris', 'jagermeister', 'baileys', 'aperol', 'campari', 'vana tallinn', 'becherovka', 'limoncello'],           '#6020a0'),
    (['absints', 'absinthe'],                                                                                            '#106830'),
    (['sidrs', 'cider', 'somersby', 'westons'],                                                                         '#507818'),
    (['alus', 'lager', 'pilsner', 'porter', 'stout', ' ale', ' ipa', 'weiss', 'heineken', 'carlsberg', 'aldaris', 'cēsu', 'užavas', 'valmiermuižas'], '#b06810'),
    (['vīna dzēriens', 'sangria'],                                                                                      '#902040'),
]

def krasa_no_nosaukuma(nosaukums, alkohols):
    n = nosaukums.lower()
    for atslēgvārdi, krasa in KATEGORIJAS:
        if any(v in n for v in atslēgvārdi):
            return krasa
    if alkohols >= 35: return '#404080'
    if alkohols >= 15: return '#804020'
    if alkohols >= 8:  return '#806020'
    if alkohols >= 4:  return '#b06810'
    return '#606060'

produkti = []
for i, p in enumerate(labakais, 1):
    veikals_att   = 'Maxima' if p['veikals'] == 'Barbora' else p['veikals']
    logo          = RIMI_LOGO if p['veikals'] == 'Rimi' else MAXIMA_LOGO
    veikals_krasa = '#e3000b' if p['veikals'] == 'Rimi' else '#004FE0'
    krasa         = krasa_no_nosaukuma(p['nosaukums'], p['alkohols'])
    produkti.append({
        'vieta':         i,
        'nosaukums':     p['nosaukums'],
        'cena':          p['cena'],
        'vertiba':       p['vertiba'],
        'saite':         p['saite'],
        'bilde':         p['bilde'],
        'logo':          logo,
        'krasa':         krasa,
        'veikals_krasa': veikals_krasa,
        'veikals':       veikals_att,
        'alkohols':      p['alkohols'],
        'tilpums':       p['tilpums']
    })

dati = {'laiks': laiks, 'produkti': produkti}

with open('dati.json', 'w', encoding='utf-8') as f:
    json.dump(dati, f, ensure_ascii=False)

print(f"Saglabāti {len(produkti)} produkti → dati.json")

# Augšupielādē uz PythonAnywhere
API_TOKEN = '8bb1098e36e19fb4e3aa4877e81fcafc0e286a81'  # nomainiet!
USERNAME  = 'salsskabe'

r = requests.post(
    f'https://www.pythonanywhere.com/api/v0/user/{USERNAME}/files/path/home/{USERNAME}/mysite/dati.json',
    files={'content': open('dati.json', 'rb')},
    headers={'Authorization': f'Token {API_TOKEN}'}
)

if r.status_code in (200, 201):
    print("✓ dati.json augšupielādēts uz PythonAnywhere")
else:
    print(f"✗ Kļūda: {r.status_code} {r.text}")