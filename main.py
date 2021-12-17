import os
import re
from datetime import datetime
import configparser
import urllib3
from html_parser import HTMLParser


def date_from_str(str_date):  # дата из строки 'ДД.ММ.ГГГГ'
    try:
        date = datetime.strptime(str(str_date).strip(), '%d.%m.%Y')
        return date.date()
    except Exception as ex:
        print(f'Ошибка преобразования даты: {ex}')
        exit(-1)


def str_date_from_url(url):  # строка с датой из URL
    return re.search('^[0-9.]+', url.strip().rsplit('/', 1)[-1])[0]  # только цифры и точка после последнего '/'


def main():
    # Игнор предупреждения от urllib3:
    urllib3.disable_warnings(urllib3.exceptions.SecurityWarning)

    config = configparser.ConfigParser()  # создаём объекта парсера
    config.read('config.ini')  # читаем конфиг

    # Парсим ЕГРИП:
    # =================================================================================================================
    config_section = 'egrip'
    egrip_parser = HTMLParser(
        config[config_section]['p12_file'],
        config[config_section]['pwd']
    )
    try:
        # Получаю директорию с последним обновлением:
        egrip_last_dir_url = egrip_parser.get_last_item(config[config_section]['url'])
        if egrip_last_dir_url == -1:
            exit(-1)
    except Exception as ex:
        print(f'Error getting the address of the last directory "{config_section}": {ex}')


    egrip_str_date = str_date_from_url(egrip_last_dir_url)
    # проверка даты последнего обновления:
    if date_from_str(config[config_section]['last_date']) < date_from_str(egrip_str_date):
        # требуется загрузка файлов обновлений:
        dnld_dir = os.path.normpath(
            config[config_section]['zip_dir'])  # папка на локальном диске для загрузки ZIP-файлов
        # dnld_dir = os.path.abspath(os.getcwd())
        # egrip_parser.get_zip_files(egrip_last_dir_url, dnld_dir)  # текущая директория
        egrip_parser.get_zip_files('https://ftp.egrul.nalog.ru/?dir=EGRIP_405/01.01.2021_FULL', dnld_dir)

        # обновляю дату последнего релиза в файле конфигурации:
        config.set(config_section, 'last_date', egrip_str_date)
        with open('config.ini', 'w') as config_file:
            config.write(config_file)
    else:
        print('This date is already fixed in the configuration file. No download is required.')

    # Парсим ЕГРЮЛ:
    # =================================================================================================================
    config_section = 'egrul'
    egrip_parser = HTMLParser(
        config[config_section]['p12_file'],
        config[config_section]['pwd']
    )
    try:
        # Получаю директорию с последним обновлением:
        egrip_last_dir_url = egrip_parser.get_last_item(config[config_section]['url'])
        if egrip_last_dir_url == -1:
            exit(-1)
    except Exception as ex:
        print(f'Error getting the address of the last directory "{config_section}": {ex}')

    egrip_str_date = str_date_from_url(egrip_last_dir_url)
    # проверка даты последнего обновления:
    if date_from_str(config[config_section]['last_date']) < date_from_str(egrip_str_date):
        # требуется загрузка файлов обновлений:
        dnld_dir = os.path.normpath(
            config[config_section]['zip_dir'])  # папка на локальном диске для загрузки ZIP-файлов
        # dnld_dir = os.path.abspath(os.getcwd())
        egrip_parser.get_zip_files(egrip_last_dir_url, dnld_dir)  # текущая директория
        # egrip_parser.get_zip_files('https://ftp.egrul.nalog.ru/?dir=EGRIP_405/17.12.2020')

        # обновляю дату последнего релиза в файле конфигурации:
        config.set(config_section, 'last_date', egrip_str_date)
        with open('config.ini', 'w') as config_file:
            config.write(config_file)
    else:
        print('This date is already fixed in the configuration file. No download is required.')

    # =================================================================================================================

    return 0

if __name__ == '__main__':
    start_dt = datetime.now()
    print(f'Running the script at: {start_dt.strftime("%d.%m.%Y %H:%M:%S")}\n{50*"-"}')
    main()
    stop_dt = datetime.now()
    print(f'The script finished working at: {stop_dt.strftime("%d.%m.%Y %H:%M:%S")},\nTotal: {stop_dt - start_dt}')