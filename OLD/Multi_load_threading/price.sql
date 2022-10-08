-- --------------------------------------------------------

--
-- Структура таблицы `price`
--

CREATE TABLE `price` (
  `birza` smallint(5) UNSIGNED NOT NULL,
  `symbol` varchar(20) NOT NULL,
  `price` decimal(20,10) NOT NULL,
  `last_update` int(10) UNSIGNED NOT NULL DEFAULT unix_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Индексы таблицы `price`
--
ALTER TABLE `price`
  ADD PRIMARY KEY (`symbol`,`birza`) USING HASH;
COMMIT;