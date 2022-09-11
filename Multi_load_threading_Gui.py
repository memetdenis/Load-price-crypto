import threading
import time
import MySQLdb
import requests

RunLoad = {
    "Binance": True,
    "Gate": True,
    "Huobi": True,
    "KuCoin": True
}

#Подключение к базе данных
def connectDB():
    return MySQLdb.connect(host="localhost", user="root", passwd="", db="price")

# Функция загрузки цен с биржи Binance
def load_Binance():
    global RunLoad
    time_start = time.time() # Запомним время страта

    # Подключимся к базе данных
    conn = connectDB()
    cursor = conn.cursor()

    #Получим по ссылки данные с ценами.
    price_list = requests.get("https://api.binance.com/api/v3/ticker/24hr").json() # Получим ответ в виде JSON формата

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
    print(f"Загрузил Binance за {round(time.time()-time_start,3)} сек.")

    return RunLoad["Binance"]

def while_binance():
    run=True
    #Бесконечный цикл
    while run==True:
        run = load_Binance()
        time.sleep(10)

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
    print(f"Загрузка Gate за {round(time.time()-time_start,3)} сек.")

    return RunLoad["Gate"]

def while_Gate():
    run = True

    #Бесконечный цикл
    while run==True:
        run = load_Gate()
        time.sleep(10)


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
    print(f"Загрузка Huobi за {round(time.time()-time_start,3)} сек.")

    return RunLoad["Huobi"]

# Сделаем бесконечный цикл загрузки цен.
def while_Huobi():
    run = True

    #Бесконечный цикл
    while run == True:
        run = load_Huobi()
        time.sleep(10)

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
    print(f"Загрузка KuCoin за {round(time.time()-time_start,3)} сек.")

    return RunLoad["KuCoin"]

# Сделаем бесконечный цикл загрузки цен.
def while_KuCoin():
    run = True
    while run == True:
        run = load_KuCoin()
        time.sleep(10)

#Запуск разрешенных бирж для загрузки
def start():
    global RunLoad

    if RunLoad["Binance"]:
        binance = threading.Thread(target = while_binance)
        binance.start()

    if RunLoad["Gate"]:
        Gate = threading.Thread(target = while_Gate)
        Gate.start()

    if RunLoad["Huobi"]:
        Huobi = threading.Thread(target = while_Huobi)
        Huobi.start()

    if RunLoad["KuCoin"]:
        KuCoin = threading.Thread(target = while_KuCoin)
        KuCoin.start()

# Остановим все загрузки
def stopAll():
    global RunLoad
    RunLoad["Binance"]  = False
    RunLoad["Gate"]     = False
    RunLoad["Huobi"]    = False
    RunLoad["KuCoin"]   = False
    print("All Stop")

if __name__ == '__main__':
    start()
    time.sleep(30)
    stopAll()