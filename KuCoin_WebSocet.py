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

    data = json.loads(message)
    if 'type' in data:
        if data['type']=='welcome':
            id_channel = data['id']
            ws.send(json.dumps({
                "id": data['id'],                     
                "type": "subscribe",
                "topic": "/market/ticker:all",
                "response": 'true'                              
            }))
        elif data['type']=='message':
            count_message += 1
            cursor.execute(f"INSERT INTO `price` (`symbol`, `price`) VALUES ('{data['subject']}', '{data['data']['price']}') ON DUPLICATE KEY UPDATE price = '{data['data']['price']}' , last_update = UNIX_TIMESTAMP();")  # Записать изменение цены
            #print(f"{data['subject']} = {data['data']['price']}")
        else:
            print(data)
    else:
        print(data)
    
    if (pingTime+pingInterval) <= round(time.time()):
        ws.send(json.dumps({
            "id":id_channel,
            "type":"ping"
        }))
        pingTime = round(time.time())
        print(f'За {round(time.time()-start_time,2)} секунд записали {count_message} сообщений')
        count_message = 0 # Обнулим счетчик сообщений
        start_time = time.time() # Сбросим счетчик времени

def on_open(ws):
    print("open")

#При закрытии подключения к бирже
def on_close(ws):
    print("### closed ###")

def on_error(ws, message):
    print(message)

def loadSetting():
    return requests.post('https://api.kucoin.com/api/v1/bullet-public').json()

settings = loadSetting()
print(settings['data']['instanceServers'][0]['pingInterval'])
pingInterval = ((settings['data']['instanceServers'][0]['pingInterval']/1000)/2)-1
pingTime = round(time.time())+5 # Первое сообщение на сервер отправим не менее чем через 5 секунд
id_channel = ''

ws = websocket.WebSocketApp(f"{settings['data']['instanceServers'][0]['endpoint']}?token={settings['data']['token']}",
                            on_message=on_message,
                            on_close=on_close,
                            on_error=on_error)

#ws.on_open=on_open
ws.run_forever()  # Set dispatcher to automatic reconnection
#print(settings)
#print(settings['data']['token'])
#print(settings['data']['instanceServers'][0]['endpoint'])
#print(settings['data']['instanceServers'][0]['pingInterval'])
#print(settings['data']['instanceServers'][0]['pingTimeout'])