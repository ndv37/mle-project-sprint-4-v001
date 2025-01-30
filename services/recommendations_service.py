import logging
import pandas as pd
from fastapi import FastAPI
from contextlib import asynccontextmanager
import requests
logger = logging.getLogger("uvicorn.error")

PERSONAL_RECS_PATH="/home/mle-user/mle_projects/mle-project-sprint-4-v001/recs/recommendations.parquet"
TOP_POPULAR_RECS_PATH="/home/mle-user/mle_projects/mle-project-sprint-4-v001/recs/top_popular.parquet"
features_store_url = "http://127.0.0.1:8010"
events_store_url = "http://127.0.0.1:8020" 

class Recommendations:

    def __init__(self):

        self._recs = {"personal": None, "default": None}
        self._stats = {
            "request_personal_count": 0,
            "request_default_count": 0,
        }

    def load(self, type, path, **kwargs):
        """
        Загружает рекомендации из файла
        """

        logger.info(f"Loading recommendations, type: {type}")
        self._recs[type] = pd.read_parquet(path, **kwargs)
        if type == "personal":
            self._recs[type] = self._recs[type].set_index("user_id")
        logger.info(f"Loaded")

    def get(self, user_id: int, k: int=100):
        """
        Возвращает список рекомендаций для пользователя
        """
        try:
            recs = self._recs["personal"].loc[user_id]
            recs = recs["track_id"].to_list()[:k]
            self._stats["request_personal_count"] += 1
        except KeyError:
            recs = self._recs["default"]
            recs = recs["track_id"].to_list()[:k]
            self._stats["request_default_count"] += 1
        except:
            logger.error("No recommendations found")
            recs = []

        return recs

    def stats(self):

        logger.info("Stats for recommendations")
        for name, value in self._stats.items():
            logger.info(f"{name:<30} {value} ")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # код ниже (до yield) выполнится только один раз при запуске сервиса
    logger.info("Starting")
    yield
    # этот код выполнится только один раз при остановке сервиса
    logger.info("Stopping")

# создаём приложение FastAPI
app = FastAPI(title="recommendations", lifespan=lifespan)

rec_store = Recommendations()

rec_store.load("personal",PERSONAL_RECS_PATH,columns=["user_id", "track_id", "score"],)
rec_store.load("default",TOP_POPULAR_RECS_PATH,columns=["track_id", "score"],)

#офлайн рекомендации
@app.post("/recommendations_offline")
async def recommendations_offline(user_id: int, k: int = 100):

    """ Возвращает список рекомендаций длиной k для пользователя user_id """
    recs = rec_store.get(user_id, k)#[]
    return {"recs": recs} 

def dedup_ids(ids):

    """Дедублицирует список идентификаторов, оставляя только первое вхождение"""
    seen = set()
    ids = [id for id in ids if not (id in seen or seen.add(id))]
    return ids

#онлайн рекомендации
@app.post("/recommendations_online")
async def recommendations_online(user_id: int, k: int = 100):
    """    Возвращает список онлайн-рекомендаций длиной k для пользователя user_id"""
    headers = {"Content-type": "application/json", "Accept": "text/plain"}

    # получаем список последних событий пользователя, возьмём три последних
    params = {"user_id": user_id, "k": 3}
    resp = requests.post(events_store_url + "/get", headers=headers, params=params)
    events = resp.json()
    events = events["events"]
    
    # получаем список айтемов, похожих на последние три, с которыми взаимодействовал пользователь
    tracks = []
    scores = []
    for track_id in events:
        # для каждого item_id получаем список похожих в item_similar_items
        params = {"track_id": track_id, "k": k}
        resp = requests.post(features_store_url + "/similar_items", headers=headers, params=params)
        item_similar_items = resp.json()
        tracks += item_similar_items["track_id_2"]
        scores += item_similar_items["score"]
    # сортируем похожие объекты по scores в убывающем порядке
    # для старта это приемлемый подход
    combined = list(zip(tracks, scores))
    combined = sorted(combined, key=lambda x: x[1], reverse=True)
    combined = [track for track, _ in combined]

    # удаляем дубликаты, чтобы не выдавать одинаковые рекомендации
    recs = dedup_ids(combined)
    recs = recs[:k]
    return {"recs": recs}

#финальные рекомендации
@app.post("/recommendations")
async def recommendations(user_id: int, k: int = 100):
    """ Возвращает список рекомендаций длиной k для пользователя user_id """
    recs_offline = await recommendations_offline(user_id, k) 
    recs_online = await recommendations_online(user_id, k)
    recs_offline = recs_offline["recs"]
    recs_online = recs_online["recs"]

    recs_blended = []

    min_length = min(len(recs_offline), len(recs_online))
    # чередуем элементы из списков, пока позволяет минимальная длина
    for i in range(min_length):
        recs_blended.append(recs_online[i])
        recs_blended.append(recs_offline[i])

    # добавляем оставшиеся элементы в конец
    recs_blended += recs_online[min_length:]
    recs_blended += recs_offline[min_length:]
    # удаляем дубликаты
    recs_blended = dedup_ids(recs_blended)

    # оставляем только первые k рекомендаций
    recs_blended = recs_blended[:k]
    return {"recs": recs_blended}
