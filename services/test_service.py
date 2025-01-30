
import requests
events_store_url = "http://127.0.0.1:8020"
feature_store_url= "http://127.0.0.1:8010"
recommendations_url = "http://127.0.0.1:8000"
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

#**********************************************************************
#ПРИМЕР 1 - Рекомендации для холодных пользователей без онлайн активности
params = {"user_id": 100500100, 'k': 3}

print('***********************************')
print('example 1 - cold user')
print(f'cold user {params["user_id"]}')
resp = requests.post(recommendations_url + "/recommendations", headers=headers, params=params)
if resp.status_code == 200:
    recs = resp.json()
else:
    recs = []
    print(f"status code: {resp.status_code}")
print(f"recommendation: {recs}")

#**********************************************************************
#ПРИМЕР 2 - Рекомендации для существующих пользователей без онлайн активности - персональные рекомендации
params = {"user_id": 4, 'k': 3}

print('***********************************')
print('example 2 - hot user no events')
print(f'hot user no events {params["user_id"]}')
resp = requests.post(recommendations_url + "/recommendations_offline", headers=headers, params=params)
if resp.status_code == 200:
    recs = resp.json()
else:
    recs = []
    print(f"status code: {resp.status_code}")
print(f"recommendation_offline: {recs}")

resp = requests.post(recommendations_url + "/recommendations", headers=headers, params=params)
if resp.status_code == 200:
    recs = resp.json()
else:
    recs = []
    print(f"status code: {resp.status_code}")
print(f"recommendation: {recs}")

#**********************************************************************
#ПРИМЕР 3 - Рекомендации для существующих пользователей c онлайн активностью - смешивание персональных офлайн рекомендаций и онлайн
print('***********************************')
print('example 3 - hot user with events')
#теперь запишем пользователю в историю прослушанный трек
params = {"user_id": 3, "track_id": 24417}

resp = requests.post(events_store_url + "/put", headers=headers, params=params)
if resp.status_code == 200:
    result = resp.json()
else:
    result = None
    print(f"status code: {resp.status_code}")
print(f'hot user save online events {result}')

#проверим что получилось
resp = requests.post(events_store_url + "/get", headers=headers, params=params)
if resp.status_code == 200:
    result = resp.json()
else:
    result = None
    print(f"status code: {resp.status_code}")
print(f'hot user online events {result}')

# онлайн рекомендации
params = {"user_id": 3, 'k': 3}

resp = requests.post(recommendations_url + "/recommendations_online", headers=headers, params=params)
online_recs = resp.json() 
print(f'hot user online recs {online_recs}') 

#оffline
resp = requests.post(recommendations_url + "/recommendations_offline", headers=headers, params=params)
offline_recs = resp.json()
print(f'hot user offline recs {offline_recs}') 

#финальная рекомендация
resp = requests.post(recommendations_url + "/recommendations", headers=headers, params=params)
offline_recs = resp.json()
print(f'hot user result recs {offline_recs}') 