"""
utils.py
Модуль вспомогательных инструментов:
 * config_parser() - парсер файла конфигурации
 * write_csv() - запись фрейма данных в csv-файл
 * replace_list_by_dict() - замена элементов списка значениями из словаря (по ключу)
"""
import re, sys
import subprocess
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


def str_dates_from_url_zip(url):  # строка с датами из URL zip-файла
    """
    Для ЕРСМСП URL вида: https://file.nalog.ru/opendata/7707329152-rsmp/data-10012022-structure-10082021.zip
    :param url: URL на архив ЕРСМСП
    :return: список строк вида: ['10.01.2022', '10.08.2021']
        [0] 10.01.2022 - дату архива
        [1] 10.08.2021 - дата структуры
    """
    try:
        date_arr = re.findall(r'\d+(?:\d+){2}', url.strip().rsplit('/', 1)[-1])
        print(date_arr[0])
        # return re.findall(r'\d+(?:\d+){2}', url.strip().rsplit('/', 1)[-1])  # только цифры и точка после последнего '/'
    except Exception as ex:
        logger.exception(f'Date extraction from URL error: {ex}')
        return -1


def str_date_from_url(url):  # строка с датой из URL папки с архивами
    """
    Дата из URL для ЕГРИП или ЕГРЮЛ вида: https://ftp.egrul.nalog.ru/?dir=EGRIP_405/31.12.2021
    :param url: URL на папку с файлами архивов ЕГРИП или ЕГРЮЛ
    :return: строка вида: '31.12.2021'
    """
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


# Удаляю пробелы в ключах и значениях словаря, значения к int:
def removew(dict_with_ws):
    dict_free_ws = {k.strip(): removew(v) if isinstance(v, dict) else int(v.strip()) for k, v in dict_with_ws.items()}
    return dict_free_ws


"""
Проверка:
--------------------------------
Проверенные объекты          : 1
Всего обнаружено объектов    : 0
Зараженные и другие объекты  : 0
Вылеченные объекты           : 0
Помещено в Хранилище         : 0
Удаленные объекты            : 0
Невылеченный объект          : 0
Ошибки проверки              : 0
Объекты, защищенные паролем  : 0
Пропущено объектов           : 0	
--------------------------------
Scanned objects                     : 1
Total detected objects              : 0
Infected objects and other objects  : 0
Disinfected objects                 : 0
Moved to Storage                    : 0
Removed objects                     : 0
Not disinfected objects             : 0
Scan errors                         : 0
Password-protected objects          : 0
Skipped objects                     : 0
--------------------------------
"""
def kesl_check_file(abs_kesl_name=None, abs_file_name=None):
    str_kesl_res = """
Проверенные объекты          : 1
Всего обнаружено объектов    : 0
Зараженные и другие объекты  : 0
Вылеченные объекты           : 0
Помещено в Хранилище         : 0
Удаленные объекты            : 0
Невылеченный объект          : 0
Ошибки проверки              : 0
Объекты, защищенные паролем  : 0
Пропущено объектов           : 0
"""

    """
    [-T] --scan-file <путь>...        проверить указанные файлы или директории
                                      --action <действие>  действие по отношению к угрозе
                                      <действие> может принимать одно из следующих значений:
                                      Disinfect, Remove, Recommended, Skip, Block
    """
    try:
        # bash_command = f"{abs_kesl_name} --scan-file {abs_file_name} --action Remove"
        # str_kesl_res = subprocess.check_output(bash_command, shell=True, encoding='utf-8')
        kesl_res_dict = removew(dict(line.split(':') for line in str_kesl_res.split('\n') if line != ''))
        print(kesl_res_dict)
        if kesl_res_dict['Проверенные объекты'] > 0 or kesl_res_dict['Scanned objects'] > 0:
            for key in kesl_res_dict:
                if key != 'Проверенные объекты' and key != 'Scanned objects' and kesl_res_dict[key] > 0:
                    logger.info(f'Antivirus check: a virus may be present!')
                    return -1
            logger.info(f'The antivirus check is completed.')
            return 0
        else:
            logger.exception(f'Antivirus scan error. Not a single file has been checked.')
            return -1
    except Exception as ex:
        logger.exception(f'Antivirus scan error: {ex}')
        return -1




    # d_line = dict(line.split(':').strip() for line in str_kesl_res.split(r'\r\n'))
    # print(d_line)



def is_python_version(version):
    return version >= sys.version_info[0] + sys.version_info[1] / 10.
