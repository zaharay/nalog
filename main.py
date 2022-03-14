import logging.config
from log_settings import logger_config
from utils import *
import os
from sys import platform
import re
from datetime import datetime
import configparser
import urllib3
# from html_parser import HTMLParser
import html_parser
import pprint

#
from utils import kesl_check_file


logging.config.dictConfig(logger_config)
s_logger = logging.getLogger('simple_logger')  # логгер для старта и стопа
logger = logging.getLogger('app_logger')  # основной логгер


def main():
    abs_path_conf = os.path.abspath('~/')  # текущая директория, где запущен скрипт

    # Игнор предупреждения от urllib3:
    urllib3.disable_warnings(urllib3.exceptions.SecurityWarning)

    # Файл конфигурации в зависимости от ОС:
    if platform == "linux" or platform == "linux2":  # Linux...
        abs_path_conf = os.path.abspath('config.ini')
    elif platform == "win32":  # Windows...
        abs_path_conf = os.path.abspath('config_win.ini')
    else:
        pass

    try:
        # Конфигурация:
        config = configparser.ConfigParser()  # создаём объекта парсера
        ex = config.read(abs_path_conf)  # читаем конфиг
        if not ex:
            raise Exception('File not found or empty!')
    except Exception as ex:
        logger.exception(f'Error accessing the configuration file: {ex}')
        return -1

    # Парсим ЕРСМСП:
    # =================================================================================================================
    config_section = 'ersmsp'
    logger.info(f'{"_" * 5}Starting processing of section: "{config_section}"{"_" * 5}')
    try:
        html_page = html_parser.get_html(config[config_section]['url'])
        if html_page == -1:
            raise Exception('html_page')

        refs_arr = html_parser.get_data_refs(html_page)  # список с URL-ссылками на архивы
        if refs_arr == -1:
            raise Exception('refs_arr')

        # print(*refs_arr, sep='\n')
        print(refs_arr[0])  # первый элемент списка - URL на последний архив
        print(str_dates_from_url_zip(refs_arr[0]))


    except Exception as err:
        logger.exception(f'Shutdown as a result of an error "{err}" in the section: "{config_section}"')

    logger.info(f'{"_" * 5}Section "{config_section}" processing completed{"_" * 5}')
    # =================================================================================================================
    return 0

    # Агент Касперского (только для Linux):
    # =================================================================================================================
    # kesl_abs_path = None
    # try:
    #     if platform == "linux" or platform == "linux2":  # агент только в Linux
    #         config_section = 'kesl'
    #         kesl_abs_path = config[config_section]['kesl_abs_path']
    #         if not os.path.isfile(kesl_abs_path):
    #             logger.info(f'{"_" * 5}The antivirus program was not found. Execution stopped!{"_" * 5}')
    #             return -1
    # except Exception as err:
    #     logger.exception(f'Shutdown as a result of an error {err} in the section: "{config_section}"')
    #     return -1
    #
    # # Парсим ЕГРИП:
    # # =================================================================================================================
    # config_section = 'egrip'
    # logger.info(f'{"_" * 5}Starting processing of section: "{config_section}"{"_" * 5}')
    # try:
    #     # Экземпляр парсера ЕГРИП:
    #     egrip_parser = html_parser.EGRIPULParser(
    #         config[config_section]['p12_file'],
    #         config[config_section]['pwd']
    #     )
    #
    #     # Получаю директорию с последним обновлением:
    #     egrip_last_dir_url = egrip_parser.get_last_item(config[config_section]['url'])
    #     if egrip_last_dir_url == -1:
    #         raise Exception('egrip_last_dir_url')
    #
    #     # Получаю дату из URL-адреса директории последнего обновления:
    #     egrip_str_date = str_date_from_url(egrip_last_dir_url)
    #     if egrip_str_date == -1:
    #         raise Exception('egrip_str_date')
    #
    #     # Проверка даты последнего обновления:
    #     config_last_date = date_from_str(config[config_section]['last_date'])
    #     current_date = date_from_str(egrip_str_date)
    #     if (config_last_date == -1) or (current_date == -1):
    #         raise Exception('config_last_date or current_date')
    #
    #     if config_last_date < current_date:  # требуется загрузка файлов обновлений:
    #
    #         dnld_dir = os.path.normpath(
    #             config[config_section]['zip_dir'])  # папка на локальном диске для загрузки ZIP-файлов
    #         # dnld_dir = os.path.abspath(os.getcwd())
    #
    #         """
    #         Скачивание ZIP-файлов и их проверка агентом Касперского (в Linux)
    #         """
    #         egrip_parser.get_zip_files(egrip_last_dir_url, dnld_dir, kesl_abs_path)  # dnld_dir - текущая директория
    #         # egrip_parser.get_zip_files('https://ftp.egrul.nalog.ru/?dir=EGRIP_405/01.01.2021_FULL', dnld_dir)  # проверка
    #
    #         # обновляю дату последнего релиза в файле конфигурации:
    #         config.set(config_section, 'last_date', egrip_str_date)
    #         with open('config.ini', 'w') as config_file:
    #             config.write(config_file)
    #     else:
    #         logger.info(f'This date is already fixed in the configuration file. No download is required.')
    #         # print('This date is already fixed in the configuration file. No download is required.')
    #
    #     del egrip_parser
    #
    # except Exception as err:
    #     logger.exception(f'Shutdown as a result of an error "{err}" in the section: "{config_section}"')
    #
    # logger.info(f'{"_" * 5}Section "{config_section}" processing completed{"_" * 5}')
    #
    # # Парсим ЕГРЮЛ:
    # # =================================================================================================================
    # config_section = 'egrul'
    # logger.info(f'{"_" * 5}Starting processing of section: "{config_section}"{"_" * 5}')
    # try:
    #     # Экземпляр парсера ЕГРЮЛ:
    #     egrul_parser = html_parser.EGRIPULParser(
    #         config[config_section]['p12_file'],
    #         config[config_section]['pwd']
    #     )
    #
    #     # Получаю директорию с последним обновлением:
    #     egrul_last_dir_url = egrul_parser.get_last_item(config[config_section]['url'])
    #     if egrul_last_dir_url == -1:
    #         raise Exception('egrul_last_dir_url')
    #
    #     # Получаю дату из URL-адреса директории последнего обновления:
    #     egrul_str_date = str_date_from_url(egrul_last_dir_url)
    #     if egrul_str_date == -1:
    #         raise Exception('egrul_str_date')
    #
    #     # Проверка даты последнего обновления:
    #     config_last_date = date_from_str(config[config_section]['last_date'])
    #     current_date = date_from_str(egrul_str_date)
    #     if (config_last_date == -1) or (current_date == -1):
    #         raise Exception('config_last_date or current_date')
    #
    #     if config_last_date < current_date:  # требуется загрузка файлов обновлений:
    #
    #         dnld_dir = os.path.normpath(
    #             config[config_section]['zip_dir'])  # папка на локальном диске для загрузки ZIP-файлов
    #         # dnld_dir = os.path.abspath(os.getcwd())
    #
    #         """
    #         Скачивание ZIP-файлов и их проверка агентом Касперского
    #         """
    #         egrul_parser.get_zip_files(egrul_last_dir_url, dnld_dir, kesl_abs_path)  # текущая директория
    #         # egrip_parser.get_zip_files('https://ftp.egrul.nalog.ru/?dir=EGRIP_405/01.01.2021_FULL', dnld_dir)  # проверка
    #
    #         # обновляю дату последнего релиза в файле конфигурации:
    #         config.set(config_section, 'last_date', egrul_str_date)
    #         with open('config.ini', 'w') as config_file:
    #             config.write(config_file)
    #     else:
    #         logger.info(f'This date is already fixed in the configuration file. No download is required.')
    #         # print('This date is already fixed in the configuration file. No download is required.')
    #
    #     del egrul_parser
    #
    # except Exception as err:
    #     logger.exception(f'Shutdown as a result of an error "{err}" in the section: "{config_section}"')
    #
    # logger.info(f'{"_" * 5}Section "{config_section}" processing completed{"_" * 5}')
    # =================================================================================================================


    return 0


if __name__ == '__main__':
    s_logger.info('Start at')
    str_start = datetime.now().strftime('%d-%m-%Y %H:%M:%S')

    main()

    logger.info('Script running time: {}'.format(get_timedelta(
        str_start,
        datetime.now().strftime('%d-%m-%Y %H:%M:%S'))))
    s_logger.info('Stop at')