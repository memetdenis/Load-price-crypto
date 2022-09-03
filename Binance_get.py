import time
import requests
import json
import MySQLdb

#Подключимся к базе данных
db=MySQLdb.connect(host="localhost", user="root", passwd="", db="price")
cursor = db.cursor()

#Функция загрузки цен
def load_price():
    
    time_start = time.time()
    
    #Получим данные в виде JSON
    data = requests.get("https://api.binance.com/api/v3/ticker/24hr").json()

    #В цикле переберём каждую валюту.
    for symbol in data:
        cursor.execute("INSERT INTO `price` (`symbol`, `price`) VALUES ('"+symbol["symbol"]+"', '"+symbol["lastPrice"]+"') ON DUPLICATE KEY UPDATE price = '"+symbol["lastPrice"]+"' , last_update = UNIX_TIMESTAMP();") #Записать изменение цены

    db.commit() #Зафиксировать транзакции
    print(f"Загрузка за {round(time.time()-time_start,3)} сек.")

#Бесконечный цикл
while 1==1:
    load_price()
    #time.sleep(1)