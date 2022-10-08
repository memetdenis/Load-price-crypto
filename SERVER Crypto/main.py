import string
import threading
import time
import MySQLdb
import requests
import tkinter
from functools import partial
from http.server import HTTPServer, BaseHTTPRequestHandler # Веб сервер
from urllib.parse import urlparse, parse_qs # Обработка адресной строки
import shutil # Доступ к файлам
import json # Обработка json


# Массив всех наших бирж и их настроек
class Setting:
    birzi = {
        "Binance": {
            "auto_start":True,
            "count_load":0,
            "icon":"Binance.png",
            "last_time":0,
            "log":""
            },
        "Gate": {
            "auto_start":True,
            "count_load":0,
            "icon":"Gate.png",
            "last_time":0,
            "log":""
            },
        "Huobi": {
            "auto_start":True,
            "count_load":0,
            "icon":"Huobi.png",
            "last_time":0,
            "log":""
            },
        "KuCoin": {
            "auto_start":True,
            "count_load":0,
            "icon":"KuCoin.png",
            "last_time":0,
            "log":""
            }
    }
    
    # Массив настроек
    setting = {
        "refreshTime":180, # Время повторной загрузки в секундах
        "host":"localhost", # Хост для MySQL
        "user":"root", # Логин MySQL
        "passwd":"", # Пароль MySQL
        "db":"price", # База MySQL
        "checkbox": { # Все чекБоксы
            "history_1m": { # Системное имя
                "name": "Каждую минуту, но не более суток", # Название
                "act" : False # Состояние при запуске
            },
            "history_10m": { # Системное имя
                "name": "Каждые 10 минут, но не более суток", # Название
                "act" : True # Состояние при запуске
            },
            "history_1h": { # Системное имя
                "name": "Каждый час, но не более суток", # Название
                "act" : True # Состояние при запуске
            },
            "history_1d": { # Системное имя
                "name": "Раз в день, всегда", # Название
                "act" : True # Состояние при запуске
            }
        },
        "time_load": 0
    }


# Массив с нашими потоками
threading_Job = {} # Пока пустой

class Img:
    def load_favicon(self):
        self.send_response(200)
        self.send_header('Content-type', 'image/ico')
        self.end_headers()
        with open(self.path[1:], 'rb') as content:
            shutil.copyfileobj(content, self.wfile)
        
    def load_img(self):
        self.send_response(200)
        self.send_header('Content-type', 'image/png')
        self.end_headers()
        with open(self.path[1:], 'rb') as content:
            shutil.copyfileobj(content, self.wfile)

class API:
    # Направляем в правильный путь 
    def route(http, get_array):
        if('act' in get_array):
            if(get_array['act'][0]=='setting'):
                return API.setting(http)
            elif(get_array['act'][0]=='birzi'):
                return API.birzi(http)
            elif(get_array['act'][0]=='onoff'):
                return API.onoff(http, get_array)
            elif(get_array['act'][0]=='time_load'):
                return API.time_load(http)
            elif(get_array['act'][0]=='checkbox'):
                return API.checkbox(http)
            elif(get_array['act'][0]=='checkboxOnOff'):
                return API.checkboxOnOff(http, get_array)
            return API.Error(http, get_array)
        else:
           return API.Error(http, get_array) 

    # Переключаем состоянии чекбокса в настройках
    def checkboxOnOff(http, get_array):
        # Сменим переключатель
        if(Setting.setting['checkbox'][get_array['name'][0]]['act']):
            Setting.setting['checkbox'][get_array['name'][0]]['act'] = False
        else:
            Setting.setting['checkbox'][get_array['name'][0]]['act'] = True
        # Отправим новые настройки
        API.send_json(http, Setting.setting['checkbox'])

    # Отправим все чекбоксы в настройках
    def checkbox(http):
        API.send_json(http, Setting.setting['checkbox'])

    # Счетчик времени запуска загрузки скриптов            
    def time_load(http):
        time_load = {
            "time_load":Setting.setting["time_load"]
        }
        API.send_json(http, time_load)

    # Переключаем загрузку биржи        
    def onoff(http, get_array):
        # Сменим переключатель
        if(Setting.birzi[get_array['name'][0]]['auto_start']):
            Setting.birzi[get_array['name'][0]]['auto_start'] = False
        else:
            Setting.birzi[get_array['name'][0]]['auto_start'] = True
        # Отправим новые настройки
        API.send_json(http, Setting.birzi)

    # Список бирж 
    def birzi(http):
        API.send_json(http, Setting.birzi)

    # Список настроек
    def setting(http):
        API.send_json(http, Setting.setting)
    
    # Отправим сообщение об ошибке
    def Error(http, message): 
        error = {
            'code':'error',
            'message': message
        }
        API.send_json(http, error)

    # Отправить сообщение в формате JSON    
    def send_json(http, message):
        http.send_response(200)
        http.send_header('Content-type', 'application/json; charset=UTF-8')
        http.end_headers()
        jsonRequest = json.dumps(message)
        http.wfile.write(f"{jsonRequest}".encode())

class HTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Все переменные запроса GET положим в массив
        get_array = parse_qs(urlparse(self.path).query)

        # Работа с картинками
        if self.path.startswith("/img/"):
            Img.load_img(self)
        # Подгрузим иконку
        elif self.path == "/favicon.ico":
            Img.load_favicon(self)
        #Остальные пути обрабатываем здесь.
        elif self.path.startswith("/api/"):
            #print(get_array)
            API.route(self, get_array)
            pass
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()

            #print(self.path)
            if 'act' in get_array:
                self.wfile.write(f"{get_array['act'][0]}".encode())
            else:
                html = open('index.html','r', encoding = "utf-8").read()
                self.wfile.write(html.encode())
                pass

class Birzi:
    # Загрузка Binance
    def Binance():

        time_start = time.time() # Запомним время страта

        #Получим по ссылки данные с ценами.
        price_list = requests.get("https://api.binance.com/api/v3/ticker/24hr").json() # Получим ответ в виде JSON формата

        # Если в сообщении есть код ошибки, то стоит прервать работу.
        if 'code' in price_list:
            print(f"Error code {price_list['code']} msg = {price_list['msg']}")
            return False
    
        price = []
        # Переберём в цикле все торговые пары
        for symbol in price_list:
            try:
                if float(symbol['lastPrice']) > 0: # Проверим наличие цены
                    price.append([symbol['symbol'],symbol['lastPrice']])
                    
            except Exception as inst:
                print(inst) # Если ошибка доступа к результату

        save_price(price,1)

        # Сообщим о проделанной работе
        
        Setting.birzi['Binance']["count_load"] += 1
        Setting.birzi['Binance']["log"] = f"Загрузил Binance за {round(time.time()-time_start,3)} сек."
        log(Setting.birzi['Binance']["log"], 1)
                
    # Загрузка Gate
    def Gate():
        time_start = time.time()

        #Получим данные в виде JSON
        data = requests.get("https://api.gateio.ws/api/v4/spot/tickers/").json()

        price = []
        #В цикле переберём каждую валюту.
        for symbol in data:
            try:
                price.append([symbol['currency_pair'],symbol['last']])        
            except Exception as inst:
                print(inst) # Если ошибка доступа к результату

        save_price(price,2)

        Setting.birzi['Gate']["count_load"] += 1
        Setting.birzi['Gate']["log"] = f"Загрузка Gate за {round(time.time()-time_start,3)} сек."
        log(Setting.birzi['Gate']["log"], 2)

    # Загрузка Huobi
    def Huobi():

        time_start = time.time() # Запомним время страта

        #Получим по ссылки данные с ценами.
        price_list = requests.get("https://api.huobi.pro/market/tickers").json() # Получим ответ в виде JSON формата
        
        price = []
        # Переберём в цикле все торговые пары
        for symbol in price_list['data']:
            price.append([symbol['symbol'],symbol['close']])
        
        save_price(price,3)

        # Сообщим о проделанной работе
        Setting.birzi['Huobi']["count_load"] += 1
        Setting.birzi['Huobi']["log"] = f"Загрузка Huobi за {round(time.time()-time_start,3)} сек."
        log(Setting.birzi['Huobi']["log"], 3)

    # Загрузка KuCoin
    def KuCoin():

        time_start = time.time() # Запомним время страта

        #Получим по ссылки данные с ценами.
        price_list = requests.get("https://api.kucoin.com/api/v1/market/allTickers").json() # Получим ответ в виде JSON формата

        price = []
        # Переберём в цикле все торговые пары
        for symbol in price_list['data']['ticker']:
            price.append([symbol['symbol'],symbol['last']])
            
        save_price(price,4)
        # Сообщим о проделанной работе
        Setting.birzi['KuCoin']["count_load"] += 1
        Setting.birzi['KuCoin']["log"] = f"Загрузка KuCoin за {round(time.time()-time_start,3)} сек."
        log(Setting.birzi['KuCoin']["log"], 4)
    
#Подключение к базе данных
def connectDB():
    return MySQLdb.connect(host=Setting.setting["host"], user=Setting.setting["user"], passwd=Setting.setting["passwd"], db=Setting.setting["db"])
    
# Расчитаем разницу цен
def price_difference(new : string, old : string):
    if new=='' or new=='0':# Цена не должна быть пустой или 0
        return 0
    else:
        # Переведем строки в числа
        old = float(old)
        new = float(new)
        if old==0:
            return 0
        return round(((new - old) / old) * 100, 2)

# Сохраним список цен под номером биржи
def save_price(price : list, birza: int):
    # Подключимся к базе данных
    conn = connectDB()
    cursor = conn.cursor()

    # Создадим массив со старыми ценами для расчёта изменения цены за 24 часа
    old_time = round(time.time())-86400 # Расчитаем время - 24 часа в секундах
    cursor.execute(f"SELECT `symbol`, `price` FROM `price_history_10m` WHERE `birza` = {birza} AND `last_update` >= {old_time} GROUP BY `symbol` ORDER BY `price_history_10m`.`last_update` ASC; ")
    result = cursor.fetchall()
    crypto_price_old = {}
    for row in result:
        crypto_price_old[row[0]] = float(row[1])

    for symbol in price:
        # Расчитаем изменение цены в процентах
        if symbol[0] in crypto_price_old:
            changes = price_difference(symbol[1],crypto_price_old[symbol[0]])
        else:
            changes = 0
        
        cursor.execute(f"INSERT INTO `price` (`birza`, `symbol`, `price`) VALUES ({birza}, '{symbol[0]}', '{symbol[1]}') ON DUPLICATE KEY UPDATE price = '{symbol[1]}' , `prevDay` = {changes} ,last_update = UNIX_TIMESTAMP();") # Записать изменение цены

        if(Setting.setting["checkbox"]["history_1h"]["act"]):
            cursor.execute(f"INSERT INTO `price_history_1h` (`birza`, `symbol`, `price`) VALUES ({birza}, '{symbol[0]}', {symbol[1]}) ON DUPLICATE KEY UPDATE price = {symbol[1]} , last_update = UNIX_TIMESTAMP();")
        if(Setting.setting["checkbox"]["history_1d"]["act"]):
            cursor.execute(f"INSERT INTO `price_history_1d` (`birza`, `symbol`, `date_day`, `price`) VALUES ({birza}, '{symbol[0]}', now(), {symbol[1]}) ON DUPLICATE KEY UPDATE price = {symbol[1]} ;")
        if(Setting.setting["checkbox"]["history_10m"]["act"]):
            cursor.execute(f"INSERT INTO `price_history_10m` (`birza`, `symbol`, `minut`, `price`) VALUES ({birza}, '{symbol[0]}', concat(SUBSTRING(date_format(now(),'%H:%i'),1,4), '0'), {symbol[1]}) ON DUPLICATE KEY UPDATE price = {symbol[1]} , last_update = UNIX_TIMESTAMP();")
        if(Setting.setting["checkbox"]["history_1m"]["act"]):
            cursor.execute(f"INSERT INTO `price_history_1m` (`birza`, `symbol`, `minut`, `price`) VALUES ({birza}, '{symbol[0]}', date_format(current_timestamp(),'%H:%i'), {symbol[1]}) ON DUPLICATE KEY UPDATE price = {symbol[1]} , last_update = UNIX_TIMESTAMP();")

    conn.commit()
    conn.close()

# Бесконечный цикл для бирж
def while_Birzi():

    # Старт перенесём назад во времени, что бы первая загрузка произошла сразу
    start_time = round(time.time())-Setting.setting["refreshTime"]

    while True:
        timer = start_time+Setting.setting["refreshTime"] - round(time.time())
        if timer <= 0:# Пора запускать
            loadAllBirzi()
            Setting.setting['time_load'] = 0
            start_time = round(time.time()) # Сбросим время
        else: # Ждем ещё секунду
            Setting.setting['time_load'] +=1
            time.sleep(1)

# Загружаем биржи
def loadAllBirzi():
    if(Setting.birzi['Binance']['auto_start']):
        threading.Thread(target = Birzi.Binance).start()
    if(Setting.birzi['Gate']['auto_start']):
        threading.Thread(target = Birzi.Gate).start()
    if(Setting.birzi['Huobi']['auto_start']):
        threading.Thread(target = Birzi.Huobi).start()
    if(Setting.birzi['KuCoin']['auto_start']):
        threading.Thread(target = Birzi.KuCoin).start()

def log(message:string, birza:int):
    #conn = connectDB()
    #cursor = conn.cursor()
    #cursor.execute(f"INSERT INTO `log` (`message`, `birza`, `time_create`) VALUES ('{message}', {birza}, UNIX_TIMESTAMP());")
    #conn.commit()
    #conn.close()
    print(message)

if __name__ == '__main__':

    # Запустим бесконечный цикл для запуска бирж
    threading.Thread(target = while_Birzi).start()

    # Запускаем web сервер для управления работой
    httpd = HTTPServer(('', 8000), HTTPRequestHandler)
    httpd.serve_forever()