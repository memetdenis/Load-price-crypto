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
setting = {
        "refreshTime":60, # Время повторной загрузки в секундах
        "host":"localhost", # Хост для MySQL
        "user":"root", # Логин MySQL
        "passwd":"", # Пароль MySQL
        "db":"price", # База MySQL
        "Checkbox": { # Все чекБоксы
            "history_1m": { # Системное имя
                "name": "Каждую минуту, но не более суток", # Название
                "act" : True # Состояние при запуске
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
        }
    }
```

Настройка автозапуска загрузки
```Python
RunLoad = {
    "Binance": {
        "auto_start":True, # Автозапуск
        "count_load":0 # Счетчик количесво загрузок
        },
    "Gate": {
        "auto_start":False,
        "count_load":0
        },
    "Huobi": {
        "auto_start":False,
        "count_load":0
        },
    "KuCoin": {
        "auto_start":False,
        "count_load":0
        }
}
```
