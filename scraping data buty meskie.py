import requests
import json
import pyodbc
import urllib.parse

server = 'karol'
database = 'Sklep'
connection_string = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'

conn = pyodbc.connect(connection_string)
cursor = conn.cursor()

base_url = "https://api.nike.com/cic/browse/v2"
endpoint_template = (
    "/product_feed/rollup_threads/v2?"
    "filter=marketplace(PL)&"
    "filter=language(pl)&"
    "filter=employeePrice(true)&"
    "filter=attributeIds(0f64ecc7-d624-4e91-b171-b83a03dd8550,16633190-45e5-4830-a068-232ac7aea82c)&"
    "anchor={anchor}&"
    "consumerChannelId=d9a5bc42-4b9c-4976-858a-f159cf99c647&"
    "count={count}"
)

def generate_link(anchor, count):
    endpoint = endpoint_template.format(anchor=anchor, count=count)
    params = {
        "queryid": "products",
        "anonymousId": "3206839DD97D43F4D435D4A4682E3FDA",
        "country": "pl",
        "endpoint": endpoint,
        "language": "pl",
        "localizedRangeStr": "{lowestPrice} – {highestPrice}"
    }
    return f"{base_url}?{urllib.parse.urlencode(params, safe=':/(),')}"

def fetch_and_store_data(url):
    try:
        response = requests.get(url=url)
        response.raise_for_status()
        output = response.json()
        products = output.get('data', {}).get('products', {}).get('products', [])
        if products:
            for product in products:
                for colorway in product.get('colorways', []):
                    current_price = colorway.get('price', {}).get('currentPrice')
                    title = product.get('title')
                    subtitle = product.get('subtitle')
                    fullprice = colorway.get('price', {}).get('fullPrice')

                    cursor.execute("""
                        INSERT INTO Informacjeoproduktach (Nazwa, Podtytuł, Aktualna_cena, Pelna_cena)
                        VALUES (?, ?, ?, ?)
                    """, (title, subtitle, current_price, fullprice))
            conn.commit()
            return True
        else:
            return False
    except requests.exceptions.RequestException as e:
        print(f"Błąd pobierania danych z URL: {url}")
        print(e)
        return False

page = 0
count_per_page = 60

while True:
    url = generate_link(page * count_per_page, count_per_page)
    if not fetch_and_store_data(url):
        break
    page += 1

cursor.close()
conn.close()

print("Dane zostały pomyślnie zaimportowane do bazy danych.")
