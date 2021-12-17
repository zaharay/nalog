# egrip (ЕГРИП)
 * Fastest Way to Load Data Into PostgreSQL Using Python (https://hakibenita.com/fast-load-data-python-postgresql)
 * Recursive XML parsing python using ElementTree (https://stackoverflow.com/questions/28194703/recursive-xml-parsing-python-using-elementtree)
 1. SSLError "bad handshake: Error([('SSL routines', 'tls_process_server_certificate', 'certificate verify failed')],)
 with self signed certificate #4381 (см. пост RSwarnkar, commented on 13 Apr 2020):
https://github.com/psf/requests/issues/4381
 2. requests.exceptions.SSLError with tls_process_server_certificate, certificate verify failed for valid p12:
https://github.com/m-click/requests_pkcs12/issues/16
 3. Python: reading a pkcs12 certificate with pyOpenSSL.crypto:
https://stackoverflow.com/questions/6345786/python-reading-a-pkcs12-certificate-with-pyopenssl-crypto:
 4. https://stackoverflow.com/questions/6345786/python-reading-a-pkcs12-certificate-with-pyopenssl-crypto
 5. Installing OpenSSL on Windows 10 and updating PATH: 
https://medium.com/swlh/installing-openssl-on-windows-10-and-updating-path-80992e26f6a1

### Certificate verify failed
Python (pip), Conda и любое другое программное обеспечение на основе python использует отдельное __хранилище сертификатов__,
как и все браузеры. Библиотека Python Requests по умолчанию использует свой собственный CA-файл 
(https://incognitjoe.github.io/adding-certs-to-requests.html)  или будет использовать пакет сертификатов пакета certifi,
если он установлен. Кроме того, pip не использует системные сертификаты, в отличие от curl.
Следовательно, для запросов **requests** необходимо вручную указать хранилище сертификатов через conda или pip.
#### Для этого:
1. Экспортируйте всю цепочку сертификатов в кодировке .cer с помощью браузера в соответствии с этим 
удивительным блогом (http://blog.majcica.com/2016/12/27/installing-self-signed-certificates-into-git-cert-store/).
Обратите внимание, что этот блог посвящен не conda certstore, а git certstore, и в нем говорится только об экспорте 
корневого каталога, однако я экспортировал __все цепочки сертификатов в отдельные файлы__.
2. Затем установите модуль certifi, используя команду pip install certifi.
3. Проверьте путь по умолчанию к хранилищу сертификатов conda или python:
```python
import ssl
ssl.get_default_verify_paths()
 ```
или
```python
import certifi
certifi.where()
```
4. Как только вы найдете файл __cacert.pem__ по умолчанию, откройте его (предпочтительно в Notepad++) и добавьте весь
сертификат в конец файла. (Позаботьтесь о разграничении сертификатов ------BEGIN CERTIFICATE----- и 
-----END CERTIFICATE-----). Сохраните файл.<br>
Или, если вы используете conda, используйте команды conda:
```conda
conda config --set ssl_verify <pathToYourFile>.crt
```
(Замечено, что эта команда обновляет информацию в C:\Users\johndoe\.condarc)
5.Используйте приведенный ниже код для проверки:
```python
import certifi
auth = session.post('https://mysecuresite.com/', cert=());
 ```
Кроме того, если вы используете linux, вы можете экспортировать пользовательский cacert в общесистемный или 
пользовательский профиль (.bashrc или .bash_profile), используя эту ссылку 
(https://stackoverflow.com/questions/38571099/how-can-i-set-the-certificates-in-curl).

### Run/Debug as root in PyCharmRun/Debug as root in PyCharm:
 * http://esmithy.net/2015/05/05/rundebug-as-root-in-pycharm/
### Running Pycharm as root from launcher:
 * https://stackoverflow.com/questions/36530082/running-pycharm-as-root-from-launcher/44647137

### Python run bash command and get output:
 * https://stackoverflow.com/questions/4760215/running-shell-command-and-capturing-the-output
 * https://docs.python.org/3/library/subprocess.html#subprocess.check_output
 * 
