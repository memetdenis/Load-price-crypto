import string
import threading
import time
import MySQLdb
import requests
import tkinter
from functools import partial

# Массив настроек
setting = {
        "refreshTime":60, # Время повторной загрузки в секундах
        "host":"localhost", # Хост для MySQL
        "user":"root", # Логин MySQL
        "passwd":"", # Пароль MySQL
        "db":"price", # База MySQL
        "Checkbox": { # Все чекБоксы
            "history_1m": { # Системное имя
                "name": "Каждую минуту, но не более суток", # Название
                "act" : True # Состояние при запуске
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
        }
    }

# Массив всех наших бирж и их настроек 
RunLoad = {
    "Binance": {
        "auto_start":True,
        "count_load":0
        },
    "Gate": {
        "auto_start":False,
        "count_load":0
        },
    "Huobi": {
        "auto_start":False,
        "count_load":0
        },
    "KuCoin": {
        "auto_start":False,
        "count_load":0
        }
}

# Массив с нашими потоками
threading_Job = {} # Пока пустой

# Массив с нашими формами.
# Что бы не плодить переменные, пишем всё в массив.
frame = {}
    
# Пустой массив для иконок
img = {}

#Подключение к базе данных
def connectDB():
    global setting
    return MySQLdb.connect(host=setting["host"], user=setting["user"], passwd=setting["passwd"], db=setting["db"])

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

def save_price(price : list, birza: int):
    global setting

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

        if(setting["Checkbox"]["history_1h"]["act"]):
            cursor.execute(f"INSERT INTO `price_history_1h` (`birza`, `symbol`, `price`) VALUES ({birza}, '{symbol[0]}', {symbol[1]}) ON DUPLICATE KEY UPDATE price = {symbol[1]} , last_update = UNIX_TIMESTAMP();")
        if(setting["Checkbox"]["history_1d"]["act"]):
            cursor.execute(f"INSERT INTO `price_history_1d` (`birza`, `symbol`, `date_day`, `price`) VALUES ({birza}, '{symbol[0]}', now(), {symbol[1]}) ON DUPLICATE KEY UPDATE price = {symbol[1]} ;")
        if(setting["Checkbox"]["history_10m"]["act"]):
            cursor.execute(f"INSERT INTO `price_history_10m` (`birza`, `symbol`, `minut`, `price`) VALUES ({birza}, '{symbol[0]}', concat(SUBSTRING(date_format(now(),'%H:%i'),1,4), '0'), {symbol[1]}) ON DUPLICATE KEY UPDATE price = {symbol[1]} , last_update = UNIX_TIMESTAMP();")
        if(setting["Checkbox"]["history_1m"]["act"]):
            cursor.execute(f"INSERT INTO `price_history_1m` (`birza`, `symbol`, `minut`, `price`) VALUES ({birza}, '{symbol[0]}', date_format(current_timestamp(),'%H:%i'), {symbol[1]}) ON DUPLICATE KEY UPDATE price = {symbol[1]} , last_update = UNIX_TIMESTAMP();")

    conn.commit()
    conn.close()

# Загрузка Binance
def load_Binance():
    global frame, setting

    time_start = time.time() # Запомним время страта

    #Получим по ссылки данные с ценами.
    price_list = requests.get("https://api.binance.com/api/v3/ticker/24hr").json() # Получим ответ в виде JSON формата

    # Если в сообщении есть код ошибки, то стоит прервать работу.
    if 'code' in price_list:
        print(f"Error code {price_list['code']} msg = {price_list['msg']}")
        time.sleep(10)
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
    frame['Binance']['txt_Job'].configure(text=f"Загрузил за {round(time.time()-time_start,3)} сек.")
    print(f"Загрузил Binance за {round(time.time()-time_start,3)} сек.")

# Цикл запуска загрузки Binance
def while_Binance():
    global setting, RunLoad

    start_time = round(time.time())-setting["refreshTime"]

    birza = "Binance"

    frame[birza]['txt_Job'].configure(text="Запускаю")

    #Цикл работает, пока нужно загружать цены
    while RunLoad[birza]["auto_start"]:
        # Расчитаем время до запуска
        timer = start_time+setting["refreshTime"] - round(time.time())

        if timer <= 0:# Пора запускать
            frame[birza]['txt_time'].configure(text=f"{timer}")
            load_Binance() # Загрузим цены
            RunLoad[birza]["count_load"] += 1
            frame[birza]['count_load'].configure(text=str(RunLoad[birza]["count_load"]))
            start_time = round(time.time()) # Сбросим время
        else: # Ждем ещё секунду
            time.sleep(1)
            frame[birza]['txt_time'].configure(text=f"{timer}") # Выведем таймер на экран

    # Если остановили цикл, то надо подчистить текст.
    frame[birza]['txt_Job'].configure(text="")
    frame[birza]['txt_time'].configure(text="")
               
# Загрузка Gate
def load_Gate():
    global setting

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

    frame['Gate']['txt_Job'].configure(text=f"Загрузил за {round(time.time()-time_start,3)} сек.")
    print(f"Загрузка Gate за {round(time.time()-time_start,3)} сек.")

# Цикл запуска загрузки Gate
def while_Gate():
    global setting, RunLoad

    # Запомним 
    start_time = round(time.time())-setting["refreshTime"]

    # Название биржи в масииве. 
    # Для доступа к форме и состоянию загрузки
    birza = "Gate" 

    frame[birza]['txt_Job'].configure(text="Запускаю")

    #Цикл работает, пока нужно загружать цены
    while RunLoad[birza]["auto_start"]:
        # Расчитаем время до запуска
        timer = start_time+setting["refreshTime"] - round(time.time())

        if timer <= 0:# Пора запускать
            frame[birza]['txt_time'].configure(text=f"{timer}")
            load_Gate() # Загрузим цены
            RunLoad[birza]["count_load"] += 1
            frame[birza]['count_load'].configure(text=str(RunLoad[birza]["count_load"]))
            start_time = round(time.time()) # Сбросим время
        else: # Ждем ещё секунду
            time.sleep(1)
            frame[birza]['txt_time'].configure(text=f"{timer}") # Выведем таймер на экран

    # Если остановили цикл, то надо подчистить текст.
    frame[birza]['txt_Job'].configure(text="")
    frame[birza]['txt_time'].configure(text="")

# Загрузка Huobi
def load_Huobi():
    global setting

    time_start = time.time() # Запомним время страта

    #Получим по ссылки данные с ценами.
    price_list = requests.get("https://api.huobi.pro/market/tickers").json() # Получим ответ в виде JSON формата
    
    price = []
    # Переберём в цикле все торговые пары
    for symbol in price_list['data']:
        price.append([symbol['symbol'],symbol['close']])
    
    save_price(price,3)
    # Сообщим о проделанной работе
    frame['Huobi']['txt_Job'].configure(text=f"Загрузил за {round(time.time()-time_start,3)} сек.")
    print(f"Загрузка Huobi за {round(time.time()-time_start,3)} сек.")

# Цикл запуска загрузки Huobi
def while_Huobi():
    global setting, RunLoad

    start_time = round(time.time())-setting["refreshTime"]

    birza = "Huobi"

    frame[birza]['txt_Job'].configure(text="Запускаю")

    #Цикл работает, пока нужно загружать цены
    while RunLoad[birza]["auto_start"]:
        # Расчитаем время до запуска
        timer = start_time+setting["refreshTime"] - round(time.time())

        if timer <= 0:# Пора запускать
            frame[birza]['txt_time'].configure(text=f"{timer}")
            load_Huobi() # Загрузим цены
            RunLoad[birza]["count_load"] += 1
            frame[birza]['count_load'].configure(text=str(RunLoad[birza]["count_load"]))
            start_time = round(time.time()) # Сбросим время
        else: # Ждем ещё секунду
            time.sleep(1)
            frame[birza]['txt_time'].configure(text=f"{timer}") # Выведем таймер на экран

    # Если остановили цикл, то надо подчистить текст.
    frame[birza]['txt_Job'].configure(text="")
    frame[birza]['txt_time'].configure(text="")

# Загрузка KuCoin
def load_KuCoin():

    time_start = time.time() # Запомним время страта

    #Получим по ссылки данные с ценами.
    price_list = requests.get("https://api.kucoin.com/api/v1/market/allTickers").json() # Получим ответ в виде JSON формата

    price = []
    # Переберём в цикле все торговые пары
    for symbol in price_list['data']['ticker']:
        price.append([symbol['symbol'],symbol['last']])
        
    save_price(price,4)
    # Сообщим о проделанной работе
    frame['KuCoin']['txt_Job'].configure(text=f"Загрузил за {round(time.time()-time_start,3)} сек.")
    print(f"Загрузка KuCoin за {round(time.time()-time_start,3)} сек.")

# Цикл запуска загрузки KuCoin
def while_KuCoin():
    global setting, RunLoad

    start_time = round(time.time())-setting["refreshTime"]

    birza = "KuCoin"

    frame[birza]['txt_Job'].configure(text="Запускаю")

    #Цикл работает, пока нужно загружать цены
    while RunLoad[birza]["auto_start"]:
        # Расчитаем время до запуска
        timer = start_time+setting["refreshTime"] - round(time.time())

        if timer <= 0:# Пора запускать
            frame[birza]['txt_time'].configure(text=f"{timer}")
            load_KuCoin() # Загрузим цены
            RunLoad[birza]["count_load"] += 1
            frame[birza]['count_load'].configure(text=str(RunLoad[birza]["count_load"]))
            start_time = round(time.time()) # Сбросим время
        else: # Ждем ещё секунду
            time.sleep(1)
            frame[birza]['txt_time'].configure(text=f"{timer}") # Выведем таймер на экран

    # Если остановили цикл, то надо подчистить текст.
    frame[birza]['txt_Job'].configure(text="")
    frame[birza]['txt_time'].configure(text="")

# Запустим нужную биржу в новый поток.
def start_while(birza : string):
    global threading_Job

    # Узнаем какую  биржу нужно запустить
    match birza:
        case 'Binance':
            threading_Job[birza] = threading.Thread(target = while_Binance)
        case 'Gate':
            threading_Job[birza] = threading.Thread(target = while_Gate)
        case 'Huobi':
            threading_Job[birza] = threading.Thread(target = while_Huobi)
        case 'KuCoin':
            threading_Job[birza] = threading.Thread(target = while_KuCoin)

    threading_Job[birza].start() # Запустим процесс в работу

# Смена работы загрузки биржи.
# Если работало, то остановим
# Если не работало, то запустим
def start(birza:string):
    global RunLoad, threading_Job
  
    # При получении биржи, меняем статус.
    if RunLoad[birza]["auto_start"]:
        RunLoad[birza]["auto_start"] = False
    else:
        RunLoad[birza]["auto_start"] = True

    # Найдем наш поток, если не работает, то запустим.
    if RunLoad[birza]["auto_start"]:
        if birza in threading_Job:
            if threading_Job[birza].is_alive(): # ещё работает
                print(f"Поток биржи {birza} ещё работает.")
            else: # Потока нет, надо запустить
                start_while(birza)
        else: # Потока для биржи ещё не создавали
            start_while(birza)

#Выполним проверку, что нужно запусти при запуске программы
def start_Onload():
    global RunLoad

    # Подождём пару секунд, пока форма откроется.
    time.sleep(2)

    for index in RunLoad:
        if RunLoad[index]["auto_start"]:
            start_while(index)

# Остановим все загрузки
def stopAll():
    global RunLoad
    for index in RunLoad:
        RunLoad[index]  = False
    print("All Stop")

# Создаём форму для управления загрузкой
def windowGui():
    global RunLoad, frame, img, setting, CheckBoxArray
    
    window = tkinter.Tk()
    window.title('Загрузка цен криптовалют')
    window.iconbitmap("img/logo_32x32.ico")

    CheckBoxArray = {}

    # Картинки для отображения работы
    img["no"] = tkinter.PhotoImage(file="img/delete_16x16.png")
    img["ok"] = tkinter.PhotoImage(file="img/ok_16x16.png")

    # Добавим в массив иконки
    img["Hourglass"] = tkinter.PhotoImage(file=f"img/Hourglass_16x16.png")
    img["count_load"] = tkinter.PhotoImage(file=f"img/load_16x16.png")

    # Создаём новый фрейм
    frame["Header"] = {}
    frame["Header"][0] = tkinter.Frame(master=window)
    frame["Header"][0].pack(fill=tkinter.X, padx=3, ipady=2, ipadx=3)

    # Картинка работы
    frame["Header"]['img_birza'] = tkinter.Label(master=frame["Header"][0], text="", width=4).pack(side=tkinter.LEFT)

    # Название биржи
    frame["Header"]['txt_name'] = tkinter.Label(master=frame["Header"][0], text="Имя", width=7).pack(side=tkinter.LEFT)

    # Картинка работы
    frame["Header"]['img_Job'] = tkinter.Label(master=frame["Header"][0], text="Статус", width=6).pack(side=tkinter.LEFT)

    # текст при работе
    frame["Header"]['txt_Job'] = tkinter.Label(master=frame["Header"][0], text="Инфо", width=20).pack(side=tkinter.LEFT)

    # Таймер выполнения кода
    frame["Header"]['txt_time'] = tkinter.Label(master=frame["Header"][0], image=img["Hourglass"], width=10).pack(side=tkinter.LEFT)

    # Количество загрузок
    frame["Header"]['count_load'] = tkinter.Label(master=frame["Header"][0], image=img["count_load"], width=48).pack(side=tkinter.LEFT)

    # для каждой биржи нужно создать строку для управления запуском.
    for index in RunLoad:

        # Добавим в массив иконок биржу
        img[index] = tkinter.PhotoImage(file=f"img/{index}_16x16.png")

        # Каждый раз создаём новый фрейм
        frame[index] = {}
        frame[index][0] = tkinter.Frame(master=window)
        frame[index][0].pack(fill=tkinter.X, padx=3, ipady=2, ipadx=3)

        # Картинка работы
        frame[index]['img_birza'] = tkinter.Label(master=frame[index][0], image=img[index], width=20)
        frame[index]['img_birza'].pack(side=tkinter.LEFT)

        # Название биржи
        frame[index]['txt_name'] = tkinter.Label(master=frame[index][0], text=index, width=10)
        frame[index]['txt_name'].pack(side=tkinter.LEFT)

        # Картинка работы
        frame[index]['img_Job'] = tkinter.Label(master=frame[index][0], image=img["no"], width=20)
        frame[index]['img_Job'].pack(side=tkinter.LEFT)

        # текст при работе
        frame[index]['txt_Job'] = tkinter.Label(master=frame[index][0], text="", width=20)
        frame[index]['txt_Job'].pack(side=tkinter.LEFT)

        # Таймер выполнения кода
        frame[index]['txt_time'] = tkinter.Label(master=frame[index][0], text="", width=5)
        frame[index]['txt_time'].pack(side=tkinter.LEFT)

        # Количество загрузок
        frame[index]['count_load'] = tkinter.Label(master=frame[index][0], text="", width=3)
        frame[index]['count_load'].pack(side=tkinter.LEFT)

        # Кнопка запуска или остановки
        frame[index]['btn'] = tkinter.Button(master=frame[index][0], text="Запустить", width=10, command=partial(start , index))
        frame[index]['btn'].pack(side=tkinter.RIGHT)

    # Форма ЧекБоксов
    frame["Checkbox"] = {}
    frame["Checkbox"][0] = tkinter.LabelFrame(master=window, text="Настройки сохранения")
    frame["Checkbox"][0].pack(fill=tkinter.X, padx=3, ipady=2, ipadx=3)
    row = 0
    for chk in setting["Checkbox"]:
        CheckBoxArray[chk] = tkinter.BooleanVar()
        CheckBoxArray[chk].set(setting["Checkbox"][chk]["act"])
        frame["Checkbox"][chk] = tkinter.Checkbutton(master=frame["Checkbox"][0], text=setting["Checkbox"][chk]["name"], variable=CheckBoxArray[chk], command=CheckBox)
        frame["Checkbox"][chk].grid(row=row, column=0, sticky=tkinter.W)
        row += 1
    
    window.mainloop()

# Изменяем состояние чек боксов
def CheckBox():
    global setting, CheckBoxArray
    for chk in CheckBoxArray:
        setting["Checkbox"][chk]["act"] = CheckBoxArray[chk].get()


# Обновления формы каждую секунду.
def update_GUI():
    global RunLoad, frame, img

    # Подождём пару секунд, пока форма откроется.
    time.sleep(2)

    ok = True
    while ok==True:
        for index in RunLoad:
            try:
                if RunLoad[index]["auto_start"]:# Если должен работать
                    frame[index]['img_Job'].configure(image=img["ok"]) # Сменим картинку
                    frame[index]['btn'].configure(text="Остановить") # Сменим текст на кнопке
                else: # Если остановлен
                    frame[index]['img_Job'].configure(image=img["no"]) # Сменим картинку
                    frame[index]['btn'].configure(text="Запустить") # Сменим текст на кнопке
            except: # При ошибки доступа к форме, значит её закрыли. Можем завершить работу программы.
                ok = False
        # обновляем форму каждую секунду.
        time.sleep(1)

if __name__ == '__main__':
    
    # отдельный поток для обновления формы
    GUI = threading.Thread(target = update_GUI)
    GUI.start()

    # Запуск отдельного потока на проверку авто старта
    startAuto = threading.Thread(target = start_Onload)
    startAuto.start()

    # Создадим нашу форму
    windowGui()