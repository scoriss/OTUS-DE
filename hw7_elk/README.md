# HW7 - Анализ веб-логов с помощью ELK

**:back: [Назад](/../../)**

## Что нужно сделать
1. Написать конфигурацию **Logstash** для загрузки данных в **ElasticSearch**.
2. Построить отчет в **Kibana** на основе этих данных.

<details><summary><strong>Инструкция по заданию</strong></summary><br>

### Инструкция
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
5. Перейдите по адресу http://localhost:5601 и создайте отчет (dashboard), показывающий распределение запросов с разными кодами ответов (status_code) по времени

### Подсказки
- Пример конфигурации можно подсмотреть [здесь](https://dzone.com/articles/logstash-elasticsearch-and)
- Для добавления данных в Kibana нужно сначала создать Index Pattern, по которому будут подгружаться индексы из ES
</details>
<br>

## Файлы
* **[docker-compose-hw7.yml](docker-compose-hw7.yml)** - Доработанный файл `docker-compose` для одновременного запуска сервисов **ELK** и выполнения загрузки данных **Logstash** по файлу конфигурации `clickstream.conf`.

* **[kibana.ndjson](kibana.ndjson)** - Файл экспорта с настройками и сохраненными объектами **Kibana** по заданию.


## Инструкция по запуску 
1. Развернуть инфраструктуру сервисов **ELK**, выполнив команду:<br><br>
    ```Bash 
    docker compose -f docker-compose-hw7.yml up -d
    ```
2. После загрузки всех сервисов - перейти по адресу http://localhost:5601
3. Импортируйте настройки и сохраненные объекты в **Kibana**.<br>
    Для этого необходимо выполнить следующие шаги:
    1. Перейти в настройки: `Management -> Kibana -> Saved Objects`
    2. Выполнить импорт файла `kibana.ndjson`, с включенными опциями `Check for existing objects` и `Automatically overwrite conflicts`
    3. После выполнения импорта можно запускать на выполнение dashboard по заданию **Weblog Dashboard**, из списка сохраненных объектов или из раздела Kibana.
4. По завершению работы, выполнить команду:<br><br>
    ```Bash 
    docker compose -f docker-compose-hw7.yml down
    ```
