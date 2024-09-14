import datetime
from typing import List

import requests
import json

from enums import TransportType


def collect_routes(data, transport="train"):
    routes = []

    if not data[0]['dictionary'][transport]['voyages']:
        return []

    for voyage_id, voyage_info in data[0]['dictionary'][transport]['voyages'].items():
        route = {
            'voyage_number': voyage_info['number'],
            'stops': []
        }
        for stop in voyage_info['stops']:
            stop_info = {
                'name': stop['name'],
                'arrivalTime': stop['arrivalTime'],
                'departureTime': stop['departureTime'],
                'stopDuration': stop['stopDuration']
            }
            route['stops'].append(stop_info)
        routes.append(route)

    # Check for routes with transfers
    for route_id, route_info in data[1]['dictionary']['common']['routes'].items():
        if route_info['segmentIds'] and len(route_info['segmentIds']) > 1:
            transfer_route = {
                'route_id': route_id,
                'segments': []
            }
            for segment_id in route_info['segmentIds']:
                segment = data[0]['dictionary']['common']['segments'][segment_id]
                voyage_info = data[0]['dictionary'][transport]['voyages'][segment['voyageNumber']]
                segment_info = {
                    'voyage_number': voyage_info['number'],
                    'departure': segment['departureDateTime'],
                    'arrival': segment['arrivalDateTime'],
                    'duration': segment['duration'],
                    'stops': []
                }
                for stop in voyage_info['stops']:
                    stop_info = {
                        'name': stop['name'],
                        'arrivalTime': stop['arrivalTime'],
                        'departureTime': stop['departureTime'],
                        'stopDuration': stop['stopDuration']
                    }
                    segment_info['stops'].append(stop_info)
                transfer_route['segments'].append(segment_info)
            routes.append(transfer_route)

    return routes

def get_response(start_station, finish_station, date):
    print(date)
    response = requests.post("https://offers-api.tutu.ru/railway/offers",
                  json={
                      "routes": [
                        {
                          "departureStationCode": start_station,
                          "arrivalStationCode": finish_station,
                          "departureDate": date
                        }
                      ],
                      "flags": [
                        {
                          "name": "interchangeOffersStrategy",
                          "value": "ON_EMPTY_DIRECT_SEARCH"
                        },
                        {
                          "name": "possibleOffersEnabled",
                          "value": "ENABLED"
                        }
                      ],
                      "source": "trainOffers"
                    }
                  )
    if response.status_code == 200:
        return (response.text)
    else:
        return (f"Error {response.status_code}: Unable to fetch the data.")




def read_station_data_from_csv(file_path):
    import csv

    # Создаем пустой словарь для хранения данных о станциях
    station_data = {}

    # Открываем файл для чтения
    with open(file_path, mode='r', encoding='utf-8') as csv_file:
        # Используем csv.reader для чтения данных из файла
        csv_reader = csv.reader(csv_file, delimiter=';')
        next(csv_reader)  # Пропускаем заголовок
        for row in csv_reader:
            # Добавляем данные о станциях в словарь
            # Название станции отправления
            station_data[row[1]] = row[0]
            # Название станции прибытия
            station_data[row[3]] = row[2]
    return station_data


def get_voyage_prices(data):
    prices = {}
    for offer_id, offer_info in data[1]['offers']['actual'].items():
        for offer_variant in offer_info['offerVariants']:
            for segment_hash, fare_application in offer_variant['fareApplications'].items():
                for fare_id in fare_application:
                    segment = data[1]['dictionary']['common']['segments'][segment_hash]
                    voyage_number = segment['voyageNumber']
                    prices[voyage_number] = offer_variant['price']['value']['amount']
    return prices


def main(start_station, finish_station, date: datetime.date, type: TransportType):
    station_name_to_number_dict = read_station_data_from_csv("routes.csv")
    #print(station_name_to_number_dict)

    global stations
    stations = station_name_to_number_dict

    response_str = get_response(station_name_to_number_dict[start_station], station_name_to_number_dict[finish_station], date.strftime("%Y-%m-%d"))
    data = json.loads(response_str)
    print(get_voyage_prices(data))
    print(collect_routes(data, type))
    return (collect_routes(data, type))


stations: List = []


def suggest(sample: str):
    result = []
    if stations:
        for station in stations:
            if sample.lower() in station.lower():
                result.append(station)
    return result


main("Брянск", "Москва", datetime.date.fromisoformat("2024-06-03"), TransportType.TRAIN)

