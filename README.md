# Подготовка виртуальной машины

## Склонируйте репозиторий

Склонируйте репозиторий проекта:
git clone https://github.com/yandex-praktikum/mle-project-sprint-4-v001.git

## Активируйте виртуальное окружение
Создать новое виртуальное окружение можно командой:
cd ~/mle_projects/mle-project-sprint-4-v001/
sudo apt-get update
sudo apt-get install python3-venv
python3 -m venv .env_recsys_start

После его инициализации следующей командой
source .env_recsys_start/bin/activate

установите в него необходимые Python-пакеты следующей командой
pip install -r requirements.txt

#теперь создаем новые kernel для работы yupiter notebook
python -m ipykernel install --user --name=.env_recsys_start

### Скачайте файлы с данными
cd ~/mle_projects/mle-project-sprint-4-v001/data
Для начала работы понадобится три файла с данными:
- [tracks.parquet](https://storage.yandexcloud.net/mle-data/ym/tracks.parquet)
- [catalog_names.parquet](https://storage.yandexcloud.net/mle-data/ym/catalog_names.parquet)
- [interactions.parquet](https://storage.yandexcloud.net/mle-data/ym/interactions.parquet)
 
Скачайте их в директорию локального репозитория. Для удобства вы можете воспользоваться командой wget:

wget https://storage.yandexcloud.net/mle-data/ym/tracks.parquet
wget https://storage.yandexcloud.net/mle-data/ym/catalog_names.parquet
wget https://storage.yandexcloud.net/mle-data/ym/interactions.parquet

## Запустите Jupyter Lab

Запустите Jupyter Lab в командной строке
jupyter lab --ip=0.0.0.0 --no-browser

# Расчёт рекомендаций

Код для выполнения первой части проекта находится в файле `recommendations.ipynb`. Изначально, это шаблон. Используйте его для выполнения первой части проекта.


# Сервис рекомендаций

Код сервиса рекомендаций находится в файле `recommendations_service.py`. Для онлайн рекомендаций используются события пользователя - events_service и предрасчитанные рекомендации для треков - feature service

для запуска сервисов необходимо последовательно запустить
cd ~/mle_projects/mle-project-sprint-4-v001/services
uvicorn recommendations_service:app 
uvicorn features_service:app --port 8010 
uvicorn events_service:app --port 8020

для новых пользователей без недавних прослушиваний - рекомендуем популярные треки
для существующих пользователей без недавних прослушиваний - рекомендуем предрассчитаные персональные рекомендации на основе истории прослушивания
для существующих пользователей с недавними прослушиваниями - чередуем офлайн и онлайн рекомендации в выдаче результатов


# Инструкции для тестирования сервиса

Код для тестирования сервиса находится в файле `test_service.py`.

