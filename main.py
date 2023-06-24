import requests
# import _citys
import datetime as dt
from data.weather import Weather
from data import db_session
import pandas as pd
from sqlalchemy import create_engine
import seaborn as sns
import matplotlib.pyplot as plt


def citys():
    APPID = "API_KEY"
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
    return geo


def load(geo):
    # загрузка данных с сайта погоды
    APPID = "API_KEY"
    URL_BASE = "https://api.openweathermap.org/data/2.5/forecast?"
    db_session.global_init("db/weather.db")
    # параметр - количество выгружаемых записей на один объект
    n = 24
    # формирование запроса по каждому объекту из модуля citys по геоданным
    for x in geo.keys():
        lat, lon = geo[x]
        params = f'lat={lat:.2f}&lon={lon:.2f}&cnt={n}&appid={APPID}&units=metric&lang=ru'
        # получение ответа и перевод его в .json
        responce = requests.get(f'{URL_BASE}{params}').json()
        # парсинг ответа с формированием записи для загрузки в БД
        for data in responce['list']:
            report = Weather()
            report.date = dt.datetime.strptime(data['dt_txt'], '%Y-%m-%d %H:%M:%S')
            report.city = x
            report.humidity = int(data['main']['humidity'])
            report.pressure = int(data['main']['pressure'])
            report.temp_max = float(data['main']['temp_max'])
            report.temp_min = float(data['main']['temp_min'])
            report.clouds = int(data['clouds']['all'])
            report.wind_napr = int(data['wind']['deg'])
            report.wind_speed = float(data['wind']['speed'])
            report.description = data['weather'][0]['description']
            db_sess = db_session.create_session()
            # проверка дублей
            if db_sess.query(Weather).filter(
                    Weather.date == dt.datetime.strptime(data['dt_txt'], '%Y-%m-%d %H:%M:%S'),
                    Weather.city == x):
                # существующую старую запись удаляем
                db_sess.query(Weather).filter(
                    Weather.date == dt.datetime.strptime(data['dt_txt'], '%Y-%m-%d %H:%M:%S'),
                    Weather.city == x).delete()
                db_sess.commit()
            # добавляем запись к БД
            db_sess.add(report)
            db_sess.commit()


def query(cols, condition, group, type):
    # создание курсора
    engine = create_engine('sqlite:///db/weather.db', echo=True)
    # формирование витрины по запросам
    if cols and condition and group:
        qu = f'select {cols} from weather where {condition} group by {group}'
    elif cols and condition:
        qu = f'select {cols} from weather where {condition}'
    elif cols:
        qu = f'select {cols} from weather'
    # получение датафрейма из ответа на запрос
    df = pd.read_sql_query(qu, engine)
    print(df)
    st = cols.split(', ')
    # вызов функции построения графика для данной витрины
    draw(df, st, group, type)


def draw(df, st, group=None, type='line'):
    # функция построения графика для одной витрины под разные параметры
    sns.set_theme(style="darkgrid")
    x = st[0]
    y = st[1:]
    if type == 'line':
        sns.lineplot(data=df)
    elif type == 'bar':
        sns.barplot(data=df)
    elif type == 'hist':
        sns.histplot(data=df, x=x, y=st[2], hue=st[1])
    elif type == 'scatter':
        sns.scatterplot(data=df)
    elif type == 'heat':
        sns.heatmap(data=df)
    plt.show()


def main():
    geo = citys()
    # загрузка данных
    load(geo)
    # формирование витрин
    queries = {'cols': [f'city, max(temp_max), max(wind_speed), min(wind_speed)',
                        f'date, max(humidity), max(wind_speed), min(wind_speed)',
                        f'wind_speed, humidity'
                        ],
               'condition': ['city like "А%"',
                             'temp_min > 5',
                             None
                             ],
               'group': ['city',
                         'date',
                         None
                         ],
               'type': ['bar', 'hist', 'line']}
    # запрос на визуализацию данных
    for i in range(len(queries['cols'])):
        cols = queries['cols'][i]
        condition = queries['condition'][i]
        group = queries['group'][i]
        type = queries['type'][i]
        query(cols, condition, group, type)


main()
