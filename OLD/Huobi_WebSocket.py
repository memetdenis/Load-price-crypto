import time
import json
import websocket
import MySQLdb
import requests
import gzip

#Подключимся к базе данных
db=MySQLdb.connect(host="localhost", user="root", passwd="", db="price")
cursor = db.cursor()

count_subbed = 0 # Количество подписок
count_message = 0 # Количество сообщений
start_time = time.time() # Запомним время старта

#При получении сообщения
def on_message(ws, message):
    global cursor, db, count_subbed, count_message, start_time  #Доступ к глобальной переменной

    # Распакуем сообщение из архива и выгрузим его в массив.
    data = json.loads(gzip.decompress(message))
    
    if 'ping' in data:
        #Отправить pong
        ws.send(json.dumps({
            "pong": data['ping']
        })) 
    elif 'ch' in data:
        symbol = data['ch'].replace('market.','').replace('.ticker','') # Удалим лишнее в сообщении о торговой паре
        cursor.execute(f"INSERT INTO `price` (`symbol`, `price`) VALUES ('{symbol}', '{data['tick']['lastPrice']}') ON DUPLICATE KEY UPDATE price = '{data['tick']['lastPrice']}' , last_update = UNIX_TIMESTAMP();") #Записать изменение цены
        db.commit()
        count_message += 1
    elif 'subbed' in data: 
        count_subbed += 1
        #print(f"Подписались на канал {data['subbed']}. Всего подписок {count_subbed}")
    else:
        print(data) # Неизвестный ответ от сервера

    # Если с начала замера прошло больше 3 сек, то выведем сообщение о количестве полученный за это время сообщений от сервера
    if round(start_time)+10 <= round(time.time()):
        print(f'За {round(time.time()-start_time,2)} секунд записали {count_message} сообщений')
        count_message = 0 # Обнулим счетчик сообщений
        start_time = time.time() # Сбросим счетчик времени

#При закрытии подключения к бирже
def on_close(ws):
    print("### closed ###")

def on_error(ws, message):
    print(message)

#При открытии подключения
def on_open(ws):
    
    #Загурзим все торговые пары в массив
    symbols_list = requests.get("https://api.huobi.pro/v1/common/symbols").json()

    count_symbol = 0 # Количество торговых пар
    for symbol in symbols_list['data']:
        if symbol['state']=='online': #Если пара торгуется
            count_symbol +=1 # Добавим счетчик количества пар
            #Отправим подписку на изменения цены
            ws.send(json.dumps({"sub": f"market.{symbol['symbol']}.ticker"}))
  
    print(f"Нашли для загрузки {count_symbol} символов на бирже Huobi")
    
ws = websocket.WebSocketApp("wss://api.huobi.pro/ws",
                            on_message=on_message,
                            on_close=on_close,
                            on_error=on_error)
ws.on_open=on_open
ws.run_forever()  # Set dispatcher to automatic reconnection