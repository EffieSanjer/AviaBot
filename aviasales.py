from datetime import datetime

import requests

from config_reader import config

headers = {
    'X-Access-Token': config.aviasales_token.get_secret_value(),
    'Accept-Encoding': 'gzip, deflate'
}

airlines = {}
for airline in requests.get('https://api.travelpayouts.com/data/ru/airlines.json').json():
    airlines[airline['code']] = airline['name']

airports = {}
for airport in requests.get('https://api.travelpayouts.com/data/ru/airports.json').json():
    airports[airport['code']] = airport['name']

cities = {}
for city in requests.get('https://api.travelpayouts.com/data/ru/cities.json').json():
    cities[city['code']] = city['name']


def get_airport(airport_code):
    return airport_code in airports


def get_airlines(airline_code):
    return airline_code in airlines


def get_prices_for_dates(*kwargs):
    tg_response = ''
    params = kwargs[0]
    params['limit'] = 10

    data = requests.get(f'https://api.travelpayouts.com/aviasales/v3/prices_for_dates',
                        params=params,
                        headers=headers)

    if not data.json().get('data', None):
        return 'Ничего не найдено'

    for ticket in data.json()['data']:
        tg_response += f"Аэропорт вылета: {airports[ticket['origin']]}\n"
        tg_response += f"Аэропорт прилета: {airports[ticket['destination']]}\n"
        # tg_response += f"Рейс: {ticket['flight_number']}\n"
        tg_response += f"Цена: {ticket['price']} руб\n"
        tg_response += f"Вылет: {datetime.fromisoformat(ticket['departure_at']).strftime('%d.%m.%Y %H:%M')}\n"
        tg_response += f"Авиакомпания: {airlines[ticket['airline']]}\n\n"

    return tg_response
