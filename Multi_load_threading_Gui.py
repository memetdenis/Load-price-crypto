import threading
import time
import MySQLdb
import requests
import tkinter
from functools import partial

# Массив настроек
setting = {
        "refreshTime":10 # Время повторной загрузки
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
    return MySQLdb.connect(host="localhost", user="root", passwd="", db="price")

# Функция загрузки цен с биржи Binance
def load_Binance():
    global RunLoad, frame
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

    return RunLoad["Binance"] # Вернём глобальную переменную биржи, вдруг мы решили остановить её.

def while_Binance():
    global setting

    # При старте цикл работает 
    run=True 

    #Бесконечный цикл
    while run==True:
        run = load_Binance()
        # Если остановили цикл, то надо изменить текст на точки. Что бы было понятно, что цикл больше не работает.
        if run==False:
            frame['Binance']['txt_Job'].configure(text="....") 
         
        time.sleep(setting["refreshTime"])

#Функция загрузки цен
def load_Gate():
    global RunLoad
    
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

    return RunLoad["Gate"]

def while_Gate():
    global setting

    # При старте цикл работает 
    run=True 

    #Бесконечный цикл
    while run==True:
        run = load_Gate()
        if run==False:
            frame['Gate']['txt_Job'].configure(text="....")  
        time.sleep(setting["refreshTime"])


# Функция загрузки цен с биржи GATE
def load_Huobi():
    global RunLoad
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

    return RunLoad["Huobi"]

# Сделаем бесконечный цикл загрузки цен.
def while_Huobi():
    global setting

    # При старте цикл работает 
    run=True 

    #Бесконечный цикл
    while run == True:
        run = load_Huobi()
        if run==False:
            frame['Huobi']['txt_Job'].configure(text="....")  
        time.sleep(setting["refreshTime"])

# Функция загрузки цен с биржи
def load_KuCoin():
    global RunLoad
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

    return RunLoad["KuCoin"]

# Сделаем бесконечный цикл загрузки цен.
def while_KuCoin():
    global setting

    # При старте цикл работает 
    run=True 

    #Бесконечный цикл
    while run == True:
        run = load_KuCoin()
        if run==False:
            frame['KuCoin']['txt_Job'].configure(text="....")           
        time.sleep(setting["refreshTime"])

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

    

#Запуск разрешенных бирж для загрузки
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
            if threading_Job[birza].is_alive():
                print(f"Поток биржи {birza} ещё работает.")
            else:
                start_while(birza)
        else:
            start_while(birza)

    return True

# Остановим все загрузки
def stopAll():
    global RunLoad
    RunLoad["Binance"]  = False
    RunLoad["Gate"]     = False
    RunLoad["Huobi"]    = False
    RunLoad["KuCoin"]   = False
    print("All Stop")

def windowGui():
    global RunLoad, frame, imgNo, imgOk
    
    window = tkinter.Tk()

    imgNo = tkinter.PhotoImage(file="img/delete_16x16.png")
    imgOk = tkinter.PhotoImage(file="img/ok_16x16.png")

    for index in RunLoad:
        frame[index] = {}
        frame[index][0] = tkinter.Frame(master=window)
        frame[index][0].pack(fill=tkinter.X)

        frame[index]['txt_name'] = tkinter.Label(master=frame[index][0], text=index, width=10)
        frame[index]['txt_name'].pack(side=tkinter.LEFT)


        frame[index]['img_Job'] = tkinter.Label(master=frame[index][0], image=imgNo, width=20)
        frame[index]['img_Job'].pack(side=tkinter.LEFT)

        frame[index]['txt_Job'] = tkinter.Label(master=frame[index][0], text="Остановлен...", width=20)
        frame[index]['txt_Job'].pack(side=tkinter.LEFT)

        frame[index]['btn'] = tkinter.Button(master=frame[index][0], text="Запустить", width=10, command=partial(start , index))
        frame[index]['btn'].pack(side=tkinter.RIGHT)

    window.mainloop()

def update_txt_GUI():
    global RunLoad, frame, imgNo, imgOk

    # Подождём пару секунд, пока форма откроется.
    time.sleep(2)

    ok = True
    while ok==True:
        for index in RunLoad:
            try:
                if RunLoad[index]:# Если должен работать
                    frame[index]['img_Job'].configure(image=imgOk)
                    frame[index]['btn'].configure(text="Остановить")
                else: # Если остановлен
                    frame[index]['img_Job'].configure(image=imgNo)
                    frame[index]['btn'].configure(text="Запустить")
            except: # При ошибки доступа к форме, значит её закрыли. Можем завершить работу программы.
                ok = False
        # обновляем форму каждую секунду.
        time.sleep(1)

if __name__ == '__main__':

    GUI = threading.Thread(target = update_txt_GUI)
    GUI.start()

    windowGui()