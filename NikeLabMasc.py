# -*- coding: utf-8 -*-
import os
import sys
import requests as rq
import time
import csv
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from pathlib import Path
import json
import logging
import getpass
import shutil

# import pandas as pd

DRIVER_PATH = str(Path('chromedriver').resolve())

url = 'https://www.nike.com.br/Loja/Masculino/Compre-por-Marcas/NikeLab/153-184-188'
urlfem = 'https://www.nike.com.br/Loja/Feminino/Compre-por-Marcas/NikeLab/1-37-41'

logging.basicConfig(filename='SNKRSlog.log', filemode='a',
                    format='%(asctime)s - %(name)s - %(message)s', level=logging.DEBUG)


def del_tmp_files():
    username = getpass.getuser()
    del_path = "C:\\Users\\" + username + "\\AppData\\Local\\Temp"
    shutil.rmtree(del_path, ignore_errors=True)
    print("Del Path" + del_path)
    return


def write_csv(ads):
    filename = 'results-lancamentos.csv'

    with open(filename, 'a+', newline='', encoding='utf-8') as f:
        fields = ['title', 'url', 'codigo', 'thumbnail']
        writer = csv.DictWriter(f, fieldnames=fields)

        # moving file pointer at the start of the file
        f.seek(0)
        existing_lines = csv.reader(f)

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
                # checking if ad['title'] is present in the first column of csv file
                for line in existing_lines:
                    if ad['codigo'] in line[2]:
                        flag = 1

                # if ad['title'] is not found
                if flag == 0:
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
                            'fields': [
                                {'name': 'Código', 'value':  ad['codigo']},
                            ]
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
                    print(
                        'Não há nenhum produto novo')

        # if file is empty write the dictionary contents into the csv
        else:
            for ad in ads:
                writer.writerow(ad)


def get_html(url):
    browser = webdriver.Chrome(ChromeDriverManager().install())
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
        a = card.find('a', attrs={'class': 'produto__nome'})

    except:
        title = ''
        url = ''
        codigo = ''
    else:
        title = a.text.strip()
        url = card.a.get('href')
        codigo = card.get('data-codigo')
        thumbnail = card.a.img.get('data-src')

    data = {'title': title, 'url': url,
            'codigo': codigo, 'thumbnail': thumbnail}
    print(data)
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
