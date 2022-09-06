import time
import json
import websocket
import MySQLdb
import requests
import gzip


#Подключимся к базе данных
db=MySQLdb.connect(host="localhost", user="root", passwd="", db="price")
cursor = db.cursor()

# Счетчик количества сообщений
count_message = 0

# Запомним время
time_start = time.time()

#При получении сообщения
def on_message(ws, message):
    global count_message, time_start

    #Распакуем полученное сообщение.
    data = gzip.decompress(message)

    #Преобразуем в массив
    array_message = json.loads(data)
   
    #Если есть поле ping , то нужно ответить серверу pong
    if 'ping' in array_message:
        ws.send(json.dumps({"pong": array_message['ping']})) 
        #print(f"ping = {array_message['ping']}")
    #Если есть поле ch то значит это сообщение о курсе торговой пары
    elif 'ch' in array_message:
        #Обрежем наименование торговой пары от лишнего 'market.' и '.detail'
        name = array_message['ch'].replace('market.', '').replace('.detail', '')
        #Запишем в базу данных
        cursor.execute(f"INSERT INTO `price` (`symbol`, `price`) VALUES ('{name}', '{array_message['tick']['close']}') ON DUPLICATE KEY UPDATE price = '{array_message['tick']['close']}' , last_update = UNIX_TIMESTAMP();")  
        db.commit()# Зафиксируем записанное
        count_message +=1

    # Посмотрим, нужно ли сообщить мне о количестве сообщений.
    if(round(time_start)+9 < round(time.time())):
        print(f"Получил {count_message} сообщений за {round(time.time() - time_start, 1)} сек.")
        count_message = 0 # Сбросим счетчик сообщений
        time_start = time.time() # Запомним новое время.
        
#При закрытии подключения к бирже
def on_close(ws):
    print("### closed ###")

def on_error(ws, message):
    print(message)

# При открытии подключения
def on_open(ws):
    
    # Загурзим все торговые пары в массив
    response = requests.get("https://api.huobi.pro/v2/settings/common/symbols")
    symbols_list = response.json()

    count_symbol = 0
    # Каждую торговую пару нужно запросить на сервере.
    for symbol in symbols_list['data']:
        # Проверим торгуется ли пара
        if symbol['state']=='online':
            count_symbol +=1 # Увеличим счетчик торговых пар
            # Подпишемся на поток.
            ws.send(json.dumps({"sub": f"market.{symbol['sc']}.detail"}))
    # Сообщим о количестве найденных торговых пар.       
    print(f"Нашли для загрузки {count_symbol} символов на бирже Gate")
    
#Создадим подлючение к бирже через WebSocket
ws = websocket.WebSocketApp("wss://api.huobi.pro/ws",
                            on_message=on_message,
                            on_close=on_close,
                            on_error=on_error)
ws.on_open=on_open
ws.run_forever()  # Set dispatcher to automatic reconnection