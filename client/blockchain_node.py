import requests

params = {
    'sender': 'igor',
    'recipient': 'ivan',
    'amount': 12
}
# resp = requests.post('http://localhost:5000/transactions/new', params=params)
# print(resp.content)

# url = 'http://localhost:5000/mine'
# mine = requests.get(url=url)
# print(mine.status_code)
# print(mine.content)

url_chian = 'http://localhost:5000/chain'
r = requests.get(url=url_chian)
print(r.content)
