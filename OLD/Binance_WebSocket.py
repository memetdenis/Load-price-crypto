# Загрузка всех торговых пар с биржи Binance через WSS
import websocket
import json
import time
import MySQLdb

# Подключимся к базе данных
db = MySQLdb.connect(host="localhost", user="root", passwd="", db="price")
cursor = db.cursor()

def on_message(ws, message):
    time_start = time.time()

    data = json.loads(message)  # Выгрузим JSON в массив

    # Переберём массив данных(json)
    for crypto_symbol in data:
        cursor.execute(f"INSERT INTO `price` (`symbol`, `price`) VALUES ('{crypto_symbol['s']}', '{crypto_symbol['c']}') ON DUPLICATE KEY UPDATE price = '{crypto_symbol['c']}' , last_update = UNIX_TIMESTAMP();")  # Записать изменение цены

    db.commit()  # Зафиксировать транзакции
    print(f'Обработали {len(data)} торговых символов за {round(time.time() - time_start, 3)} сек.')

def on_close(ws):
    print("### closed ###")

ws = websocket.WebSocketApp("wss://stream.binance.com:9443/ws/!ticker@arr",
                            on_message=on_message,
                            on_close=on_close)

ws.run_forever()  # Set dispatcher to automatic reconnection