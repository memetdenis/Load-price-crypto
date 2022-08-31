import websocket
import json
import time
import MySQLdb
import requests

db=MySQLdb.connect(host="localhost", user="root", passwd="", db="price")
cursor = db.cursor()

header = {
    'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:82.0) Gecko/20100101 Firefox/82.0'
}

def on_message(ws, message):
    global cursor, db
    try:
        data = json.loads(message)
        cursor.execute("INSERT INTO `price` (`exchange`, `symbol`, `price`) VALUES ( '2', '"+data['result']['currency_pair']+"', '"+data['result']['last']+"') ON DUPLICATE KEY UPDATE price = '"+data['result']['last']+"' , last_modified = UNIX_TIMESTAMP();") #Записать изменение цены
        #print(f"{data['result']['currency_pair']} = {data['result']['last']}")
        db.commit() #Зафиксировать транзакции
        #print("Got msg: ", message)
        pass
    except:
        print(message)

def on_error(ws, error):
    print("received error as {}".format(error))

def on_close(ws):
    print("Connection closed")

def on_open(ws):
    response = requests.get('https://api.gateio.ws/api/v4/spot/currency_pairs/')
    symbol_list = json.loads(response.text)
    symbol_list_loads = []
    symbol_list_loads2 = []
    counter_symbol = 30
    count_symbol = 0
    reset_count = 0
    for symbol in symbol_list:
        if symbol['trade_status']=="tradable":
            count_symbol +=1
            if reset_count<120:
                if counter_symbol>0:
                    symbol_list_loads.append(symbol['id'])
                    counter_symbol -= 1
                else:
                    #print(f'Найдено {len(symbol_list_loads)} торговых пар на Gate')
                    ws.send(json.dumps({
                        "time": int(time.time()),
                        "channel": "spot.tickers",
                        "event": "subscribe",  # "unsubscribe" for unsubscription
                        "payload": symbol_list_loads
                    }))
                    symbol_list_loads = []
                    counter_symbol = 30
                    reset_count += 1


    #["BTC_USDT","ETH_USDT","GT_USDT"]
    print(f'Найдено {count_symbol} торговых пар на Gate')
    #print("Open connection")
    #print(symbol_list_loads)

    ws.send(json.dumps({
        "time": int(time.time()),
        "channel": "spot.tickers",
        "event": "subscribe",  # "unsubscribe" for unsubscription
        "payload": symbol_list_loads
    }))


#websocket.enableTrace(True)
ws = websocket.WebSocketApp("wss://api.gateio.ws/ws/v4/",
                            on_message = on_message,
                            on_error = on_error,
                            on_close = on_close)
ws.on_open = on_open
ws.run_forever()
