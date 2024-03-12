#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to gather historical cryptocurrency data from coinmarketcap.com (cmc) """

import json
import requests
from bs4 import BeautifulSoup
import csv
import sys
from time import sleep

def CoinNames():
    """Gets ID's of all coins on cmc"""

    names = []
    response = requests.get("https://api.coinmarketcap.com/v1/ticker/?limit=0")
    respJSON = json.loads(response.text)
    for i in respJSON:
        names.append(i['id'])
    return names

def gather(startdate, enddate, names):
    historicaldata = []
    counter = 1

    if len(names) == 0:
        names = CoinNames()

    for coin in names:
        sleep(10)  # Be polite to the server
        r = requests.get(f"https://coinmarketcap.com/currencies/{coin}/historical-data/?start={startdate}&end={enddate}")
        data = r.text
        soup = BeautifulSoup(data, "html.parser")
        table = soup.find('table', attrs={"class": "table"})

        # Add table header to list
        if len(historicaldata) == 0:
            headers = [header.text for header in table.find_all('th')]
            headers.insert(0, "Coin")

        for row in table.find_all('tr'):
            currentrow = [val.text for val in row.find_all('td')]
            if len(currentrow) != 0:
                currentrow.insert(0, coin)
                historicaldata.append(currentrow)

        print(f"Coin Counter -> {counter}", end='\r')
        counter += 1

    return headers, historicaldata

def _gather(startdate, enddate, names):
    """ Scrape data off cmc"""
    headers, historicaldata = gather(startdate, enddate, names)
    Save(headers, historicaldata)

def Save(headers, rows):
    filename = "HistoricalCoinData.csv" if len(sys.argv) <= 3 else f"{sys.argv[3]}.csv"
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(row for row in rows if row)
    print("Finished!")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python crypto_history.py startdate enddate [coin1,coin2,...]")
        sys.exit(1)

    startdate = sys.argv[1]
    enddate = sys.argv[2]
    if len(sys.argv) > 3:
        crypto_names = sys.argv[3].split(',')  # Split the third argument into a list
    else:
        crypto_names = []  # If no cryptocurrencies are specified, use an empty list to scrape all

    _gather(startdate, enddate, crypto_names)
