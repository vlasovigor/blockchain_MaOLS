import requests

resp = requests.get('http://localhost:5000/chain')
print(resp.json())