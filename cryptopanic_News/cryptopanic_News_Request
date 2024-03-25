import requests

url = "https://cryptopanic.com/api/v1/posts/?auth_token=40638bc52524aa59273d51fac8edc7d377671007&currencies=BTC,ETH,USDT,BNB,SOL,XRP,ADA,AVAX,DOGE&filter=hot"

response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    print(data)
else:
    print("Fehler bei der Anfrage:", response.status_code)