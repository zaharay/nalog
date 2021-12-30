"""
utils.py
Модуль вспомогательных инструментов:
 * config_parser() - парсер файла конфигурации
 * write_csv() - запись фрейма данных в csv-файл
 * replace_list_by_dict() - замена элементов списка значениями из словаря (по ключу)
"""
import re
import sys
import logging.config
from datetime import datetime

logger = logging.getLogger('app_logger')


def date_from_str(str_date):  # дата из строки 'ДД.ММ.ГГГГ'
    try:
        date = datetime.strptime(str(str_date).strip(), '%d.%m.%Y')
        return date.date()
    except Exception as ex:
        logger.exception(f'Date conversion error: {ex}')
        return -1


def str_date_from_url(url):  # строка с датой из URL
    try:
        return re.search('^[0-9.]+', url.strip().rsplit('/', 1)[-1])[0]  # только цифры и точка после последнего '/'
    except Exception as ex:
        logger.exception(f'Date extraction from URL error: {ex}')
        return -1

def get_timedelta(str_start, str_stop):
    """
    Возвращает разницу во времени между двумя временными метками.
    Формат строк на входе: 'ДД-ММ-ГГГГ ЧЧ:ММ:CC'.
    :param str_start: метка старта
    :param str_stop: метка завершения
    :return: дельта типа 'datetime.timedelta'
    """
    try:
        dt_start = datetime.strptime(str_start, '%d-%m-%Y %H:%M:%S')
        dt_stop = datetime.strptime(str_stop, '%d-%m-%Y %H:%M:%S')
        return dt_stop - dt_start
    except Exception as err:
        logger.exception('\nTime interval calculation error:\n\t{}'.format(err))
        return -1

def is_python_version(version):
    return version >= sys.version_info[0] + sys.version_info[1] / 10.
