Готовый код для загрузки цен с 4 бирж
- Binance
- Gate
- Huobi
- KuCoin

Настройка :
```Python
setting = {
        "refreshTime":60, # Время повторной загрузки
        "host":"localhost", # Хост для MySQL
        "user":"root", # Логин MySQL
        "passwd":"", # Пароль MySQL
        "db":"price" # База MySQL
    }
```

Настройка автозапуска загрузки
```Python
RunLoad = {
    "Binance": False,
    "Gate": True, # Авто запуск
    "Huobi": False,
    "KuCoin": False
}
```
