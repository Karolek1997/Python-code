import requests
import json
import pyodbc


server = 'karol' 
database = 'Sklep'  
connection_string = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'


conn = pyodbc.connect(connection_string)
cursor = conn.cursor()


url = 'https://api.nike.com/cic/browse/v2?queryid=products&anonymousId=3206839DD97D43F4D435D4A4682E3FDA&country=pl&endpoint=%2Fproduct_feed%2Frollup_threads%2Fv2%3Ffilter%3Dmarketplace(PL)%26filter%3Dlanguage(pl)%26filter%3DemployeePrice(true)%26searchTerms%3Djordan%26anchor%3D48%26consumerChannelId%3Dd9a5bc42-4b9c-4976-858a-f159cf99c647%26count%3D24&language=pl&localizedRangeStr=%7BlowestPrice%7D%20%E2%80%93%20%7BhighestPrice%7D'

html = requests.get(url=url)
output = json.loads(html.text)


for product in output['data']['products']['products']:
    for colorway in product['colorways']:
        current_price = colorway['price']['currentPrice']
        title = product['title']
        subtitle = product['subtitle']
        fullprice = colorway['price']['fullPrice']


        cursor.execute("""
            INSERT INTO Informacjeoproduktach (Nazwa, Podtytuł, Aktualna_cena, Pelna_cena)
            VALUES (?, ?, ?, ?)
        """, (title, subtitle, current_price, fullprice))


conn.commit()
cursor.close()
conn.close()

print("Dane zostały pomyślnie zaimportowane do bazy danych.")