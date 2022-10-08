import time
import MySQLdb
import requests

# Подключимся к базе данных
db=MySQLdb.connect(host="localhost", user="root", passwd="", db="price")
cursor = db.cursor()

# Функция загрузки цен с биржи GATE
def load_Huobi():
    time_start = time.time() # Запомним время страта

    #Получим по ссылки данные с ценами.
    price_list = requests.get("https://api.huobi.pro/market/tickers").json() # Получим ответ в виде JSON формата

    count_symbol = 0 # Счетчик торговых пар с ценами
    # Переберём в цикле все торговые пары
    for symbol in price_list['data']:
        count_symbol += 1 # Увеличим счетчик торговых пар.
        cursor.execute(f"INSERT INTO `price` (`symbol`, `price`) VALUES ('{symbol['symbol']}', '{symbol['close']}') ON DUPLICATE KEY UPDATE price = '{symbol['close']}' , last_update = UNIX_TIMESTAMP();") # Записать изменение цены
        
    db.commit() # После всех записей, зафиксируем записаное.

    # Сообщим о проделанной работе
    print(f"Загрузил {count_symbol} торговых пар за {round(time.time()-time_start,3)} сек.")

# Сделаем бесконечный цикл загрузки цен.
while 1==1:
    load_Huobi()