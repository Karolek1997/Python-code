import requests
import json
import pyodbc
import urllib.parse

server = 'karol'
database = 'Sklep'
connection_string = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'

conn = pyodbc.connect(connection_string)
cursor = conn.cursor()

api_link = "https://api.nike.com/cic/browse/v2?queryid=products&anonymousId=3206839DD97D43F4D435D4A4682E3FDA&country=pl&endpoint=%2Fproduct_feed%2Frollup_threads%2Fv2%3Ffilter%3Dmarketplace(PL)%26filter%3Dlanguage(pl)%26filter%3DemployeePrice(true)%26filter%3DattributeIds(16633190-45e5-4830-a068-232ac7aea82c%2C7baf216c-acc6-4452-9e07-39c2ca77ba32)%26anchor%3D{anchor}%26consumerChannelId%3Dd9a5bc42-4b9c-4976-858a-f159cf99c647%26count%3D{count}&language=pl&localizedRangeStr=%7BlowestPrice%7D%20%E2%80%93%20%7BhighestPrice%7D"

def generate_link(anchor, count):
    return api_link.format(anchor=anchor, count=count)

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
count_per_page = 24

while True:
    url = generate_link(page * count_per_page, count_per_page)
    if not fetch_and_store_data(url):
        break
    page += 1

cursor.close()
conn.close()

print("Dane zostały pomyślnie zaimportowane do bazy danych.")
