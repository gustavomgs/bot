# -*- coding: utf-8 -*-
# import os, sys
import pandas as pd
import requests as rq
import time
import csv
from bs4 import BeautifulSoup
from selenium import webdriver
from pathlib import Path
import json
import logging
import getpass
import shutil
# import pandas as pd

DRIVER_PATH = str(Path('chromedriver').resolve())

url = 'https://www.nike.com.br/snkrs'

logging.basicConfig(filename='SNKRSlog.log', filemode='a',
                    format='%(asctime)s - %(name)s - %(message)s', level=logging.DEBUG)


def del_tmp_files():
    username = getpass.getuser()
    del_path = "C:\\Users\\" + username + "\\AppData\\Local\\Temp"
    shutil.rmtree(del_path, ignore_errors=True)
    print("Del Path" + del_path)
    return


def write_csv(ads):
    filename = 'results.csv'

    with open(filename, 'a+', newline='', encoding='utf-8') as f:
        fields = ['title', 'url', 'stock', 'thumbnail']
        writer = csv.DictWriter(f, fieldnames=fields)

        # moving file pointer at the start of the file
        f.seek(0)
        existing_lines = csv.reader(f)
        # making data frame from csv file

        # finding no of lines in the file
        count = 0
        for line in existing_lines:
            count += 1
            break

        # if file is not empty
        if count > 0:
            for ad in ads:
                flag = 0

                # moving file pointer to the start of the file
                f.seek(0)
                seen = set()
                # checking if ad['title'] is present in the first column of csv file
                for line in existing_lines:
                    if ad['title'] in line[0]:
                        flag = 1

                        if ad['stock'] != line[2]:
                            print(
                                "\nProduto: " + ad['title'] + ad['stock'] + "\nTabela: " + line[0] + line[2])

                            flag = 2
                # if ad['title'] is not found
                if flag == 0:
                    if ad['stock'] != 'Comprar':
                        print(
                            'Não há nenhum produto novo')
                    if ad['stock'] == 'Avise-me':
                        writer.writerow(ad)
                        print(
                            "Produto novo em calendário: " + ad['title'])
                        data = {
                            'username': 'Haunter Monitor',
                            'avatar_url':  'https://dfgcomunic.com/wp-content/uploads/2021/09/perfil.png',
                            'embeds': [{
                                'title': ad['title'],
                                'description': 'Produto novo no calendário',
                                'url': ad['url'],
                                "thumbnail": {
                                    "url": ad['thumbnail']
                                },
                                'color': '16777215',
                                'footer': {'text': 'Haunter alert'},
                            }]
                        }
                        # SEND DISCORD
                        result = rq.post("#", data=json.dumps(data), headers={
                            "Content-Type": "application/json"})
                        try:
                            result.raise_for_status()
                        except rq.exceptions.HTTPError as err:
                            logging.error(msg=err)
                        else:
                            print("Payload delivered successfully, code {}.".format(
                                result.status_code))
                            logging.info(msg="Payload delivered successfully, code {}.".format(
                                result.status_code))

                    else:
                        writer.writerow(ad)
                        print(
                            "Produto novo enviado ao discord: " + ad['title'])
                        data = {
                            'username': 'Haunter Monitor',
                            'avatar_url':  'https://dfgcomunic.com/wp-content/uploads/2021/09/perfil.png',
                            'embeds': [{
                                'title': ad['title'],
                                'description': 'Produto novo',
                                'url': ad['url'],
                                "thumbnail": {
                                    "url": ad['thumbnail']
                                },
                                'color': '16777215',
                                'footer': {'text': 'Haunter alert'},
                            }]
                        }

                        # SEND DISCORD
                        result = rq.post("#", data=json.dumps(data), headers={
                            "Content-Type": "application/json"})
                        try:
                            result.raise_for_status()
                        except rq.exceptions.HTTPError as err:
                            logging.error(msg=err)
                        else:
                            print("Payload delivered successfully, code {}.".format(
                                result.status_code))
                            logging.info(msg="Payload delivered successfully, code {}.".format(
                                result.status_code))

                if flag == 2:
                    if ad['stock'] != 'Comprar':
                        print(
                            'Não há nenhum restock')

                    else:

                        writer.writerow(ad)

                        print(
                            "Restock do produto: " + ad['title'])
                        data = {
                            'username': 'Haunter Monitor',
                            'avatar_url':  'https://dfgcomunic.com/wp-content/uploads/2021/09/perfil.png',
                            'embeds': [{
                                'title': ad['title'],
                                'description': 'Estoque restabelecido',
                                'url': ad['url'],
                                "thumbnail": {
                                    "url": ad['thumbnail']
                                },
                                'color': '16777215',
                                'footer': {'text': 'Haunter alert'},
                            }]
                        }

                        # SEND DISCORD
                        result = rq.post("#", data=json.dumps(data), headers={
                            "Content-Type": "application/json"})
                        try:
                            result.raise_for_status()
                        except rq.exceptions.HTTPError as err:
                            logging.error(msg=err)
                        else:
                            print("Payload delivered successfully, code {}.".format(
                                result.status_code))
                            logging.info(msg="Payload delivered successfully, code {}.".format(
                                result.status_code))
        # if file is empty write the dictionary contents into the csv
        else:
            for ad in ads:
                writer.writerow(ad)


def get_html(url):
    browser = webdriver.Chrome()
    browser.get(url)
    footer = browser.find_element_by_css_selector("div#footer")
    preY = 0
    while footer.rect['y'] != preY:
        preY = footer.rect['y']
        footer.location_once_scrolled_into_view
        time.sleep(2)
    return browser.page_source


def scrapde_data(card):
    try:
        h2 = card.h2

    except:
        title = ''
        url = ''
        comprar = ''
        thumbnail = ''
    else:
        title = h2.text.strip()
    try:
        url = card.find('a', attrs={'class': 'btn'}).get('href')
        comprar = card.find('a', attrs={'class': 'btn'})
        thumbnail = card.find(
            'img', attrs={'class': 'aspect-radio-box-inside'}).get('data-src')
    except:
        url = ''
        comprar = ''
        thumbnail = ''
    data = {'title': title, 'url': url,
            'stock': comprar.text, 'thumbnail': thumbnail}
    return data


def main():
    contador = 0
    # s = HTMLSession()
    # response = s.get(url)
    # content = response.content

    while True:
        html = get_html(url)
        soup = BeautifulSoup(html, 'lxml')
        cards = soup.find_all('div', class_="produto")

        ads_data = []
        print("Searching (" + str(contador) + ")")
        if contador == 30:
            contador = 0
            time.sleep(15)

        for card in cards:
            data = scrapde_data(card)
            ads_data.append(data)
            write_csv(ads_data)

        contador += 1
        del_tmp_files()
        time.sleep(6)


if __name__ == '__main__':
    main()
