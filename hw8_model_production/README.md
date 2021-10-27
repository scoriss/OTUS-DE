# HW8 - Продуктивизация модели

**:back: [Назад](/../../)**

## Что нужно сделать
Использовать на практике приобретенные навыки написания чистого кода (чистота кода, структура проекта, архитектурные паттерны, тесты), изоляции окружения (python virtual environment, docker) и деплой проекта. 

1. Продуктивизировать ноутбук и довести его до состояния близкого к продуктивному решению.
2. Реализовать автоматическую перетренировку модели по запросу или по расписанию (через вызов скрипта из консоли или REST-запрос).
3. Написать тесты разработанной функциональности на `pytest`. 
4. Упаковать код с виртуальным окружением в образ `docker`, который реализует предиктивное действие (получение результатов через REST-запросы). 
5. Деплой проекта локально или в Yandex.Cloud. 

## Комментарии по заданию
* Для начальной структуры проекта взят репозиторий **[ml_project_example](https://github.com/Mikhail-M/ml_project_example)**.
* В качестве исходного кода для продуктивизации модели использован ноутбук **[Tip of the Iceberg: EDA & Prediction (0.80861)](https://www.kaggle.com/sumukhija/tip-of-the-iceberg-eda-prediction-0-80861)**, решающий известную задачу на **Kaggle - [Titanic - Machine Learning from Disaster](https://www.kaggle.com/c/titanic/overview)**.<br>
  Файл - **[Titanic Predictions.ipynb](notebooks/Titanic%20Predictions.ipynb)**
* Конфигурация параметров модели и REST-сервиса задается в YAML-файле **[model_config.yaml](configs/model_config.yaml)**.
* Для запуска docker-контейнера, порт REST-сервиса также прописывается в переменной окружения `MODEL_API_PORT`<br> в файле **[.env](.env)**

Проект "titanic_model"
==============================

### Установка проекта
* Вариант запуска в docker-контейнере:<br><br>
    ```Bash 
    docker-compose up
    ```
    При выполнении будет собран docker-образ **otus-de-hw8:1.0** и поднят контейнер **titanic-model**
* Локальная установка:<br><br>
    ```Bash 
    python -m venv .titanic_model
    source .titanic_model/bin/activate
    pip install -r requirements.txt
    python setup.py install
    ```

### Использование:
Запуск работы модели и REST-сервиса производится через python-код **[titanic_model.py](titanic_model.py)** реализующий консольное приложение.<br>
<details><summary>Скриншот консольного приложения</summary><br>

![model_console_prog](https://user-images.githubusercontent.com/18349305/139060293-b142e4a1-bbcb-41c4-8067-c3c33c12b8de.jpg)

</details>

Для выполнения команд в запущенном docker-контейнере - выполнить команду:<br>
```Bash 
docker exec -it titanic-model bash
```
Рабочий каталог в контейнере **/opt/titanic_model**

#### Тренировка модели

Производится выполнением команды **train** с указанием пути к файлу конфигурации модели.
```Bash 
python titanic_model.py train ./configs/model_config.yaml
```
<details><summary>Скриншот выполнения тренировки</summary><br>

![train](https://user-images.githubusercontent.com/18349305/139076912-038b59c4-15bd-447e-84c4-58ea33701565.jpg)

</details>


#### Прогнозирование результатов

Производится выполнением команды **predict** с указанием пути к файлу конфигурации модели.
```Bash 
python titanic_model.py predict ./configs/model_config.yaml
```
<details><summary>Скриншот выполнения прогнозирования</summary><br>

![predict](https://user-images.githubusercontent.com/18349305/139076930-1e0ed29c-ac67-4365-a637-83f42b23f349.jpg)

</details>


#### Запуск REST-сервиса
* При запуске проекта в docker-контейнере, REST-сервис автоматически запущен и доступен.
* Для локального запуска необходимо выполнить команду:<br><br>
    ```Bash 
    python titanic_model.py serve ./configs/model_config.yaml
    ```
* REST-сервис доступен по ссылкам:
  * Прогнозирование результатов - **[http://localhost:5555/](http://localhost:5555/)** или **[http://localhost:5555/predict](http://localhost:5555/predict)**
  * Тренировка модели - **[http://localhost:5555/train](http://localhost:5555/train)**

#### Тесты функциональности:
Выполнить команду:
```Bash 
pytest tests/
```
<details><summary>Скриншот результатов тестирования</summary><br>

![pytest_result](https://user-images.githubusercontent.com/18349305/139063374-b73b04fc-685c-4cfa-b9a3-be5855b0b82f.jpg)

</details>

### Завершение работы
При завершении работы, выполнить команду:
```Bash 
docker-compose down
docker rmi otus-de-hw8:1.0
```

## Структура проекта


    ├── configs             <- Файл конфигурации проекта для работы модели в формате YAML.
    │
    ├── data                <- Оригинальные данные для модели проекта с Kaggle.
    │
    ├── models              <- Папка с дампами обученной модели в бинарном формате (joblib).
    │
    ├── notebooks           <- Оригинальный код, на котором основан данный проект и файл зависимостей для его выполнения.
    │
    ├── references          <- Справочники и другие пояснительные материалы.
    │
    ├── reports             <- Сформированные файлы предсказательной аналитики в формате CSV.
    │
    ├── tests               <- Файлы тестов проекта (pytest).
    │
    ├── titanic_model       <- Исходный код модуля для использования в данном проекте.
    │   │
    │   ├── data            <- Код загрузки данных модели.
    │   │
    │   ├── model           <- Код реализации Rest API сервиса, тренировки модели и прогнозирования.
    │   │
    │   └── preprocess      <- Код для преобразования необработанных данных в характеристики для моделирования.
    │
    ├── .env                <- Файл с переменными окружения для docker-контейнера.
    ├── docker-compose.yml  <- Файл Docker Compose для запуска контейнера.
    ├── dockerfile          <- Docker-файл для создания образа с Python virtual environment.
    ├── README.md           <- README с описанием проекта.
    ├── requirements.txt    <- Файл зависимостей для воспроизведения среды выполнения.
    ├── setup.py            <- Сценарий установки модуля проекта.
    └── titanic_model.py    <- Код основного запуска модели с параметрами командной строки.
