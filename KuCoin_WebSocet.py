import time
import json
import websocket
import MySQLdb
import requests

#Подключимся к базе данных
db=MySQLdb.connect(host="localhost", user="root", passwd="", db="price")
cursor = db.cursor()

count_message = 0 # Количество сообщений
start_time = time.time() # Запомним время старта

def on_message(ws, message):
    global pingInterval, pingTime, id_channel, count_message, start_time

    #Преобразуем сообщение в массив
    data = json.loads(message)

    # Проверим наличие ключа 'type'
    if 'type' in data:
        # Если ключ 'type' = 'welcome' , значит соединение установлено.
        # Нужно отправить запрос на подписку.
        if data['type']=='welcome':
            id_channel = data['id']
            ws.send(json.dumps({
                "id": data['id'],                     
                "type": "subscribe",
                "topic": "/market/ticker:all",
                "response": 'true'                              
            }))
        # Если ключ 'type' = 'message' , значит получилди сообщение о ордере. ТОрговая пара и цена
        elif data['type']=='message':
            count_message += 1
            cursor.execute(f"INSERT INTO `price` (`symbol`, `price`) VALUES ('{data['subject']}', '{data['data']['price']}') ON DUPLICATE KEY UPDATE price = '{data['data']['price']}' , last_update = UNIX_TIMESTAMP();")  # Записать изменение цены
        # Неизвестное сообщение с ключом 'type'
        else:
            print(data)
    # Если не поняли что получили от сервера
    else:
        print(data)
    
    # Наш счетчик сообщений за промежуток времени и
    # общение с сервером для поддержки соединения
    if (pingTime+pingInterval) <= round(time.time()):
        ws.send(json.dumps({
            "id":id_channel,
            "type":"ping"
        }))
        print(f'За {round(time.time()-start_time,2)} секунд записали {count_message} сообщений')

        pingTime = round(time.time()) # Запомним новое время после сообщения
        count_message = 0 # Обнулим счетчик сообщений
        start_time = time.time() # Сбросим счетчик времени

# При закрытии подключения к бирже
def on_close(ws):
    print("### closed ###")

# При ошибки в соединение
def on_error(ws, message):
    print(message)

# Получим настройки от сервера
def loadSetting():
    return requests.post('https://api.kucoin.com/api/v1/bullet-public').json()

# Запомним настройки
settings = loadSetting() 

# Запомним интервал для поддержки соединения
# Берём нужный интервал, делим на 2(что бы отправлять в два раза чаще) и вычтем одну секунду(что бы точно успеть в интервал отправить 2 сообщения)
pingInterval = round((settings['data']['instanceServers'][0]['pingInterval']/1000)/2)-1

# Запомним время старта подключения
pingTime = round(time.time())

# Запомним id канала, которое открываем. 
# Его мы узнаем после подписки на канал
id_channel = ''

ws = websocket.WebSocketApp(f"{settings['data']['instanceServers'][0]['endpoint']}?token={settings['data']['token']}",
                            on_message=on_message,
                            on_close=on_close,
                            on_error=on_error)

ws.run_forever()  # Set dispatcher to automatic reconnection
#print(settings)
#print(settings['data']['token']) - Токен для подключения выданные сервером при получении настроек
#print(settings['data']['instanceServers'][0]['endpoint']) - Адрес подключения к WebSocket
#print(settings['data']['instanceServers'][0]['pingInterval']) - интервал сообщений ping, для поддержки соединения
#print(settings['data']['instanceServers'][0]['pingTimeout']) - Максимальное време ответа на сообщение 'ping' от сервера 