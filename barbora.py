from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

URLS = [
    'https://barbora.lv/dzerieni/alus-sidri-un-kokteili',
    'https://barbora.lv/dzerieni/vini',
    'https://barbora.lv/dzerieni/stiprie-alkoholiskie-dzerieni'
]


## -- 1. SOLIS: katrai kategorijai savs draiveris paralēli -----------

def jauns_draiveris():
    options = Options()
    options.add_argument("--log-level=3")
    options.add_argument("--headless=new")
    return webdriver.Chrome(options=options)

def iegut_lapu_skaitu(url):
    driver = jauns_draiveris()

    driver.get(f"{url}?page=1")
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-b-for-cart]'))
    )

    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"))
        ).click()
    except:
        pass

    def lapa_eksiste(n):
        driver.get(f"{url}?page={n}")
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-b-for-cart]'))
            )
            return True
        except:
            return False

    augsa = 1
    while lapa_eksiste(augsa):
        augsa *= 2

    apaksa = augsa // 2
    while apaksa + 1 < augsa:
        vids = (apaksa + augsa) // 2
        if lapa_eksiste(vids):
            apaksa = vids
        else:
            augsa = vids

    driver.quit()
    return url, apaksa

def iegut_lapu_html(args):
    url, lapa_nr = args
    driver = jauns_draiveris()
    try:
        driver.get(f"{url}?page={lapa_nr}")
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-b-for-cart]'))
        )
        return driver.page_source
    except:
        return ''
    finally:
        driver.quit()

# Lapu skaits visām kategorijām paralēli
with ThreadPoolExecutor(max_workers=3) as executor:
    kategoriju_lapas = dict(executor.map(iegut_lapu_skaitu, URLS))

# Visas lapas paralēli
uzdevumi = [(url, lapa) for url, kopa in kategoriju_lapas.items() for lapa in range(1, kopa + 1)]

with ThreadPoolExecutor(max_workers=10) as executor:
    visas_lapas_html = list(executor.map(iegut_lapu_html, uzdevumi))

visas_lapas_html = [h for h in visas_lapas_html if h]


## -- 2. SOLIS: izvelk produktus no html ar bs4 ----------------------

def iegut_produktus(html):
    soup = BeautifulSoup(html, 'html.parser')
    rezultati = []

    for produkts in soup.find_all('li', attrs={'data-cnstrc-item-name': True}):
        nosaukums    = produkts['data-cnstrc-item-name']
        cena         = float(produkts['data-cnstrc-item-price'])
        saite_klucis = produkts.find('a', href=True)
        bilde_klucis = produkts.find('img')

        if not nosaukums or not cena or not saite_klucis: ##erroru eksterminators
            continue

        saite = 'https://barbora.lv' + saite_klucis['href']
        bilde = bilde_klucis['src'] if bilde_klucis else ''
        rezultati.append([nosaukums, cena, saite, bilde])

    return rezultati


def aprekinat_vertibas(visi_produkti):
    vertibas = []

    for nosaukums, cena, saite, bilde in visi_produkti:

        alkohols = 0
        for vards in nosaukums.split():
            if '%' in vards:
                skaitlis = vards.replace('%', '').replace(',', '.').rstrip('.')
                if skaitlis.replace('.', '').isdigit():
                    alkohols = float(skaitlis)
                    break

        tilpums = 0
        nosaukums_lower = nosaukums.lower().replace(' l', 'l').replace(' ml', 'ml')
        for vards in nosaukums_lower.split():
            if vards.endswith('ml') and any(c.isdigit() for c in vards):
                skaitlis = vards.replace('ml', '').replace(',', '.').rstrip('.')
                if skaitlis.replace('.', '').isdigit():
                    tilpums = float(skaitlis) / 1000
                    break
            elif vards.endswith('l') and any(c.isdigit() for c in vards):
                skaitlis = vards.replace('l', '').replace(',', '.').rstrip('.')
                if skaitlis.replace('.', '').isdigit():
                    tilpums = float(skaitlis)
                    break

        vertiba = round((alkohols * tilpums) / cena, 4)
        vertibas.append({'nosaukums': nosaukums, 'cena': cena, 'vertiba': vertiba, 'saite': saite, 'bilde': bilde, 'veikals': 'Barbora', 'alkohols': alkohols, 'tilpums': tilpums})

    return vertibas


with ThreadPoolExecutor() as executor:
    rezultati = list(executor.map(iegut_produktus, visas_lapas_html))

visi_produkti = [p for lapas in rezultati for p in lapas]


if __name__ == '__main__':
    barbora_vertibas = aprekinat_vertibas(visi_produkti)