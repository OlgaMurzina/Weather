# С сайта openweathermap.org забираю пары город-(широта, долгота)

import requests

APPID = "dd434a2bab749c9a841f6cb6b41e3ab1"
URL_BASE = "https://pro.openweathermap.org/data/2.5/"

# запрос локаций городов Московской области (города взяла просто из списка первых в МО)
URL_GEO = "http://api.openweathermap.org/geo/1.0/direct?"
CITYS = ['Москва', 'Абрамцево', 'Алабино', 'Апрелевка', 'Архангельское', 'Ашитково',
         'Бакшеево', 'Балашиха', 'Барыбино', 'Белозёрский', 'Белоомут', 'Белые Столбы',
         'Бородино', 'Бронницы']
limit = 1
# словарь город:локация
geo = {}
for q in CITYS:
    params = f'q={q}&limit={limit}&appid={APPID}'
    responce = requests.get(f'{URL_GEO}{params}').json()
    lat = responce[0]['lat']
    lon = responce[0]['lon']
    geo[q] = (lat, lon)
# print(geo)
