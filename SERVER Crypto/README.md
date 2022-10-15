Готовый код для загрузки цен с 4 бирж
- Binance
- Gate
- Huobi
- KuCoin
С чего начать:
1. Создать базу данных из файла price.sql
2. Внести изменения в настройки
3. Установить компоненты для запуска Python
```CMD
pip install mysqlclient
pip install requests
```

Настройка :
```Python
    # Массив настроек
    setting = {
        "refreshTime":180, # Время повторной загрузки в секундах
        "host":"localhost", # Хост для MySQL
        "user":"root", # Логин MySQL
        "passwd":"", # Пароль MySQL
        "db":"price", # База MySQL
        "checkbox": { # Все чекБоксы
            "history_1m": { # Системное имя
                "name": "Каждую минуту, но не более суток", # Название
                "act" : False # Состояние при запуске
            },
            "history_10m": { # Системное имя
                "name": "Каждые 10 минут, но не более суток", # Название
                "act" : True # Состояние при запуске
            },
            "history_1h": { # Системное имя
                "name": "Каждый час, но не более суток", # Название
                "act" : True # Состояние при запуске
            },
            "history_1d": { # Системное имя
                "name": "Раз в день, всегда", # Название
                "act" : True # Состояние при запуске
            }
        },
        "time_load": 0
    }
```

Настройка автозапуска загрузки
```Python
   birzi = {
        "Binance": {
            "auto_start":True, # Авто старт загрузки
            "count_load":0, # Колчиество загрузок с момента старта
            "icon":"Binance.png", # Иконка
            "last_time":0, # Последнее успешная загрузка
            "number":1, # Номер биржи в базе
            "log":"" # Последнее сообщение после загрузки
            },
        "Gate": {
            "auto_start":True,
            "count_load":0,
            "icon":"Gate.png",
            "last_time":0,
            "number":2,
            "log":""
            },
        "Huobi": {
            "auto_start":True,
            "count_load":0,
            "icon":"Huobi.png",
            "last_time":0,
            "number":3,
            "log":""
            },
        "KuCoin": {
            "auto_start":True,
            "count_load":0,
            "icon":"KuCoin.png",
            "last_time":0,
            "number":4,
            "log":""
            }
    }
```
