import requests
import json
from bs4 import BeautifulSoup as bs
import pandas as pd


cookies = {
    'PHPSESSID': 'd9f1m4t0m221iuqv49v5ldmh70',
}

headers = {
    'authority': 'actelocale.gov.md',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'x-requested-with': 'XMLHttpRequest',
    'sec-ch-ua-mobile': '?0',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36',
    'sec-ch-ua-platform': '"Windows"',
    'origin': 'https://actelocale.gov.md',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://actelocale.gov.md/',
    'accept-language': 'ro-RO,ro;q=0.9,en-SE;q=0.8,en;q=0.7,sv-SE;q=0.6,sv;q=0.5,ru-RU;q=0.4,ru;q=0.3,da-DK;q=0.2,da;q=0.1,en-US;q=0.1',
    # 'cookie': 'PHPSESSID=d9f1m4t0m221iuqv49v5ldmh70',
    'dnt': '1',
    'sec-gpc': '1',
}

data = {
    'sEcho': '1',
    'iColumns': '1',
    'sColumns': '',
    'iDisplayStart': '1000',
    'iDisplayLength': '1000',
    'sSearch': '',
    'bRegex': 'false',
    'sSearch_0': '',
    'bRegex_0': 'false',
    'bSearchable_0': 'true',
    'iSortingCols': '0',
    'bSortable_0': 'true',
    'raion': '',
    'apl': '',
    'intext': '',
    'ord_number': '',
    'intext_method': '1',
    'release_date_from': '',
    'release_date_to': '',
}

"""resp1 = requests.post('https://actelocale.gov.md/ral/search/search_request',\
     headers=headers, cookies=cookies, data=data)

print(resp1.json()["iTotalRecords"])
print(len(resp1.json()['aaData']))"""

import sys
if __name__ == "__main__":
    print("Executing the main")
else: 
    print(f"Imported {sys.argv[0]}")