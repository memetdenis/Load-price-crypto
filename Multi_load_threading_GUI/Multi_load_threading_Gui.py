import threading
import time
import MySQLdb
import requests
import tkinter
from functools import partial

# Массив настроек
setting = {
        "refreshTime":15, # Время повторной загрузки
        "host":"localhost", # Хост для MySQL
        "user":"root", # Логин MySQL
        "passwd":"", # Пароль MySQL
        "db":"price" # База MySQL
    }

# Массив всех наших бирж
# По умолчанию всё выключенно.
RunLoad = {
    "Binance": False,
    "Gate": False,
    "Huobi": False,
    "KuCoin": False
}

# Массив с нашими потоками
threading_Job = {} # Пока пустой

# Массив с нашими формами.
# Что бы не плодить переменные, пишем всё в массив.
frame = {}

#Подключение к базе данных
def connectDB():
    global setting
    return MySQLdb.connect(host=setting["host"], user=setting["user"], passwd=setting["passwd"], db=setting["db"])

# Функция загрузки цен с биржи Binance
def load_Binance():
    global frame
    time_start = time.time() # Запомним время страта

    # Подключимся к базе данных
    conn = connectDB()
    cursor = conn.cursor()

    #Получим по ссылки данные с ценами.
    price_list = requests.get("https://api.binance.com/api/v3/ticker/24hr").json() # Получим ответ в виде JSON формата

    # Если в сообщении есть код ошибки, то стоит прервать работу.
    if 'code' in price_list:
        print(f"Error code {price_list['code']} msg = {price_list['msg']}")
        time.sleep(10)
        return False

    # Переберём в цикле все торговые пары
    for symbol in price_list:
        try:
            if float(symbol['lastPrice']) > 0: # Проверим наличие цены
                cursor.execute(f"INSERT INTO `price` (`birza`, `symbol`, `price`) VALUES (1, '{symbol['symbol']}', '{symbol['lastPrice']}') ON DUPLICATE KEY UPDATE price = '{symbol['lastPrice']}' , last_update = UNIX_TIMESTAMP();") # Записать изменение цены
        except Exception as inst:
            print(inst) # Если ошибка доступа к результату
    conn.commit()
    conn.close()

    # Сообщим о проделанной работе
    frame['Binance']['txt_Job'].configure(text=f"Загрузил за {round(time.time()-time_start,3)} сек.")
    print(f"Загрузил Binance за {round(time.time()-time_start,3)} сек.")

def while_Binance():
    global setting, RunLoad

    start_time = round(time.time())

    birza = "Binance"

    frame[birza]['txt_Job'].configure(text="Запускаю")

    #Цикл работает, пока нужно загружать цены
    while RunLoad[birza]:
        # Расчитаем время до запуска
        timer = start_time+setting["refreshTime"] - round(time.time())

        if timer <= 0:# Пора запускать
            frame[birza]['txt_time'].configure(text=f"{timer}")
            load_Binance() # Загрузим цены
            start_time = round(time.time()) # Сбросим время
        else: # Ждем ещё секунду
            time.sleep(1)
            frame[birza]['txt_time'].configure(text=f"{timer}") # Выведем таймер на экран

    # Если остановили цикл, то надо подчистить текст.
    frame[birza]['txt_Job'].configure(text="")
    frame[birza]['txt_time'].configure(text="")
               
#Функция загрузки цен Gate
def load_Gate():
    
    time_start = time.time()

    # Подключимся к базе данных
    conn = connectDB()
    cursor = conn.cursor()

    #Получим данные в виде JSON
    data = requests.get("https://api.gateio.ws/api/v4/spot/tickers/").json()

    #В цикле переберём каждую валюту.
    for symbol in data:
        try:
            cursor.execute(f"INSERT INTO `price` (`birza`, `symbol`, `price`) VALUES (2, '{symbol['currency_pair']}', '{symbol['last']}') ON DUPLICATE KEY UPDATE price = '{symbol['last']}' , last_update = UNIX_TIMESTAMP();") # Записать изменение цены   
        except Exception as inst:
            print(inst) # Если ошибка доступа к результату
    conn.commit() # Зафиксировать транзакции
    conn.close()
    
    frame['Gate']['txt_Job'].configure(text=f"Загрузил за {round(time.time()-time_start,3)} сек.")
    print(f"Загрузка Gate за {round(time.time()-time_start,3)} сек.")

# Цикл запуска загрузки цены
def while_Gate():
    global setting, RunLoad

    # Запомним 
    start_time = round(time.time())

    # Название биржи в масииве. 
    # Для доступа к форме и состоянию загрузки
    birza = "Gate" 

    frame[birza]['txt_Job'].configure(text="Запускаю")

    #Цикл работает, пока нужно загружать цены
    while RunLoad[birza]:
        # Расчитаем время до запуска
        timer = start_time+setting["refreshTime"] - round(time.time())

        if timer <= 0:# Пора запускать
            frame[birza]['txt_time'].configure(text=f"{timer}")
            load_Gate() # Загрузим цены
            start_time = round(time.time()) # Сбросим время
        else: # Ждем ещё секунду
            time.sleep(1)
            frame[birza]['txt_time'].configure(text=f"{timer}") # Выведем таймер на экран

    # Если остановили цикл, то надо подчистить текст.
    frame[birza]['txt_Job'].configure(text="")
    frame[birza]['txt_time'].configure(text="")

# Функция загрузки цен с биржи GATE
def load_Huobi():

    time_start = time.time() # Запомним время страта

    # Подключимся к базе данных
    conn = connectDB()
    cursor = conn.cursor()

    #Получим по ссылки данные с ценами.
    price_list = requests.get("https://api.huobi.pro/market/tickers").json() # Получим ответ в виде JSON формата

    count_symbol = 0 # Счетчик торговых пар с ценами
    # Переберём в цикле все торговые пары
    for symbol in price_list['data']:
        count_symbol += 1 # Увеличим счетчик торговых пар.
        cursor.execute(f"INSERT INTO `price` (`birza`, `symbol`, `price`) VALUES (3, '{symbol['symbol']}', '{symbol['close']}') ON DUPLICATE KEY UPDATE price = '{symbol['close']}' , last_update = UNIX_TIMESTAMP();") # Записать изменение цены
        
    conn.commit() # После всех записей, зафиксируем записаное.
    conn.close()
    
    # Сообщим о проделанной работе
    frame['Huobi']['txt_Job'].configure(text=f"Загрузил за {round(time.time()-time_start,3)} сек.")
    print(f"Загрузка Huobi за {round(time.time()-time_start,3)} сек.")

# Сделаем бесконечный цикл загрузки цен.
def while_Huobi():
    global setting, RunLoad

    start_time = round(time.time())

    birza = "Huobi"

    frame[birza]['txt_Job'].configure(text="Запускаю")

    #Цикл работает, пока нужно загружать цены
    while RunLoad[birza]:
        # Расчитаем время до запуска
        timer = start_time+setting["refreshTime"] - round(time.time())

        if timer <= 0:# Пора запускать
            frame[birza]['txt_time'].configure(text=f"{timer}")
            load_Huobi() # Загрузим цены
            start_time = round(time.time()) # Сбросим время
        else: # Ждем ещё секунду
            time.sleep(1)
            frame[birza]['txt_time'].configure(text=f"{timer}") # Выведем таймер на экран

    # Если остановили цикл, то надо подчистить текст.
    frame[birza]['txt_Job'].configure(text="")
    frame[birza]['txt_time'].configure(text="")

# Функция загрузки цен с биржи
def load_KuCoin():

    time_start = time.time() # Запомним время страта

    # Подключимся к базе данных
    conn = connectDB()
    cursor = conn.cursor()

    #Получим по ссылки данные с ценами.
    price_list = requests.get("https://api.kucoin.com/api/v1/market/allTickers").json() # Получим ответ в виде JSON формата

    count_symbol = 0 # Счетчик торговых пар с ценами
    # Переберём в цикле все торговые пары
    for symbol in price_list['data']['ticker']:
        count_symbol += 1 # Увеличим счетчик торговых пар.
        cursor.execute(f"INSERT INTO `price` (`birza`, `symbol`, `price`) VALUES ( 4, '{symbol['symbol']}', '{symbol['last']}') ON DUPLICATE KEY UPDATE price = '{symbol['last']}' , last_update = UNIX_TIMESTAMP();") # Записать изменение цены
        
    conn.commit() # После всех записей, зафиксируем записаное.
    conn.close()
    # Сообщим о проделанной работе
    frame['KuCoin']['txt_Job'].configure(text=f"Загрузил за {round(time.time()-time_start,3)} сек.")
    print(f"Загрузка KuCoin за {round(time.time()-time_start,3)} сек.")

# Сделаем бесконечный цикл загрузки цен.
def while_KuCoin():
    global setting, RunLoad

    start_time = round(time.time())

    birza = "KuCoin"

    frame[birza]['txt_Job'].configure(text="Запускаю")

    #Цикл работает, пока нужно загружать цены
    while RunLoad[birza]:
        # Расчитаем время до запуска
        timer = start_time+setting["refreshTime"] - round(time.time())

        if timer <= 0:# Пора запускать
            frame[birza]['txt_time'].configure(text=f"{timer}")
            load_KuCoin() # Загрузим цены
            start_time = round(time.time()) # Сбросим время
        else: # Ждем ещё секунду
            time.sleep(1)
            frame[birza]['txt_time'].configure(text=f"{timer}") # Выведем таймер на экран

    # Если остановили цикл, то надо подчистить текст.
    frame[birza]['txt_Job'].configure(text="")
    frame[birza]['txt_time'].configure(text="")

# Запустим нужную биржу в новый поток.
def start_while(birza):
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
def start(birza):
    global RunLoad, threading_Job
  
    # При получении биржи, меняем статус.
    if RunLoad[birza]:
        RunLoad[birza] = False
    else:
        RunLoad[birza] = True

    # Найдем наш поток, если не работает, то запустим.
    if RunLoad[birza]:
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
        if RunLoad[index]:
            start_while(index)

# Остановим все загрузки
def stopAll():
    global RunLoad
    for index in RunLoad:
        RunLoad[index]  = False
    print("All Stop")

# Создаём форму для управления загрузкой
def windowGui():
    global RunLoad, frame, imgNo, imgOk
    
    window = tkinter.Tk()

    # Картинки для отображения работы
    imgNo = tkinter.PhotoImage(file="img/delete_16x16.png")
    imgOk = tkinter.PhotoImage(file="img/ok_16x16.png")

    # для каждой биржи нужно создать строку для управления запуском.
    for index in RunLoad:
        # Каждый раз создаём новый фрейм
        frame[index] = {}
        frame[index][0] = tkinter.Frame(master=window)
        frame[index][0].pack(fill=tkinter.X)

        # Название биржи
        frame[index]['txt_name'] = tkinter.Label(master=frame[index][0], text=index, width=10)
        frame[index]['txt_name'].pack(side=tkinter.LEFT)

        # Картинка работы
        frame[index]['img_Job'] = tkinter.Label(master=frame[index][0], image=imgNo, width=20)
        frame[index]['img_Job'].pack(side=tkinter.LEFT)

        # текст при работе
        frame[index]['txt_Job'] = tkinter.Label(master=frame[index][0], text="", width=20)
        frame[index]['txt_Job'].pack(side=tkinter.LEFT)

        # Таймер выполнения кода
        frame[index]['txt_time'] = tkinter.Label(master=frame[index][0], text="", width=5)
        frame[index]['txt_time'].pack(side=tkinter.LEFT)

        # Кнопка запуска или остановки
        frame[index]['btn'] = tkinter.Button(master=frame[index][0], text="Запустить", width=10, command=partial(start , index))
        frame[index]['btn'].pack(side=tkinter.RIGHT)

    window.mainloop()

# Обновления формы каждую секунду.
def update_GUI():
    global RunLoad, frame, imgNo, imgOk

    # Подождём пару секунд, пока форма откроется.
    time.sleep(2)

    ok = True
    while ok==True:
        for index in RunLoad:
            try:
                if RunLoad[index]:# Если должен работать
                    frame[index]['img_Job'].configure(image=imgOk) # Сменим картинку
                    frame[index]['btn'].configure(text="Остановить") # Сменим текст на кнопке
                else: # Если остановлен
                    frame[index]['img_Job'].configure(image=imgNo) # Сменим картинку
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