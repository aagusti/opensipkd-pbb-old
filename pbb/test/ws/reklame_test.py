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
    data1 = dict(
            command        = 1, #1 insert #2 update #3 delete 
            no_permohonan  = 'TEST 0001', 
            id_permohonan  = 1,
            tgl_permohonan = '2015-01-01',
            no_sk_ipr      = '123456',
            tgl_sk_ipr     = '2015-01-20',
            nama_pemohon   = 'TEST NAMA 01',
            alamat_pemohon = 'TEST ALAMAT', 
            naskah         = 'ROKOK', 
            jenis_reklame_id = 1,
            jenis_nssr_id    = 1,
            lokasi_pasang_id = 1,
            kelas_jalan_id   = 1,
            faktor_lain_id   = 1,
            panjang          = 3,
            lebar            = 5,
            tinggi           = 3,
            muka             = 1,
            jumlah_titik     = 1, 
            sudut_pandang_id = 1,
            ketinggian_id    = 1,
            periode_awal     = '2015-02-01',
            periode_akhir    = '2016-01-31',
            npwpd            = 'NPWPD'
            )
    data2 = dict(
            command        = 2,
            no_permohonan  = 'TEST 0001', 
            id_permohonan  = 1,
            tgl_permohonan = '2015-01-01',
            no_sk_ipr      = '123456',
            tgl_sk_ipr     = '2015-01-20',
            nama_pemohon   = 'TEST NAMA 02',
            alamat_pemohon = 'TEST ALAMAT', 
            naskah         = 'ROKOK', 
            jenis_reklame_id = 1,
            jenis_nssr_id    = 1,
            lokasi_pasang_id = 1,
            kelas_jalan_id   = 1,
            faktor_lain_id   = 1,
            panjang          = 3,
            lebar            = 5,
            tinggi           = 3,
            muka             = 1,
            jumlah_titik     = 1, 
            sudut_pandang_id = 1,
            ketinggian_id    = 1,
            periode_awal     = '2015-02-01',
            periode_akhir    = '2016-01-31',
            npwpd            = 'NPWPD'
            )
            
row_dicted = [data1]
row_dicted.append(data2)
headers = json_rpc_header(username, pass_encrypted)
params = dict(data=row_dicted)
data = dict(jsonrpc = '2.0',
            method = 'set_izin',
            params = params,
            id = 1)
jsondata = json.dumps(data, ensure_ascii=False)
print('Send to {url}'.format(url=url))
print(jsondata)          
rows = requests.post(url, data=jsondata, headers=headers)
print('Result:')
print(json.loads(rows.text))
