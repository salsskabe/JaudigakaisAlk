import webbrowser
import os
import json
from datetime import datetime
## importe musu rimi.py
def iegut_rimi():
    import rimi
    return rimi.aprekinat_vertibas(rimi.visi_produkti)
## importe musu barbora.py
def iegut_barboru():
    import barbora
    return barbora.aprekinat_vertibas(barbora.visi_produkti)

rimi_dati    = iegut_rimi()
barbora_dati = iegut_barboru()

visi = rimi_dati + barbora_dati
# laiks priekš mājaslapas, lai lietotājs redzetu vai dati ir nesen atjaunoti
laiks = datetime.now().strftime("%d.%m.%Y %H:%M")
# kārtošana pēc vērtībām
labakais = sorted(
    [v for v in visi if v['vertiba'] > 0],
    key=lambda x: x['vertiba'],
    reverse=True
)

RIMI_LOGO   = 'https://upload.wikimedia.org/wikipedia/lv/thumb/c/c7/Rimi_Baltic_Logo.svg/1280px-Rimi_Baltic_Logo.svg.png'
MAXIMA_LOGO = 'https://www.maxima.lv/images/front/logos/maxima.svg'
#pec ka mainisies krasa majaslapam  kad hovero mouse
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
# sagatavo produktu sarakstu html failam
produkti_js = []
for i, p in enumerate(labakais, 1):
    veikals_att   = 'Maxima' if p['veikals'] == 'Barbora' else p['veikals']
#kastītes krāsa
    if p['veikals'] == 'Rimi':
        logo          = RIMI_LOGO
        veikals_krasa = '#e3000b'
    else:
        logo          = MAXIMA_LOGO
        veikals_krasa = '#004FE0'
#kastītes krāsa
    krasa         = krasa_no_nosaukuma(p['nosaukums'], p['alkohols'])
    produkti_js.append({
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
#filtram
max_cena     = max((p['cena']     for p in produkti_js), default=100)
min_cena     = min((p['cena']     for p in produkti_js), default=0)
max_alkohols = max((p['alkohols'] for p in produkti_js if p['alkohols'] > 0), default=96)
min_alkohols = min((p['alkohols'] for p in produkti_js if p['alkohols'] > 0), default=0)
max_tilpums  = max((p['tilpums']  for p in produkti_js if p['tilpums']  > 0), default=3)
min_tilpums  = min((p['tilpums']  for p in produkti_js if p['tilpums']  > 0), default=0)
# pārvērš par json lai varētu ielikt html failā kā javascript mainīgo
produkti_json = json.dumps(produkti_js, ensure_ascii=False)

html = f'''<!DOCTYPE html>
<html lang="lv">
<head>
    <meta charset="UTF-8">
    <title>Labākās alkohola vērtības</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@400;500&display=swap');

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html {{ scroll-behavior: smooth; }}

        body {{
            background: #f5f5f0;
            color: #111;
            font-family: 'DM Sans', sans-serif;
            min-height: 100vh;
            padding: 40px 20px 80px;
            transition: background 0.8s cubic-bezier(0.4,0,0.2,1);
        }}

        h1 {{
            font-family: 'Syne', sans-serif;
            font-size: clamp(2rem, 5vw, 3.5rem);
            font-weight: 800;
            text-align: center;
            margin-bottom: 8px;
            background: linear-gradient(90deg, #111 0%, #555 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -1px;
            animation: fadeDown 0.7s cubic-bezier(0.34,1.56,0.64,1) both;
        }}

        .apakšvirsraksts {{
            text-align: center;
            color: #999;
            font-size: 0.95rem;
            margin-bottom: 8px;
            letter-spacing: 2px;
            text-transform: uppercase;
            animation: fadeDown 0.7s 0.1s cubic-bezier(0.34,1.56,0.64,1) both;
        }}

        .atjaunots {{
            text-align: center;
            color: #ccc;
            font-size: 0.78rem;
            margin-bottom: 6px;
            letter-spacing: 1px;
            animation: fadeDown 0.7s 0.15s cubic-bezier(0.34,1.56,0.64,1) both;
        }}

        /* Social links */
        .social-saites {{
            display: flex;
            justify-content: center;
            gap: 14px;
            margin-bottom: 24px;
            animation: fadeDown 0.7s 0.18s cubic-bezier(0.34,1.56,0.64,1) both;
        }}

        .social-saite {{
            display: flex;
            align-items: center;
            gap: 6px;
            text-decoration: none;
            color: #aaa;
            font-size: 0.75rem;
            font-weight: 500;
            letter-spacing: 0.5px;
            padding: 5px 12px;
            border: 1px solid #ddd;
            border-radius: 20px;
            background: #fff;
            transition: color 0.2s, border-color 0.2s, transform 0.15s, box-shadow 0.2s;
        }}

        .social-saite:hover {{
            transform: translateY(-1px);
            box-shadow: 0 3px 10px rgba(0,0,0,0.08);
        }}

        .social-saite.instagram:hover {{
            color: #c13584;
            border-color: #c13584;
        }}

        .social-saite.soundcloud:hover {{
            color: #ff5500;
            border-color: #ff5500;
        }}

        .social-ikona {{
            width: 14px;
            height: 14px;
            flex-shrink: 0;
        }}

        .josla-sticky {{
            position: sticky;
            top: 0;
            z-index: 200;
            background: #f5f5f0;
            padding: 12px 0;
            transition: background 0.8s cubic-bezier(0.4,0,0.2,1), box-shadow 0.3s ease;
        }}

        .josla-sticky.ritina {{
            box-shadow: 0 2px 16px rgba(0,0,0,0.07);
        }}

        .augsa-josla {{
            display: flex;
            gap: 12px;
            max-width: 1400px;
            margin: 0 auto;
            flex-wrap: wrap;
            align-items: center;
            animation: fadeDown 0.7s 0.2s cubic-bezier(0.34,1.56,0.64,1) both;
        }}

        .augsa-josla input[type=text] {{
            flex: 1;
            min-width: 200px;
            padding: 10px 16px;
            border: 1px solid #ddd;
            border-radius: 10px;
            font-family: 'DM Sans', sans-serif;
            font-size: 0.95rem;
            background: #fff;
            outline: none;
            transition: border-color 0.2s, box-shadow 0.2s;
        }}

        .augsa-josla input[type=text]:focus {{
            border-color: #aaa;
            box-shadow: 0 0 0 3px rgba(0,0,0,0.05);
        }}

        .filtru-wrapper {{ position: relative; z-index: 200; }}

        .filtri-poga {{
            padding: 10px 16px;
            border: 1px solid #ddd;
            border-radius: 10px;
            font-family: 'DM Sans', sans-serif;
            font-size: 0.95rem;
            background: #fff;
            cursor: pointer;
            user-select: none;
            transition: border-color 0.2s, background 0.2s, color 0.2s, transform 0.15s;
            display: flex;
            align-items: center;
            gap: 8px;
            white-space: nowrap;
        }}

        .filtri-poga:hover {{ border-color: #aaa; transform: translateY(-1px); }}
        .filtri-poga:active {{ transform: translateY(0); }}
        .filtri-poga.aktīvs {{ border-color: #111; background: #111; color: #fff; }}

        .filtri-poga .bulta {{
            font-size: 0.7rem;
            transition: transform 0.35s cubic-bezier(0.34,1.56,0.64,1);
        }}

        .filtri-poga.aktīvs .bulta {{ transform: rotate(180deg); }}

        .filtri-badge {{
            display: none;
            background: #e3000b;
            color: #fff;
            font-size: 0.65rem;
            font-weight: 700;
            width: 18px;
            height: 18px;
            border-radius: 50%;
            align-items: center;
            justify-content: center;
        }}

        .filtri-badge.redzams {{ display: flex; }}
        .filtri-poga.aktīvs .filtri-badge {{ background: #fff; color: #111; }}

        .filtru-dropdown {{
            position: absolute;
            top: calc(100% + 8px);
            right: 0;
            width: 380px;
            background: #fff;
            border: 1px solid #e0e0e0;
            border-radius: 16px;
            overflow: hidden;
            max-height: 0;
            opacity: 0;
            z-index: 999;
            transition: max-height 0.45s cubic-bezier(0.4,0,0.2,1), opacity 0.3s ease;
            box-shadow: 0 8px 32px rgba(0,0,0,0.12);
        }}

        .filtru-dropdown.redzams {{ max-height: 900px; opacity: 1; }}

        .filtru-sekcija {{
            padding: 20px 24px;
            border-bottom: 1px solid #f0f0f0;
        }}

        .filtru-sekcija:last-child {{ border-bottom: none; }}

        .filtru-reset {{
            display: flex;
            justify-content: flex-end;
            padding: 12px 24px 0;
        }}

        .filtru-reset-poga {{
            font-size: 0.75rem;
            color: #aaa;
            cursor: pointer;
            border: none;
            background: none;
            font-family: 'DM Sans', sans-serif;
            transition: color 0.2s;
            padding: 0;
        }}

        .filtru-reset-poga:hover {{ color: #e3000b; }}

        .filtru-virsraksts {{
            font-family: 'Syne', sans-serif;
            font-weight: 700;
            font-size: 0.9rem;
            margin-bottom: 4px;
        }}

        .filtru-apraksts {{
            font-size: 0.75rem;
            color: #aaa;
            margin-bottom: 16px;
        }}

        .filtru-sekcija select {{
            width: 100%;
            padding: 10px 14px;
            border: 1px solid #ddd;
            border-radius: 10px;
            font-family: 'DM Sans', sans-serif;
            font-size: 0.9rem;
            background: #fff;
            outline: none;
            cursor: pointer;
            transition: border-color 0.2s;
        }}

        .filtru-sekcija select:hover {{ border-color: #aaa; }}

        .veikalu-pogas {{
            display: flex;
            gap: 8px;
        }}

        .veikals-poga {{
            flex: 1;
            padding: 9px 12px;
            border: 1.5px solid #ddd;
            border-radius: 10px;
            font-family: 'DM Sans', sans-serif;
            font-size: 0.88rem;
            font-weight: 500;
            text-align: center;
            cursor: pointer;
            user-select: none;
            transition: border-color 0.2s, background 0.2s, color 0.2s, transform 0.15s;
            color: #666;
        }}

        .veikals-poga:hover {{ border-color: #aaa; transform: translateY(-1px); }}

        .veikals-poga.aktīva[data-veikals="visi"] {{
            border-color: #111; background: #111; color: #fff;
        }}
        .veikals-poga.aktīva[data-veikals="Rimi"] {{
            border-color: #e3000b; background: #e3000b; color: #fff;
        }}
        .veikals-poga.aktīva[data-veikals="Maxima"] {{
            border-color: #004FE0; background: #004FE0; color: #fff;
        }}
        .veikals-poga.aktīva[data-veikals="SuperAlko"] {{
            border-color: #f5a800; background: #f5a800; color: #fff;
        }}

        .range-slider {{
            position: relative;
            height: 24px;
            margin-bottom: 16px;
        }}

        .range-slider input[type=range] {{
            position: absolute;
            width: 100%;
            height: 4px;
            background: transparent;
            pointer-events: none;
            -webkit-appearance: none;
            top: 50%;
            transform: translateY(-50%);
        }}

        .range-slider input[type=range]::-webkit-slider-thumb {{
            -webkit-appearance: none;
            width: 20px; height: 20px;
            border-radius: 50%;
            background: #fff;
            border: 2px solid #111;
            pointer-events: all;
            cursor: grab;
            box-shadow: 0 1px 4px rgba(0,0,0,0.15);
            transition: transform 0.15s cubic-bezier(0.34,1.56,0.64,1), box-shadow 0.15s;
        }}

        .range-slider input[type=range]::-webkit-slider-thumb:hover {{
            transform: scale(1.2);
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        }}

        .range-slider input[type=range]::-webkit-slider-thumb:active {{
            cursor: grabbing; transform: scale(1.25);
        }}

        .range-track {{
            position: absolute;
            height: 4px;
            background: #ddd;
            width: 100%;
            top: 50%;
            transform: translateY(-50%);
            border-radius: 2px;
            pointer-events: none;
        }}

        .range-fill {{
            position: absolute;
            height: 4px;
            background: #111;
            top: 50%;
            transform: translateY(-50%);
            border-radius: 2px;
            pointer-events: none;
            transition: left 0.05s, width 0.05s;
        }}

        .range-vertibas {{ display: flex; justify-content: space-between; }}
        .range-vertibas div {{ font-size: 0.75rem; color: #888; }}

        .ievade-wrapper {{
            position: relative;
            display: inline-block;
            margin-top: 4px;
        }}

        .range-ievade {{
            font-family: 'Syne', sans-serif;
            font-size: 0.9rem;
            font-weight: 700;
            color: #111;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 4px 24px 4px 10px;
            background: #f5f5f0;
            width: 80px;
            outline: none;
            transition: border-color 0.2s;
            -moz-appearance: textfield;
            display: block;
        }}

        .range-ievade:focus {{ border-color: #aaa; }}
        .range-ievade::-webkit-outer-spin-button,
        .range-ievade::-webkit-inner-spin-button {{ -webkit-appearance: none; }}

        .ievade-simbols {{
            position: absolute;
            right: 8px;
            top: 50%;
            transform: translateY(-50%);
            font-family: 'Syne', sans-serif;
            font-size: 0.8rem;
            font-weight: 700;
            color: #aaa;
            pointer-events: none;
        }}

        .skaits {{
            text-align: center;
            color: #aaa;
            font-size: 0.85rem;
            margin: 12px 0 24px;
        }}

        .rezgis {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
            gap: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }}

        .nav-rezultatu {{
            display: none;
            text-align: center;
            padding: 60px 20px;
            max-width: 1400px;
            margin: 0 auto;
        }}

        .nav-rezultatu p:first-child {{
            font-family: 'Syne', sans-serif;
            font-size: 1.1rem;
            font-weight: 700;
            margin-bottom: 8px;
        }}

        .nav-rezultatu p:last-child {{ font-size: 0.85rem; color: #aaa; }}

        .karte {{
            background: #fff;
            border: 1px solid #e0e0e0;
            border-radius: 16px;
            overflow: hidden;
            text-decoration: none;
            color: inherit;
            display: flex;
            flex-direction: column;
            position: relative;
            opacity: 0;
            transform: translateY(20px) scale(0.97);
            transition: transform 0.35s cubic-bezier(0.34,1.56,0.64,1),
                        border-color 0.2s, box-shadow 0.3s, opacity 0.3s ease;
        }}

        .karte.redzama {{ opacity: 1; transform: translateY(0) scale(1); }}

        .karte:hover {{
            transform: translateY(-5px) scale(1.01) !important;
            border-color: #ccc;
            box-shadow: 0 12px 32px rgba(0,0,0,0.1);
        }}

        .vieta {{
            position: absolute;
            top: 10px;
            left: 10px;
            z-index: 1;
            font-family: 'Syne', sans-serif;
            font-size: 0.7rem;
            font-weight: 700;
            color: #999;
            letter-spacing: 0.5px;
        }}

        .bilde-zona {{
            position: relative;
            overflow: hidden;
            background: #ffffff;
        }}

        .bilde {{
            width: 100%;
            aspect-ratio: 1;
            object-fit: contain;
            padding: 24px;
            background: #ffffff;
            display: block;
            transition: transform 0.4s cubic-bezier(0.34,1.56,0.64,1);
        }}

        .bilde-zona::after {{
            content: '';
            position: absolute;
            bottom: 0; left: 0; right: 0;
            height: 32px;
            background: linear-gradient(to bottom, transparent, rgba(255,255,255,0.9));
            pointer-events: none;
        }}

        .karte:hover .bilde {{ transform: scale(1.06); }}
        .info {{ padding: 14px 16px; flex: 1; }}

        .nosaukums {{
            font-size: 0.82rem;
            color: #444;
            line-height: 1.4;
            margin-bottom: 10px;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}

        .cena {{
            font-family: 'Syne', sans-serif;
            font-size: 1.4rem;
            font-weight: 700;
            color: #111;
        }}

        .vertiba {{ font-size: 0.75rem; color: #aaa; margin-top: 4px; }}

        .logo {{
            width: 100%;
            height: 40px;
            object-fit: contain;
            padding: 6px 16px;
            background: #f5f5f5;
            transition: opacity 0.2s;
        }}

        .karte:hover .logo {{ opacity: 0.8; }}

        #ielades-indikators {{
            text-align: center;
            padding: 32px;
            color: #aaa;
            font-size: 0.9rem;
        }}

        .augsa-poga {{
            position: fixed;
            bottom: 28px;
            right: 28px;
            width: 44px;
            height: 44px;
            background: #111;
            color: #fff;
            border: none;
            border-radius: 50%;
            font-size: 1.1rem;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0;
            transform: translateY(12px);
            transition: opacity 0.3s, transform 0.3s;
            box-shadow: 0 4px 16px rgba(0,0,0,0.2);
            z-index: 100;
        }}

        .augsa-poga.redzama {{ opacity: 1; transform: translateY(0); }}
        .augsa-poga:hover {{ background: #333; transform: translateY(-2px) !important; }}

        @keyframes fadeDown {{
            from {{ opacity: 0; transform: translateY(-12px); }}
            to   {{ opacity: 1; transform: translateY(0); }}
        }}
    </style>
</head>
<body>
    <h1>Labākās alkohola vērtības</h1>
    <p class="apakšvirsraksts">% × litri ÷ cena — jo augstāk, jo labāk</p>
    <p class="atjaunots">Dati iegūti: {laiks}</p>

    <div class="social-saites">
        <a class="social-saite instagram" href="https://www.instagram.com/salsskabe/" target="_blank">
            <svg class="social-ikona" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="2" y="2" width="20" height="20" rx="5" ry="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="0.5" fill="currentColor"/>
            </svg>
            salsskabe
        </a>
        <a class="social-saite soundcloud" href="https://soundcloud.com/salsskabe" target="_blank">
            <img class="social-ikona" src="https://www.svgrepo.com/show/494355/soundcloud.svg" style="opacity:0.6;filter:saturate(0);">
            salsskabe
        </a>
        <a class="social-saite instagram" href="https://www.instagram.com/ikristapsons08/" target="_blank">
            <svg class="social-ikona" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="2" y="2" width="20" height="20" rx="5" ry="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="0.5" fill="currentColor"/>
            </svg>
            ikristapsons08
        </a>
    </div>

    <div class="josla-sticky" id="josla-sticky">
        <div class="augsa-josla">
            <input type="text" id="meklešana" placeholder="Meklēt pēc nosaukuma...">
            <div class="filtru-wrapper">
                <div class="filtri-poga" id="filtri-poga">
                    Filtri &amp; Kārtošana
                    <span class="filtri-badge" id="filtri-badge">0</span>
                    <span class="bulta">▼</span>
                </div>
                <div class="filtru-dropdown" id="filtru-dropdown">

                    <div class="filtru-reset">
                        <button class="filtru-reset-poga" id="filtru-reset">Notīrīt filtrus</button>
                    </div>

                    <div class="filtru-sekcija">
                        <div class="filtru-virsraksts">Veikals</div>
                        <div class="filtru-apraksts">Filtrē pēc veikala</div>
                        <div class="veikalu-pogas">
                            <div class="veikals-poga aktīva" data-veikals="visi">Visi</div>
                            <div class="veikals-poga" data-veikals="Rimi">Rimi</div>
                            <div class="veikals-poga" data-veikals="Maxima">Maxima</div>
                        </div>
                    </div>

                    <div class="filtru-sekcija">
                        <div class="filtru-virsraksts">Kārtošana</div>
                        <div class="filtru-apraksts">Izvēlies kārtošanas secību</div>
                        <select id="kartošana">
                            <option value="vertiba-labaka">Labākā vērtība → Sliktākā</option>
                            <option value="vertiba-sliktaka">Sliktākā vērtība → Labākā</option>
                            <option value="proc-vairak">Visvairāk % → Vismazāk</option>
                            <option value="proc-mazak">Vismazāk % → Visvairāk</option>
                        </select>
                    </div>

                    <div class="filtru-sekcija">
                        <div class="filtru-virsraksts">Alkohola saturs</div>
                        <div class="filtru-apraksts">Filtrē pēc % satura</div>
                        <div class="range-slider">
                            <div class="range-track"></div>
                            <div class="range-fill" id="proc-fill"></div>
                            <input type="range" id="proc-no" min="{min_alkohols}" max="{max_alkohols}" value="{min_alkohols}" step="0.1">
                            <input type="range" id="proc-lidz" min="{min_alkohols}" max="{max_alkohols}" value="{max_alkohols}" step="0.1">
                        </div>
                        <div class="range-vertibas">
                            <div>Min<div class="ievade-wrapper"><input class="range-ievade" type="number" id="proc-no-teksts" value="{min_alkohols}" min="{min_alkohols}" max="{max_alkohols}" step="0.1"><span class="ievade-simbols">%</span></div></div>
                            <div style="text-align:right">Max<div class="ievade-wrapper"><input class="range-ievade" type="number" id="proc-lidz-teksts" value="{max_alkohols}" min="{min_alkohols}" max="{max_alkohols}" step="0.1"><span class="ievade-simbols">%</span></div></div>
                        </div>
                    </div>

                    <div class="filtru-sekcija">
                        <div class="filtru-virsraksts">Tilpums</div>
                        <div class="filtru-apraksts">Filtrē pēc tilpuma</div>
                        <div class="range-slider">
                            <div class="range-track"></div>
                            <div class="range-fill" id="tilp-fill"></div>
                            <input type="range" id="tilp-no" min="{min_tilpums}" max="{max_tilpums}" value="{min_tilpums}" step="0.001">
                            <input type="range" id="tilp-lidz" min="{min_tilpums}" max="{max_tilpums}" value="{max_tilpums}" step="0.001">
                        </div>
                        <div class="range-vertibas">
                            <div>Min<div class="ievade-wrapper"><input class="range-ievade" type="number" id="tilp-no-teksts" value="{min_tilpums}" min="{min_tilpums}" max="{max_tilpums}" step="0.001"><span class="ievade-simbols">L</span></div></div>
                            <div style="text-align:right">Max<div class="ievade-wrapper"><input class="range-ievade" type="number" id="tilp-lidz-teksts" value="{max_tilpums}" min="{min_tilpums}" max="{max_tilpums}" step="0.001"><span class="ievade-simbols">L</span></div></div>
                        </div>
                    </div>

                    <div class="filtru-sekcija">
                        <div class="filtru-virsraksts">Cena</div>
                        <div class="filtru-apraksts">Filtrē pēc cenas</div>
                        <div class="range-slider">
                            <div class="range-track"></div>
                            <div class="range-fill" id="cena-fill"></div>
                            <input type="range" id="cena-no" min="{min_cena}" max="{max_cena}" value="{min_cena}" step="0.01">
                            <input type="range" id="cena-lidz" min="{min_cena}" max="{max_cena}" value="{max_cena}" step="0.01">
                        </div>
                        <div class="range-vertibas">
                            <div>Min<div class="ievade-wrapper"><input class="range-ievade" type="number" id="cena-no-teksts" value="{min_cena}" min="{min_cena}" max="{max_cena}" step="0.01"><span class="ievade-simbols">€</span></div></div>
                            <div style="text-align:right">Max<div class="ievade-wrapper"><input class="range-ievade" type="number" id="cena-lidz-teksts" value="{max_cena}" min="{min_cena}" max="{max_cena}" step="0.01"><span class="ievade-simbols">€</span></div></div>
                        </div>
                    </div>

                </div>
            </div>
        </div>
    </div>

    <p class="skaits" id="skaits"></p>
    <div class="nav-rezultatu" id="nav-rezultatu">
        <p>Nav rezultātu</p>
        <p>Pamēģini mainīt meklēšanas vārdus vai filtrus</p>
    </div>
    <div class="rezgis" id="rezgis"></div>
    <div id="ielades-indikators">Ielādē vairāk...</div>
    <button class="augsa-poga" id="augsa-poga">↑</button>

    <script>
        const visiProdukti = {produkti_json};
        const MAX_CENA     = {max_cena};
        const MIN_CENA     = {min_cena};
        const MAX_ALKOHOLS = {max_alkohols};
        const MIN_ALKOHOLS = {min_alkohols};
        const MAX_TILPUMS  = {max_tilpums};
        const MIN_TILPUMS  = {min_tilpums};
        let filtreti     = [...visiProdukti];
        let ieladetiLidz = 0;
        const SOLI = 40;
        let meklesanasTimeout;
        let aktīvaisVeikals = 'visi';

        window.addEventListener('scroll', function() {{
            document.getElementById('josla-sticky').classList.toggle('ritina', window.scrollY > 80);
            document.getElementById('augsa-poga').classList.toggle('redzama', window.scrollY > 400);
        }});

        document.getElementById('augsa-poga').addEventListener('click', function() {{
            window.scrollTo({{ top: 0, behavior: 'smooth' }});
        }});

        document.addEventListener('keydown', function(e) {{
            if ((e.ctrlKey && e.key === 'k') || (e.key === '/' && document.activeElement.tagName !== 'INPUT')) {{
                e.preventDefault();
                document.getElementById('meklešana').focus();
                document.getElementById('meklešana').select();
            }}
            if (e.key === 'Escape') {{
                document.getElementById('meklešana').blur();
                document.getElementById('filtri-poga').classList.remove('aktīvs');
                document.getElementById('filtru-dropdown').classList.remove('redzams');
            }}
        }});

        document.querySelectorAll('.veikals-poga').forEach(poga => {{
            poga.addEventListener('click', function() {{
                document.querySelectorAll('.veikals-poga').forEach(p => p.classList.remove('aktīva'));
                this.classList.add('aktīva');
                aktīvaisVeikals = this.dataset.veikals;
                atjaunotFiltrus();
            }});
        }});

        function atjaunotFill(fillId, no, lidz, min, max) {{
            const fill = document.getElementById(fillId);
            const span = max - min;
            fill.style.left  = ((no - min) / span * 100) + '%';
            fill.style.width = ((lidz - no) / span * 100) + '%';
        }}

        function atjaunotBadge() {{
            let skaits = 0;
            if (aktīvaisVeikals !== 'visi') skaits++;
            if (parseFloat(document.getElementById('proc-no').value)  > MIN_ALKOHOLS) skaits++;
            if (parseFloat(document.getElementById('proc-lidz').value) < MAX_ALKOHOLS) skaits++;
            if (parseFloat(document.getElementById('tilp-no').value)   > MIN_TILPUMS)  skaits++;
            if (parseFloat(document.getElementById('tilp-lidz').value) < MAX_TILPUMS)  skaits++;
            if (parseFloat(document.getElementById('cena-no').value)   > MIN_CENA)     skaits++;
            if (parseFloat(document.getElementById('cena-lidz').value) < MAX_CENA)     skaits++;
            if (document.getElementById('meklešana').value.trim())                     skaits++;
            const badge = document.getElementById('filtri-badge');
            badge.textContent = skaits;
            badge.classList.toggle('redzams', skaits > 0);
        }}

        function atjaunotFiltrus() {{
            const vaicajums = document.getElementById('meklešana').value.toLowerCase();
            const kartosana = document.getElementById('kartošana').value;
            const procNo    = parseFloat(document.getElementById('proc-no').value);
            const procLidz  = parseFloat(document.getElementById('proc-lidz').value);
            const tilpNo    = parseFloat(document.getElementById('tilp-no').value);
            const tilpLidz  = parseFloat(document.getElementById('tilp-lidz').value);
            const cenaNo    = parseFloat(document.getElementById('cena-no').value);
            const cenaLidz  = parseFloat(document.getElementById('cena-lidz').value);

            document.getElementById('proc-no-teksts').value   = procNo;
            document.getElementById('proc-lidz-teksts').value = procLidz;
            document.getElementById('tilp-no-teksts').value   = tilpNo;
            document.getElementById('tilp-lidz-teksts').value = tilpLidz;
            document.getElementById('cena-no-teksts').value   = cenaNo;
            document.getElementById('cena-lidz-teksts').value = cenaLidz;

            atjaunotFill('proc-fill', procNo,  procLidz,  MIN_ALKOHOLS, MAX_ALKOHOLS);
            atjaunotFill('tilp-fill', tilpNo,  tilpLidz,  MIN_TILPUMS,  MAX_TILPUMS);
            atjaunotFill('cena-fill', cenaNo,  cenaLidz,  MIN_CENA,     MAX_CENA);
            atjaunotBadge();

            filtreti = visiProdukti.filter(p =>
                p.nosaukums.toLowerCase().includes(vaicajums) &&
                p.alkohols >= procNo  && p.alkohols <= procLidz &&
                p.tilpums  >= tilpNo  && p.tilpums  <= tilpLidz &&
                p.cena     >= cenaNo  && p.cena     <= cenaLidz &&
                (aktīvaisVeikals === 'visi' || p.veikals === aktīvaisVeikals)
            );

            if (kartosana === 'vertiba-labaka') {{
                filtreti.sort((a, b) => b.vertiba - a.vertiba);
            }} else if (kartosana === 'vertiba-sliktaka') {{
                filtreti.sort((a, b) => a.vertiba - b.vertiba);
            }} else if (kartosana === 'proc-vairak') {{
                filtreti.sort((a, b) => b.alkohols - a.alkohols);
            }} else if (kartosana === 'proc-mazak') {{
                filtreti.sort((a, b) => a.alkohols - b.alkohols);
            }}

            document.getElementById('rezgis').innerHTML = '';
            ieladetiLidz = 0;
            document.getElementById('skaits').textContent = filtreti.length + ' produkti';
            document.getElementById('nav-rezultatu').style.display = filtreti.length === 0 ? 'block' : 'none';
            ieladeVairak();
        }}

        function notīrītFiltrus() {{
            document.getElementById('meklešana').value = '';
            document.getElementById('kartošana').value = 'vertiba-labaka';
            document.getElementById('proc-no').value   = MIN_ALKOHOLS;
            document.getElementById('proc-lidz').value = MAX_ALKOHOLS;
            document.getElementById('tilp-no').value   = MIN_TILPUMS;
            document.getElementById('tilp-lidz').value = MAX_TILPUMS;
            document.getElementById('cena-no').value   = MIN_CENA;
            document.getElementById('cena-lidz').value = MAX_CENA;
            aktīvaisVeikals = 'visi';
            document.querySelectorAll('.veikals-poga').forEach(p => p.classList.remove('aktīva'));
            document.querySelector('[data-veikals="visi"]').classList.add('aktīva');
            atjaunotFiltrus();
        }}

        document.getElementById('filtru-reset').addEventListener('click', notīrītFiltrus);

        function uzstatitRange(noId, lidzId) {{
            document.getElementById(noId).addEventListener('input', function() {{
                const lidz = parseFloat(document.getElementById(lidzId).value);
                if (parseFloat(this.value) > lidz) this.value = lidz;
                atjaunotFiltrus();
            }});
            document.getElementById(lidzId).addEventListener('input', function() {{
                const no = parseFloat(document.getElementById(noId).value);
                if (parseFloat(this.value) < no) this.value = no;
                atjaunotFiltrus();
            }});
        }}

        function uzstatitIevadi(ievadeId, sliderId, min, max) {{
            document.getElementById(ievadeId).addEventListener('change', function() {{
                let val = parseFloat(this.value);
                if (isNaN(val)) val = min;
                val = Math.min(Math.max(val, min), max);
                this.value = val;
                document.getElementById(sliderId).value = val;
                atjaunotFiltrus();
            }});
        }}

        uzstatitRange('proc-no', 'proc-lidz');
        uzstatitRange('tilp-no', 'tilp-lidz');
        uzstatitRange('cena-no', 'cena-lidz');
        document.getElementById('kartošana').addEventListener('change', atjaunotFiltrus);

        uzstatitIevadi('proc-no-teksts',   'proc-no',   MIN_ALKOHOLS, MAX_ALKOHOLS);
        uzstatitIevadi('proc-lidz-teksts', 'proc-lidz', MIN_ALKOHOLS, MAX_ALKOHOLS);
        uzstatitIevadi('tilp-no-teksts',   'tilp-no',   MIN_TILPUMS,  MAX_TILPUMS);
        uzstatitIevadi('tilp-lidz-teksts', 'tilp-lidz', MIN_TILPUMS,  MAX_TILPUMS);
        uzstatitIevadi('cena-no-teksts',   'cena-no',   MIN_CENA,     MAX_CENA);
        uzstatitIevadi('cena-lidz-teksts', 'cena-lidz', MIN_CENA,     MAX_CENA);

        document.getElementById('filtri-poga').addEventListener('click', function(e) {{
            e.stopPropagation();
            this.classList.toggle('aktīvs');
            document.getElementById('filtru-dropdown').classList.toggle('redzams');
        }});

        document.addEventListener('click', function() {{
            document.getElementById('filtri-poga').classList.remove('aktīvs');
            document.getElementById('filtru-dropdown').classList.remove('redzams');
        }});

        document.getElementById('filtru-dropdown').addEventListener('click', e => e.stopPropagation());

        document.getElementById('rezgis').addEventListener('mouseover', function(e) {{
            const karte = e.target.closest('.karte');
            if (!karte) return;
            const krasa = karte.dataset.krasa;
            if (!krasa) return;
            const r = parseInt(krasa.slice(1,3), 16);
            const g = parseInt(krasa.slice(3,5), 16);
            const b = parseInt(krasa.slice(5,7), 16);
            const bg = `rgb(${{Math.round(r+(255-r)*0.85)}}, ${{Math.round(g+(255-g)*0.85)}}, ${{Math.round(b+(255-b)*0.85)}})`;
            document.body.style.background = bg;
            document.getElementById('josla-sticky').style.background = bg;
        }});

        document.getElementById('rezgis').addEventListener('mouseleave', function() {{
            document.body.style.background = '#f5f5f0';
            document.getElementById('josla-sticky').style.background = '#f5f5f0';
        }});

        document.getElementById('meklešana').addEventListener('input', function() {{
            clearTimeout(meklesanasTimeout);
            meklesanasTimeout = setTimeout(atjaunotFiltrus, 200);
        }});

        function veidotKarti(p) {{
            return `
                <a class="karte" href="${{p.saite}}" target="_blank" data-krasa="${{p.krasa}}">
                    <div class="bilde-zona">
                        <div class="vieta">#${{p.vieta}}</div>
                        <img class="bilde" src="${{p.bilde}}" onerror="this.style.opacity=0" loading="lazy">
                    </div>
                    <div class="info">
                        <p class="nosaukums">${{p.nosaukums}}</p>
                        <p class="cena">${{p.cena.toFixed(2)}}€</p>
                        <p class="vertiba">Vērtība: ${{p.vertiba.toFixed(4)}} | ${{p.alkohols}}% | ${{p.tilpums}}L</p>
                    </div>
                    <img class="logo" src="${{p.logo}}" style="border-top: 3px solid ${{p.veikals_krasa}}" loading="lazy">
                </a>`;
        }}

        function ieladeVairak() {{
            const dala = filtreti.slice(ieladetiLidz, ieladetiLidz + SOLI);
            const rezgis = document.getElementById('rezgis');
            dala.forEach((p, idx) => {{
                const div = document.createElement('div');
                div.innerHTML = veidotKarti(p);
                const karte = div.firstElementChild;
                rezgis.appendChild(karte);
                setTimeout(() => karte.classList.add('redzama'), idx * 25);
            }});
            ieladetiLidz += SOLI;
            document.getElementById('ielades-indikators').style.display =
                ieladetiLidz >= filtreti.length ? 'none' : 'block';
        }}

        const novērotājs = new IntersectionObserver(ieraksti => {{
            if (ieraksti[0].isIntersecting && ieladetiLidz < filtreti.length) ieladeVairak();
        }});
        novērotājs.observe(document.getElementById('ielades-indikators'));

        atjaunotFiltrus();
    </script>
</body>
</html>'''
#automatiski atver musu majaslapu 
fails = os.path.abspath('rezultati.html')
with open(fails, 'w', encoding='utf-8') as f:
    f.write(html)

webbrowser.open(f'file://{fails}')