from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import requests

URL = 'https://www.rimi.lv/e-veikals/lv/produkti/alkoholiskie-dzerieni/c/SH-1'


## -- 1. SOLIS: atver pārlūku un dabū lapu skaitu --------------------

options = Options()
options.add_argument("--log-level=3")
options.add_argument("--headless=new")
options.add_argument("--disable-images")
driver = webdriver.Chrome(options=options)

driver.get(URL)
WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, 'div.js-product-container'))
)

try:
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"))
    ).click()
except:
    pass

soup = BeautifulSoup(driver.page_source, 'html.parser')
kopa_lapas = 1
for lapa in soup.select('li.pagination__item a[data-page]'):
    numurs = int(lapa['data-page'])
    if numurs > kopa_lapas:
        kopa_lapas = numurs

driver.quit()


## -- 2. SOLIS: ielādē visas lapas ar requests ------------------------

def iegut_html(lapa):
    ieladeta_lapa = requests.get(f"{URL}?currentPage={lapa}")
    return ieladeta_lapa.text

with ThreadPoolExecutor(max_workers=10) as executor:
    visas_lapas_html = list(executor.map(iegut_html, range(1, kopa_lapas + 1)))


## -- 3. SOLIS: izvelk produktus no html ar bs4 ----------------------

def iegut_produktus(html):
    soup = BeautifulSoup(html, 'html.parser')
    rezultati = []

    for produkts in soup.find_all('div', class_='js-product-container'):
        nosaukums_klucis = produkts.find('p', class_='card__name')
        cena_klucis      = produkts.find('div', class_='price-tag')
        saite_klucis     = produkts.find('a', class_='card__url')
        bilde_klucis     = produkts.find('img')
        

        if not nosaukums_klucis or not cena_klucis or not saite_klucis: ##erroru eksterminators
            continue

        eiro  = cena_klucis.find('span', attrs={'aria-hidden': 'true'})
        centi = cena_klucis.find('sup')

        nosaukums   = nosaukums_klucis.text
        cena_teksts = eiro.text + '.' + centi.text
        saite       = 'https://www.rimi.lv' + saite_klucis['href']
        bilde       = bilde_klucis['data-src'] if bilde_klucis else ''

        rezultati.append([nosaukums, float(cena_teksts), saite, bilde])

    return rezultati


def aprekinat_vertibas(visi_produkti):
    vertibas = []

    for nosaukums, cena, saite, bilde in visi_produkti:

        alkohols = 0
        for vards in nosaukums.split():
            if "100%" in vards or "100" == vards.replace('%', ''):
                alkohols = 0
                break
            if '%' in vards:
                skaitlis = vards.replace('%', '').replace(',', '.').rstrip('.')
                if skaitlis.replace('.', '').isdigit():
                    alkohols = float(skaitlis)
                    break

        tilpums = 0
        for vards in nosaukums.split():
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
        vertibas.append({'nosaukums': nosaukums, 'cena': cena, 'vertiba': vertiba, 'saite': saite, 'bilde': bilde, 'veikals': 'Rimi', 'alkohols': alkohols, 'tilpums': tilpums})

    return vertibas


visi_produkti = []
for html in visas_lapas_html:
    produkti_no_lapas = iegut_produktus(html)
    visi_produkti = visi_produkti + produkti_no_lapas


if __name__ == '__main__':
    rimi_vertibas = aprekinat_vertibas(visi_produkti)