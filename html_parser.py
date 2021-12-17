import os
import sys
import re
from bs4 import BeautifulSoup
from requests import Request, Session
from requests_pkcs12 import Pkcs12Adapter


class HTMLParser:
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
            print(f'Error getting the file size: {ex}')
            exit(-1)

    def get_html(self, url, stream=True):  # получаю ответ по URL
        with Session() as session:
            session.mount(
                url,
                Pkcs12Adapter(
                    pkcs12_filename=self.p12_file,
                    pkcs12_password=self.p12_pwd
                )
            )
            resp = session.post(url, verify=False, stream=stream)
            if resp.ok:
                print(f'Response from {url} ОК!')
                return resp
            print('Response from {url}:', resp.status_code)

    def get_last_item(self, url):  # получаю атрибуты (дату, ссылку) последней записи в списке
        soup = BeautifulSoup(self.get_html(url).text, 'lxml')
        if soup.find('div', class_='alert alert-danger'):
            print('Ошибка при обращении к списку каталогов:', soup.find('div', class_='alert alert-danger').text.strip())
            return -1
        ul_tag = soup.find('ul', class_='nav nav-pills nav-stacked')  # unordered list
        last_li_a = ul_tag.find_all('li')[-1].find('a')  # последняя запись в списке

        return self._base_url(url) + str(last_li_a.get('href')).strip()

    def download_by_url(self, url, file_path, file_size, chunk_size=1024):  # chunk_size=128
        resp = self.get_html(url)  # stream=True
        dl, scale = 0, 2  # уже скачано, коэффициент сжатия статус-бара
        if resp.ok:
            with open(file_path, 'wb') as file:
                for chunk in resp.iter_content(chunk_size=chunk_size):
                    file.write(chunk)
                    dl += len(chunk)  # скачано [байт]
                    done = int((100 / scale) * dl / file_size)  # % скачанного
                    sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (int(100 / scale) - done)))
                    sys.stdout.flush()
            print(f'\nFile "{os.path.basename(file.name)}" download completed!')
            return 0
        print(f'Error in response from "{url}":', resp.status_code)
        exit(-1)

    def get_zip_files(self, url, dnld_dir=''):  # получение ссылок на ZIP-архивы
        soup = BeautifulSoup(self.get_html(url).text, 'lxml')
        ul_tag = soup.find('ul', class_='nav nav-pills nav-stacked')  # unordered list
        num_files = 0
        for li_tag in ul_tag.find_all('li'):  # по всем list item (может быть несколько zip-файлов)
            if str(li_tag.get('data-name')).find('.zip') > 0:  # только записи с файлами
                url = self._base_url(url) + str(li_tag.find('a').get('href'))
                size_in_bytes = self._get_file_size(li_tag)
                self.download_by_url(
                    url=url,
                    file_path=os.path.join(dnld_dir, url.strip().rsplit('/', 1)[-1]),
                    file_size=size_in_bytes
                    )
                num_files += 1
        print(f'Download of {num_files} file{"s" if num_files > 1 else ""} is completed!')