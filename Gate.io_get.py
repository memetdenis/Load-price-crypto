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
    data = requests.get("https://api.gateio.ws/api/v4/spot/tickers/").json()
    time_load_json = round(time.time()-time_start,3)

    time_start = time.time()
    #В цикле переберём каждую валюту.
    for symbol in data:
        cursor.execute("INSERT INTO `price` (`symbol`, `price`) VALUES ('"+symbol["currency_pair"]+"', '"+symbol["last"]+"') ON DUPLICATE KEY UPDATE price = '"+symbol["last"]+"' , last_update = UNIX_TIMESTAMP();") #Записать изменение цены

    db.commit() #Зафиксировать транзакции
    print(f"Загрузка JSON за {time_load_json} сек, в базу за {round(time.time()-time_start,3)} сек.")

#Бесконечный цикл
time_old_load = 0
while 1==1:
    load_price()
    #time.sleep(10)