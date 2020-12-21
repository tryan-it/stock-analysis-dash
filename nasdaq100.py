from re import findall
import requests
import pandas as pd
from bs4 import BeautifulSoup
from requests.models import Response

headers = {
        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding":"gzip, deflate",
        "Accept-Language":"en-GB,en;q=0.9,en-US;q=0.8,ml;q=0.7",
        "Connection":"keep-alive",
        "Host":"www.nasdaq.com",
        "Referer":"http://www.nasdaq.com",
        "Upgrade-Insecure-Requests":"1",
        "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36"
  }

url = "https://www.dividendstocksonline.com/topdiv-premium/nasdaq100/"
response = requests.get(url, headers=headers, verify=False)

soup = BeautifulSoup(response.text, "html.parser")

table = soup.find('table', id='tablepress-131')

columns = [header.text for header in table.find("thead").find_all("th")]
results = [{columns[i]: cell.text for i, cell in enumerate(row.find_all('td'))}
           for row in table.find('tbody').find_all('tr')]

symbols = {}
for result in results:
    symbols[result['Symbol']]=result['Name']

symbols_df = pd.DataFrame.from_dict(symbols, orient='index')
symbols_df.to_csv('nasdaq100.csv', index_label='symbol', header=['name'])
