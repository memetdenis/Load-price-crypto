<?php
// Необходимые HTTP-заголовки 
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json; charset=UTF-8");

// Замерим скорость работы
$time_start = microtime(true);

// Пустой массив для данных
$json = array();

// Установим временную зону для правильного отображения даты и времени
date_default_timezone_set('Europe/Moscow');

//**************************************************************************************************
function DelNulls($tmp) {

    $lasttmp = $tmp[strlen($tmp)-1]; // последний символ в строке
        
    while ($lasttmp == '0') { // цикл определения нуля в конце строки
        $tmp = substr($tmp,0,strlen($tmp)-1); // укорачиваем строку на 1 символ, т.е. убираем последний ноль
        $lasttmp = $tmp[strlen($tmp)-1]; // определяем последний символ в новой строке
    }

    if (($lasttmp =='.') || ($lasttmp == ',')){
        $tmp = substr($tmp,0,strlen($tmp)-1);
    } // убираем точку или запятую
    
    return $tmp;
}

//**************************************************************************************************
//Функция антихака по текстовой переменной
function anticrack ($var){
    $var=str_replace("'","",$var);
    $var=str_replace('"','',$var);
    $var=str_replace('`','',$var);
    $var=trim(htmlspecialchars($var));
    return ($var);
}

//Подключимся к базе данных
try {
    $conn = new PDO('mysql:host=localhost;dbname=price', "root", "");
    $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch(PDOException $e) {
    $json['error'] = 'ERROR: ' . $e->getMessage();
    print(json_encode($json));
    exit;
}

// Проверим наличие фильтров
$filter = array();
if (isset($_GET['birza']))      $filter['birza'] 	 = (int)($_GET['birza']);
if (isset($_GET['symbol']))     $filter['symbol'] 	 = anticrack($_GET['symbol']);

// Наш запрос
$query = "SELECT * FROM `price`"; 

// Добавим фильтры к запросу
if(count($filter)>0){
    // Если есть фильтры, то добавим WHERE
    $query .= "WHERE ";
    // Счетчик количество добавленных фильтров
    $add_count_filter = 0; 
    // Если 
    foreach($filter as $key=>$value){
        // Если уже не первый фильтр добаляем, то нужно добавить AND
        if($add_count_filter>0){$query .= " AND ";}

        // Проверим тип переменной
        if(is_int($value)){ // Если это число, добавляем с помощью равно
            $query .= "`{$key}` = {$value}";
        }elseif(is_string($value)){// Если это строка, то добаляем сраненение LIKE
            $query .= "`{$key}` LIKE '{$value}'";
        }

        // Добавим счетчик количество фильтров
        $add_count_filter++;
    }
}

$json['query'] = $query; // Покажем нам какой запрос был сформирован

// Выполним запрос
$Q = $conn->prepare($query);
$Q->execute();

// Выгрузим все строки полученные в запросе
$json['result'] = array();
$result = $Q->fetchAll();
foreach($result as $row){
    $json['result'][] = array('birza'=>$row['birza'], 'symbol'=>$row['symbol'], 'price'=>DelNulls($row['price']), 'prevDay'=>$row['prevDay'], 'last_update'=>$row['last_update']);
}

$json['time_execution'] = round(microtime(true) - $time_start,4); // Время выполенения скрипта
$json['time'] = time(); // Текущее время сервера

print(json_encode($json));
?>