import logging.config
from log_settings import logger_config
from utils import *
import os
import re
from datetime import datetime
import configparser
import urllib3
from html_parser import HTMLParser


logging.config.dictConfig(logger_config)
s_logger = logging.getLogger('simple_logger')  # логгер для старта и стопа
logger = logging.getLogger('app_logger')  # основной логгер


def main():
    # Игнор предупреждения от urllib3:
    urllib3.disable_warnings(urllib3.exceptions.SecurityWarning)

    config = configparser.ConfigParser()  # создаём объекта парсера
    try:
        ex = config.read('config.ini')  # читаем конфиг
        if not ex:
            raise Exception('File not found or empty!')
    except Exception as ex:
        logger.exception(f'Error accessing the configuration file: {ex}')
        return -1

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
            raise Exception()

        # Получаю дату из URL-адреса директории последнего обновления:
        egrip_str_date = str_date_from_url(egrip_last_dir_url)
        if egrip_str_date == -1:
            raise Exception()

        # Проверка даты последнего обновления:
        config_last_date = date_from_str(config[config_section]['last_date'])
        current_date = date_from_str(egrip_str_date)
        if (config_last_date == -1) or (current_date == -1):
            raise Exception()

        if config_last_date < current_date:  # требуется загрузка файлов обновлений:

            dnld_dir = os.path.normpath(
                config[config_section]['zip_dir'])  # папка на локальном диске для загрузки ZIP-файлов
            # dnld_dir = os.path.abspath(os.getcwd())

            egrip_parser.get_zip_files(egrip_last_dir_url, dnld_dir)  # текущая директория
            # egrip_parser.get_zip_files('https://ftp.egrul.nalog.ru/?dir=EGRIP_405/01.01.2021_FULL', dnld_dir)  # проверка

            # обновляю дату последнего релиза в файле конфигурации:
            config.set(config_section, 'last_date', egrip_str_date)
            with open('config.ini', 'w') as config_file:
                config.write(config_file)
        else:
            print('This date is already fixed in the configuration file. No download is required.')

    except Exception:
        logger.exception(f'Shutdown as a result of an error in the section: "{config_section}"')

    # Парсим ЕГРЮЛ:
    # =================================================================================================================
    config_section = 'egrul'
    egrul_parser = HTMLParser(
        config[config_section]['p12_file'],
        config[config_section]['pwd']
    )

    try:
        # Получаю директорию с последним обновлением:
        egrul_last_dir_url = egrul_parser.get_last_item(config[config_section]['url'])
        if egrul_last_dir_url == -1:
            raise Exception()

        # Получаю дату из URL-адреса директории последнего обновления:
        egrul_str_date = str_date_from_url(egrul_last_dir_url)
        if egrip_str_date == -1:
            raise Exception()

        # Проверка даты последнего обновления:
        config_last_date = date_from_str(config[config_section]['last_date'])
        current_date = date_from_str(egrul_str_date)
        if (config_last_date == -1) or (current_date == -1):
            raise Exception()

        if config_last_date < current_date:  # требуется загрузка файлов обновлений:

            dnld_dir = os.path.normpath(
                config[config_section]['zip_dir'])  # папка на локальном диске для загрузки ZIP-файлов
            # dnld_dir = os.path.abspath(os.getcwd())

            egrul_parser.get_zip_files(egrul_last_dir_url, dnld_dir)  # текущая директория
            # egrip_parser.get_zip_files('https://ftp.egrul.nalog.ru/?dir=EGRIP_405/01.01.2021_FULL', dnld_dir)  # проверка

            # обновляю дату последнего релиза в файле конфигурации:
            config.set(config_section, 'last_date', egrul_str_date)
            with open('config.ini', 'w') as config_file:
                config.write(config_file)
        else:
            print('This date is already fixed in the configuration file. No download is required.')

    except Exception:
        logger.exception(f'Shutdown as a result of an error in the section: "{config_section}"')

    # =================================================================================================================
    return 0


if __name__ == '__main__':
    s_logger.info('Start at')
    str_start = datetime.now().strftime('%d-%m-%Y %H:%M:%S')

    main()

    logger.info('\nScript running time: {}'.format(get_timedelta(
        str_start,
        datetime.now().strftime('%d-%m-%Y %H:%M:%S'))))
    s_logger.info('Stop at')