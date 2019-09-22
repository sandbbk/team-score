import requests



host  =  'https://sandbbl.pythonanywhere.com/auth/token/'

url = '/auth/token'
headers = {'Content-Type': 'application/json',
            'Host': 'sandbbl.pythonanywhere.com',
            'User-Agent': 'PostmanRuntime/7.17.1',
            'Accept': '*/*',
            'Cache-Control': 'no-cache',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'cache-control': 'no-cache'}
#response = requests.post(host + url, json={'email': 'sandbbk@gmail.com', 'password': 'andrew1983'}, headers=headers)

response = requests.post(host, json={'email': 'sandbbk@gmail.com', 'password': 'andrew1983'})
print(response.json())
