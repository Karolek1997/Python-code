import requests
import pyodbc

connection_string = 'DRIVER={SQL Server};SERVER=karol;DATABASE=Sklep;Trusted_Connection=yes;'

try:
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
except pyodbc.Error as e:
    print(f"Błąd połączenia z bazą danych: {e}")
    exit()

api_links = [
    "https://api.nike.com/cic/browse/v2?queryid=products&anonymousId=3206839DD97D43F4D435D4A4682E3FDA&country=pl&endpoint=%2Fproduct_feed%2Frollup_threads%2Fv2%3Ffilter%3Dmarketplace(PL)%26filter%3Dlanguage(pl)%26filter%3DemployeePrice(true)%26filter%3DattributeIds(16633190-45e5-4830-a068-232ac7aea82c%2C7baf216c-acc6-4452-9e07-39c2ca77ba32)%26anchor%3D{anchor}%26consumerChannelId%3Dd9a5bc42-4b9c-4976-858a-f159cf99c647%26count%3D{count}&language=pl&localizedRangeStr=%7BlowestPrice%7D%20%E2%80%93%20%7BhighestPrice%7D",
    "https://api.nike.com/cic/browse/v2?queryid=products&anonymousId=3206839DD97D43F4D435D4A4682E3FDA&country=pl&endpoint=%2Fproduct_feed%2Frollup_threads%2Fv2%3Ffilter%3Dmarketplace(PL)%26filter%3Dlanguage(pl)%26filter%3DemployeePrice(true)%26filter%3DattributeIds(0f64ecc7-d624-4e91-b171-b83a03dd8550%2C16633190-45e5-4830-a068-232ac7aea82c)%26anchor%3D{anchor}%26consumerChannelId%3Dd9a5bc42-4b9c-4976-858a-f159cf99c647%26count%3D{count}&language=pl&localizedRangeStr=%7BlowestPrice%7D%20%E2%80%93%20%7BhighestPrice%7D",
    "https://api.nike.com/cic/browse/v2?queryid=products&anonymousId=3206839DD97D43F4D435D4A4682E3FDA&country=pl&endpoint=%2Fproduct_feed%2Frollup_threads%2Fv2%3Ffilter%3Dmarketplace(PL)%26filter%3Dlanguage(pl)%26filter%3DemployeePrice(true)%26filter%3DattributeIds(16633190-45e5-4830-a068-232ac7aea82c%2C145ce13c-5740-49bd-b2fd-0f67214765b3)%26anchor%3D{anchor}%26consumerChannelId%3Dd9a5bc42-4b9c-4976-858a-f159cf99c647%26count%3D{count}&language=pl&localizedRangeStr=%7BlowestPrice%7D%20%E2%80%93%20%7BhighestPrice%7D"
]

def generate_link(base_link, anchor, count):
    return base_link.format(anchor=anchor, count=count)

def fetch_and_store_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        products = response.json().get('data', {}).get('products', {}).get('products', [])
        if not products:
            return False

        for product in products:
            pid = product.get('pid')
            title = product.get('title')
            subtitle = product.get('subtitle')
            for colorway in product.get('colorways', []):
                cursor.execute("""
                    INSERT INTO Informacjeoproduktach (Nazwa, Podtytuł, Aktualna_cena, Pelna_cena, UnikalneID, Dostepnosc)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (title, subtitle, colorway.get('price', {}).get('currentPrice'), 
                      colorway.get('price', {}).get('fullPrice'), pid, colorway.get('inStock')))
        conn.commit()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Błąd pobierania danych z URL: {url}\n{e}")
        return False

count_per_page = 24
for base_link in api_links:
    page = 0
    while fetch_and_store_data(generate_link(base_link, page * count_per_page, count_per_page)):
        page += 1

cursor.close()
conn.close()
print("Dane zostały pomyślnie zaimportowane do bazy danych.")
