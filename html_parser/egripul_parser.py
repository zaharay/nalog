import os
import sys
import re
import string
from bs4 import BeautifulSoup
from requests import Request, Session
from requests_pkcs12 import Pkcs12Adapter
import logging.config
from utils import kesl_check_file

logger = logging.getLogger('app_logger')


class EGRIPULParser:
    def __init__(self, p12_file, p12_pwd):
        self.p12_file = p12_file  # путь к файлу сертификата
        self.p12_pwd = p12_pwd  # пароль сертификата

    @staticmethod
    def _base_url(url):  # URL корневой папки
        return re.search('(^https://)([a-z.]+[/])', str(url).strip().lower())[0]  # включительно с первым одинарным '/'

    @staticmethod
    def _get_file_size(li_tag):  # получаю размер файла в байтах
        try:
            str_size = li_tag.find(
                'span',
                attrs={'class': 'file-size col-md-2 col-sm-2 col-xs-3 text-right'}
            ).text.strip().lower()
            unit = re.findall('[a-z]+', str_size)[0]
            num = float(re.search('^[0-9.]+', str_size)[0])
            if unit == 'kb':
                num *= 1024
            elif unit == 'mb':
                num *= (1024 ** 2)
            elif unit == 'gb':
                num += (1024 ** 3)
            else:
                raise Exception('Unit not recognized!')
            return num
        except Exception as ex:
            # print(f'Error getting the file size: {ex}')
            logger.exception(f'Error getting the file size: {ex}')
            return -1

    def get_secure_html(self, url, stream=True):  # получаю ответ по URL
        with Session() as session:
            try:
                session.mount(
                    url,
                    Pkcs12Adapter(
                        pkcs12_filename=self.p12_file,
                        pkcs12_password=self.p12_pwd
                    )
                )
            except Exception as ex:
                logger.exception(f'Session opening error!')
                return -1
            resp = session.post(url, verify=False, stream=stream)
            if resp.ok:
                # print(f'Response from {url} ОК!')
                return resp
            logger.exception(f'Response from {url}: {resp.status_code}')
            return -1

    def get_last_item(self, url):  # получаю атрибуты (дату, ссылку) последней записи в списке
        page = self.get_secure_html(url)
        if page == -1:
            return -1

        try:
            soup = BeautifulSoup(page.text, 'lxml')
        except Exception as ex:
            logger.exception(f'BS4-parser error: {ex}')
            return -1

        if soup.find('div', class_='alert alert-danger'):
            # print('Error accessing the directory list:', soup.find('div', class_='alert alert-danger').text.strip())
            logger.exception(f'Error accessing the directory list: '
                             f'{soup.find("div", class_="alert alert-danger").text.strip()}')
            return -1

        try:
            ul_tag = soup.find('ul', class_='nav nav-pills nav-stacked')  # unordered list
            # проверяю, начиная с последней записи в списке, которая может быть, например: "nohup.out"
            for li in ul_tag.find_all('li')[::-1]:
                li_a_href = li.find('a').get('href').strip()
                dir_name = li_a_href.rsplit(r'/', 1)[-1]  # после последнего '/'
                dir_name_punct_free = dir_name.translate(str.maketrans('', '', string.punctuation))  # без зн. препин.
                if len(dir_name_punct_free) == 8 and dir_name_punct_free.isdigit():
                    # return self._base_url(url) + str(last_li_a.get('href')).strip()
                    return self._base_url(url) + li_a_href
        except Exception as ex:
            logger.exception(f'Error getting the address of the last directory: {ex}')
            return -1

    def download_by_url(self, url, file_path, file_size, chunk_size=1024):  # chunk_size=128
        resp = self.get_secure_html(url)  # stream=True
        if resp == -1:
            return -1
        dl, scale = 0, 2  # уже скачано, коэффициент сжатия статус-бара
        if resp.ok:
            with open(file_path, 'wb') as file:
                for chunk in resp.iter_content(chunk_size=chunk_size):
                    file.write(chunk)
                    dl += len(chunk)  # скачано [байт]
                    done = int((100 / scale) * dl / file_size)  # % скачанного
                    sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (int(100 / scale) - done)))
                    sys.stdout.flush()
                print("\r")
            # print(f'\nFile "{os.path.basename(file.name)}" download completed!')
            logger.info(f'File "{os.path.basename(file.name)}" download completed!')
            return 0
        logger.exception(f'Error in response from "{url}":', resp.status_code)
        # print(f'Error in response from "{url}":', resp.status_code)
        return -1

    def get_zip_files(self, url, dnld_dir='', kesl_abs_path=None):  # получение ссылок на ZIP-архивы
        page = self.get_secure_html(url)
        if page == -1:
            return -1

        try:
            soup = BeautifulSoup(page.text, 'lxml')
        except Exception as ex:
            logger.exception(f'BS4-parser error: {ex}')
            return -1

        try:
            ul_tag = soup.find('ul', class_='nav nav-pills nav-stacked')  # unordered list
            num_files = 0
            for li_tag in ul_tag.find_all('li'):  # по всем list item (может быть несколько zip-файлов)
                if str(li_tag.get('data-name')).find('.zip') > 0:  # только записи с файлами
                    url = self._base_url(url) + str(li_tag.find('a').get('href'))
                    size_in_bytes = self._get_file_size(li_tag)
                    file_path = os.path.join(dnld_dir, url.strip().rsplit('/', 1)[-1])
                    res = self.download_by_url(
                            url=url,
                            file_path=file_path,
                            file_size=size_in_bytes
                            )
                    if res == -1:
                        return -1

                    # Проверка Касперским (только в Linux):
                    if kesl_abs_path is not None:
                        res = kesl_check_file(kesl_abs_path, file_path)
                        if res == -1:
                            return -1

                    num_files += 1
            logger.info(f'Download of {num_files} file{"s" if num_files > 1 else ""} and anti-virus check is completed!')
            return 0
        except Exception as ex:
            logger.exception(f'Error getting links to ZIP archives: {ex}')
            return -1
