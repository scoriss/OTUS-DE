# HW7 - Анализ веб-логов с помощью ELK

**:back: [Назад](/../../)**

## Что нужно сделать
1. Написать конфигурацию **Logstash** `clickstream.conf` для загрузки данных файла **weblog.csv** в **ElasticSearch**.
2. Построить отчет в **Kibana**, показывающий распределение запросов с разными кодами ответов (status_code) по времени.

<details><summary><strong>Инструкция по заданию</strong></summary><br>

1. Клонируйте репозиторий [elk_demo](https://github.com/Gorini4/elk_demo)
2. Зайдите в эту директорию и разверните инфраструктуру, выполнив команду:<br><br>
    ```Bash 
    docker-compose up
    ```
3. Отредактируйте файл `clickstream.conf`
4. Загрузите данные веб-логов, выполнив команду:<br><br>
    ```Bash 
    ./load_data.sh
    ```
5. Перейдите по адресу http://localhost:5601 и создайте отчет (dashboard), показывающий распределение запросов с разными кодами ответов (status_code) по времени.

### Подсказки
- Пример конфигурации можно подсмотреть [здесь](https://dzone.com/articles/logstash-elasticsearch-and)
- Для добавления данных в Kibana нужно сначала создать Index Pattern, по которому будут подгружаться индексы из ES

</details>

## Файлы
* **[docker-compose-hw7.yml](docker-compose-hw7.yml)** - Доработанный файл `docker-compose` для одновременного запуска сервисов **ELK** и выполнения загрузки данных **Logstash** по файлу конфигурации [clickstream.conf](logstash/clickstream.conf).

* **[kibana.ndjson](kibana.ndjson)** - Файл экспорта с настройками и сохраненными объектами **Kibana** по заданию.


## Инструкция по запуску 
1. Развернуть инфраструктуру сервисов **ELK**, выполнив команду:<br><br>
    ```Bash 
    docker-compose -f docker-compose-hw7.yml up
    ```
2. После загрузки всех сервисов - перейти по адресу http://localhost:5601
3. Импортировать настройки и сохраненные объекты в **Kibana**.<br>
    Для этого необходимо выполнить следующие шаги:
    * Перейти в настройки:  `Management -> Kibana -> Saved Objects`
    * Выполнить импорт файла `kibana.ndjson`, с включенными опциями `Check for existing objects` и `Automatically overwrite conflicts`
    * После выполнения импорта можно запускать на выполнение **Weblog Dashboard**, из списка сохраненных объектов или из раздела **Kibana**.
4. По завершению работы, выполнить команду:<br><br>
    ```Bash 
    docker-compose -f docker-compose-hw7.yml down
    ```
### Решение иногда возникающей ошибки после импорта объектов
:warning: ***Request error: zone_rules_exception, Unknown time-zone ID: Browser***

После импорта сохраненных объектов, в разделе `Saved Objects` зайти в `Advanced Settings [7.14.1]` и перегрузить страницу `Ctrl+R`. После этого снова запустить dashboard.

## Комментарии по заданию

* Для корректного парсинга даты в логе создан паттерн **WEBLOGDATE** в файле конфигурации [clickstream.conf](logstash/clickstream.conf)
* Строки лога не попавшие в шаблон соответствия - удалены.
* В **ElasticSearch** выгружено **15 789** строк в индекс **otus-de-weblog**.
## Результат работы

**Weblog Dashboard**

![Weblog Dashboard](https://user-images.githubusercontent.com/18349305/137751864-52f2261f-856d-4889-8ab4-828aca3995db.jpg)

**Weblog Discover**
![Weblog Discover](https://user-images.githubusercontent.com/18349305/137739509-f5c176bb-56b4-4cac-af0b-9ea4e8783c80.jpg)


![otus-de-weblog-index](https://user-images.githubusercontent.com/18349305/137755049-aa48bcd3-4c95-430c-b150-8d54e7ad7e93.jpg)
