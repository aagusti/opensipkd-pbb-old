import sys
import requests
import json
from tools import json_rpc_header

argv = sys.argv

# def main(argv=sys.argv):
penerima = argv[1]
pesan = argv[2]
if argv[3:]:
    url = argv[3]
else:
    url = 'http://127.0.0.1:6543/ws/reklame'
if argv[5:]:
    username = argv[4]
    pass_encrypted = argv[5]
else:
    from config import (
        username,
        pass_encrypted,
    )
row_dicted = []
headers = json_rpc_header(username, pass_encrypted)
params = dict(data=row_dicted)
data = dict(jsonrpc = '2.0',
            method = 'get_faktor_lain',
            params = params,
            id = 1)
jsondata = json.dumps(data, ensure_ascii=False)
print('Send to {url}'.format(url=url))
print(jsondata)          
rows = requests.post(url, data=jsondata, headers=headers)
print('Result:')
print(json.loads(rows.text))
