import os
import sys
import re
import requests
from bs4 import BeautifulSoup
import logging.config

logger = logging.getLogger('app_logger')


"""
Получение ответа (текста страницы) от URL
"""
def get_html(url):
    headers = {
        'User-Agent': 'YaBrowser/22.1.6.114.00 SA/3 Mobile Safari/537.36 '
                      'Chrome/50.0.2661.102 Safari/537.36'
                      }
    resp = requests.get(url, headers=headers, verify=False)

    if resp.ok:  # print(resp.status_code)  # 200 - Ok (True)
        resp.encoding = 'utf-8'
        # print(*dir(resp), sep='\n') # методы
        # print(f'Response from {url}: Ok!')
        logger.info(f'Response from {url}: Ok!')
        return resp.text
    else:
        # print(f'Response from {url}: {resp.status_code}')
        logger.exception(f'Response from {url}: {resp.status_code}')
        return -1


"""
Получение списка ссылок на все наборы данных
Первый элемент списка - ссылка на последний релиз
"""
def get_data_refs(html):
    try:
        soup = BeautifulSoup(html, 'lxml')  # 'html.html_parser')
    except Exception as ex:
        logger.exception(f'Parser error: {ex}')
        return -1

    try:
        table = soup.find(
            'table',
            class_='border_table'
        )

        # Ссылка на последний релиз:
        last_ref = table.find(
            'td',
            text='Гиперссылка (URL) на набор'
        ).find_next_sibling('td').find('a', href=True)['href']

        # Набор тэгов с ссылками на предыдущие релизы:
        a_arr = table.find(
            'td',
            text='Гиперссылки (URL) на предыдущие релизы набора данных'
        ).find_next_sibling('td').find_all('a', href=True)

        n = len(a_arr) + 1  # +1 - с последним набором
        refs = [0] * n
        refs[0] = str(last_ref).strip()
        for i, a in enumerate(a_arr):
            refs[i + 1] = str(a['href']).strip()

        return refs

    except Exception as ex:
        logger.exception(f'HTML-page parsing error: {ex}')
        return -1

