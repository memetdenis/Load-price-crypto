import time
import json
import websocket
import MySQLdb
import requests

#Подключимся к базе данных
db=MySQLdb.connect(host="localhost", user="root", passwd="", db="price")
cursor = db.cursor()

#При получении сообщения
def on_message(ws, message):
    global cursor, db #Доступ к глобальной переменной

    data = json.loads(message) #Преобразуем в массив
    try:
        #Попробуем вывести результат сообщения
        cursor.execute("INSERT INTO `price` (`symbol`, `price`) VALUES ('"+data['result']['currency_pair']+"', '"+data['result']['last']+"') ON DUPLICATE KEY UPDATE price = '"+data['result']['last']+"' , last_update = UNIX_TIMESTAMP();") #Записать изменение цены
        db.commit()
        #print(f"{data['result']['currency_pair']} = {data['result']['last']}")
    except:
        #Если ошибка доступа к результату
        print(message)

#При закрытии подключения к бирже
def on_close(ws):
    print("### closed ###")

def on_error(ws, message):
    print(message)

#При открытии подключения
def on_open(ws):
    #Загурзим все торговые пары в массив
    response = requests.get("https://api.gateio.ws/api/v4/spot/currency_pairs")
    symbols_list = json.loads(response.text)

    count_symbol = 0
    symbol_load = []
    for symbol in symbols_list:
        if symbol['trade_status']=='tradable' and symbol['id'].find('USDT') != -1:

            symbol_load.append(symbol['id'])
            count_symbol +=1
            if len(symbol_load)>20:
                #Отправим подписку на изменения цены BTC_USDT
                ws.send(json.dumps({
                    "time": int(time.time()),
                    "channel": "spot.tickers",
                    "event": "subscribe",  # "unsubscribe" for unsubscription
                    "payload": symbol_load
                }))   
                symbol_load = []  
    #Проверим, остались ли тут пары для загрузки
    if len(symbol_load)>0:  
        #Отправим подписку на изменения цены BTC_USDT
        ws.send(json.dumps({
            "time": int(time.time()),
            "channel": "spot.tickers",
            "event": "subscribe",  # "unsubscribe" for unsubscription
            "payload": symbol_load
        })) 
           
    print(f"Нашли для загрузки {count_symbol} символов на бирже Gate")

    


ws = websocket.WebSocketApp("wss://api.gateio.ws/ws/v4/",
                            on_message=on_message,
                            on_close=on_close,
                            on_error=on_error)
ws.on_open=on_open
ws.run_forever()  # Set dispatcher to automatic reconnection