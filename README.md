# Описание решения

Создана система контекстов для чат-бота. Идея заключается в том, чтобы анализировать сообщение от пользователя и подбирать небольшое количество контекстов, чтобы не перегружать нейронную сеть большим количеством токенов. Система состоит из следующих частей:

1. Сбор сета данных (взятого с сайта компании EORA) в формате JSON со следующими полями:
   - url: ссылка на источник
   - context: полезный текст со страницы для формирования ответа
   - short_context: краткая версия context для определения нужного контекста, который будет участвовать в формировании ответа

2. Загрузка данных из JSON в базу данных.

3. При запросе от пользователя передача нейронной сети сообщения пользователя и данных в формате [{id: int, short_context: str}], чтобы она определила необходимое количество контекстов, которые будут полезны в формировании ответа. На выходе получаем список с id контекстов.

4. Передача сообщения пользователя и отобранных контекстов в формате [{url: str, context: str}] и запрос нейронной сети на формирование ответа с учетом данных из контекста, а также запрос на указание ссылок на источники контекста.


# Как поднять

1. Установите локальное окружение:
   - Перейдите в командную строку на 1-й уровень проекта (из папки src выше на 1 уровень, "\src> cd ..").
   - Установите pipenv, выполнив команду "pip install pipenv".
   - Установите пакеты в окружение с помощью команды "pipenv install --ignore-pipfile".

2. В папке src создайте копию файла default_config.toml и назовите его config.toml:
   - В файле config.toml установите настройки для базы данных.
     - Инструкция для создания образа PostgreSQL в Docker:
       - Выполните команду для создания образа PostgreSQL в Docker: "docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=pass --name postgres_eora_test_task postgres".
       - Подключитесь к контейнеру и создайте базу данных:
         1. Выполните команду: "docker exec -it postgres_eora_test_task bash".
         2. Затем выполните: "psql -U postgres".
         3. Наконец, создайте базу данных: "create database eora_test_task;".
   - Установите настройки OpenAI:
     - api_key: ключ можно получить [здесь](https://platform.openai.com/api-keys).
       - Для корректной работы ключа лимит не должен быть исчерпан; лимиты можно посмотреть [здесь](https://platform.openai.com/usage).
     - model: тип языковой модели, который будет использоваться для формирования ответа.
       - gpt-3.5-turbo: работает менее эффективно, чем gpt-4, но более доступен.
       - gpt-4: обеспечивает лучший ответ, но стоит дороже gpt-3.5-turbo.

3. Включите VPN, чтобы OpenAI не блокировал запросы.

4. В консоли перейдите на уровень src и выполните следующие команды:
   - alembic upgrade head: чтобы применить миграции к базе данных и создать таблицы.
   - uvicorn main:app --reload: чтобы запустить локальный сервер.

5. Перейдите по адресу [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs):
   - Сделайте запрос на API /answer-chat/contexts/fill, чтобы создать записи контекста в базе данных из JSON файла.

6. Делайте запросы на API /answer-chat/answer и получайте ответы. :)


# Что пробовали сделать, что сработало, а что не очень

На самом деле, я пока не пробовал ничего другого, это первая идея, которая пришла мне в голову, и я сразу её реализовал. И она заработала.


# Что бы ещё добавили в решение, если бы было больше времени

1. Улучшил бы качество данных контекста. В данных сейчас много мусора, который мешает качественному запросу.
2. Решение не масштабируется: если контекстов станет много, мы упрёмся в лимиты. Поэтому:
   - Я бы оптимизировал 3-й этап из описания решения, добавив ключевые слова к модели контекста и искал бы вхождения, чтобы уменьшить выборку контекстов для 3-го этапа из описания решения.
     - Ключевые слова можно составить также с помощью GPT.
   - Для оптимизации 3-го этапа из описания решения исследовал бы алгоритмы поиска в браузере для вдохновения.
3. Провёл бы исследование auto-GPT и проанализировал, как оно может помочь или не помочь.
4. Добавил бы тесты
5. Посвятил бы больше времени изучению SQLAlchemy и FastAPI так как это 1-й опыт
6. Добавил бы обработку ошибок при запросах к сторонним апи
7. Растащил бы логику из view по сервисам