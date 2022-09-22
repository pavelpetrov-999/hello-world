from bs4 import BeautifulSoup
from urllib.request import urlopen
import threading
eMails = []
urls = []
last_urls =[]
def findEmail(url, TTL, mainUrl):
    eMail = ''
    try:
        #Сразу отсеим ссылки на документы pdf
        if url.find("pdf") < 0:
             # Загрузаем страницу сайта
            page = urlopen(url)
    except Exception:
        return eMail
    #Парсим полученную страницу
    soup = BeautifulSoup(page, 'html.parser')
    #Получаем все теги-ссылки
    page_urls = soup.findAll('a')
    
    #Обрабатываем полученные ссылки
    for element in page_urls:
        #Если тег не пустой
        if element.string != None:
            #Если в тексте тега содержится символ Собака
            if element.string.find('@')>=0:
                # Мы нашли e-mail, возвращаем его
                eMail = element.string
                return eMail
            else:               
                # Если время жизни паука еще не кончилось
                if TTL > 0:
                    try:
                        #Проверяем, что ссылка на страницу и еще не была посещена и находится в пределах обыскиваемого сайта
                        if element['href'].find(mainUrl) >= 0 and last_urls.count(element['href'])<1:
                            #Добавляем ссылку в посещенные
                            last_urls.append(element['href'])
                            #Пробуем получить e-mail с этой страницы, уменьшив время жизни
                            eMail_1 = findEmail(element['href'], TTL-1,mainUrl)
                        #Если получили в результате адрес почты
                        if eMail_1.find('@')>=0:
                            return eMail_1
                    except Exception:
                        eMail_1 = ''
                            
    return eMail

#Фукция-обертка для удобного запуска потока
def startFinder(url, TTL, mainUrl):
    #Отчитываемся о том, что запустили поток
    print("thread " + mainUrl + " start \n")
    #Ищем адреса на сайте (mainUrl нужен для того, чтобы оставаться в пределах сайта)
    eM = findEmail(url, TTL,mainUrl)
    #Добавляем в список
    eMails.append(eM)

events = []
i = 1
while i<=26: #На сайте 26 страниц с полезной иформацией
    # Загружаем страницу
    page = urlopen("https://esir.gov.spb.ru/category/21/?page="+str(i)) 
    
    #Парсим страницу с помощью BeautifulSoup
    soup = BeautifulSoup(page, 'html.parser')
    
    #Получаем со страницы все теги с классом small
    urls_tag = soup.findAll(attrs={"class":"small"})
    
    #Добавляем адреса сайтов в список и запусткаем обработку полученного полученного сайта в отдельном потоке
    for element in urls_tag:
        urls.append(element.string)
        events.append(threading.Thread(target=startFinder,args=('http://' + element.string, 3,element.string)))
        #Запускаем поток
        events[-1].start()   
    i=i+1
i = 1
while i<=5:
    page = urlopen("https://esir.gov.spb.ru/category/22/?page="+str(i))
    soup = BeautifulSoup(page, 'html.parser')
    urls_tag = soup.findAll(attrs={"class":"small"})
    for element in urls_tag:
        urls.append(element.string)
        events.append(threading.Thread(target=startFinder,args=('http://' + element.string, 3,element.string)))
        events[-1].start()
    i=i+1  
#Завершаем потоки
for e in events:
    e.join()
#Открываем файл на запись (Если файла нет, он создастся автоматически)
f = open( 'emails.txt', 'w' )

#Записываем по очереди на отдельные строки все элементы полученного списка
for item in eMails:
    #Если длинна больше трех (убираем пустые строки с сайтов, где не было найдено e-mail)
    if len(item) > 3:
        print(item)
        f.write("%s\n" % item)
#Закрываем файл
f.close()
