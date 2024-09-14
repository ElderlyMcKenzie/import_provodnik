import datetime
from typing import List
import requests
import json
from enums import TransportType



def collect_routes(data, transport="train"):
    """
    Функция для сбора информации о маршрутах на основе входных данных.

    Parameters:
        data (list): Список входных данных о маршрутах.
        transport (str, optional): Тип транспорта (по умолчанию "train").

    Returns:
        list: Список маршрутов с информацией о поездках между указанными станциями.

    """
    # Инициализация списка для хранения маршрутов
    routes = []

    # Перебор элементов входных данных
    for entry in data:
        # Проверка наличия данных о поездках выбранного транспорта
        if not entry['dictionary'][transport]['voyages']:
            continue  # Пропуск итерации, если данные отсутствуют

        # Поиск маршрутов с пересадками
        for route_id, route_info in entry['dictionary']['common']['routes'].items():
            if route_info['segmentIds']:
                # Инициализация пересадочного маршрута
                transfer_route = {'segments': []}

                # Перебор сегментов маршрута
                for segment_id in route_info['segmentIds']:
                    segment = entry['dictionary']['common']['segments'][segment_id]
                    voyage_info = entry['dictionary'][transport]['voyages'][segment['voyageNumber']]

                    # Создание информации о сегменте маршрута
                    segment_info = {
                        'voyage_number': voyage_info['number'],  # Номер рейса
                        'stops': []  # Список остановок
                    }

                    # Добавление информации о каждой остановке
                    for stop in voyage_info['stops']:
                        stop_info = {
                            'name': stop['name'],  # Название остановки
                            'arrivalTime': stop['arrivalTime'],  # Время прибытия
                            'departureTime': stop['departureTime'],  # Время отправления
                            'stopDuration': stop['stopDuration']  # Продолжительность стоянки
                        }
                        segment_info['stops'].append(stop_info)

                    # Поиск цены для сегмента маршрута
                    for offer_id, offer_info in entry['offers']['actual'].items():
                        for offer_variant in offer_info['offerVariants']:
                            for segment_hash, fare_application in offer_variant['fareApplications'].items():
                                # Проверка, что хэш сегмента соответствует идентификатору текущего сегмента маршрута
                                if segment_hash == segment_id and offer_variant['price']['type'] != 'absent':
                                    # Если тип цены не равен "absent", обновляем цену для текущего сегмента маршрута
                                    segment_info['price'] = min(offer_variant['price']['value']['amount'], segment_info.get('price', 100000000))

                    # Добавление сегмента маршрута к пересадочному маршруту
                    if segment_info.get('price'):
                        transfer_route['segments'].append(segment_info)

                # Добавление пересадочного маршрута в список маршрутов
                if transfer_route['segments']:
                    routes.append(transfer_route)

    return routes  # Возврат списка маршрутов



def get_response(start_station, finish_station, date):
    """
    Функция для отправки запроса к API с информацией о начальной и конечной станции, а также дате отправления,
    с целью получения предложений о поездках по железной дороге.
    
    Parameters:
        start_station (str): Код начальной станции.
        finish_station (str): Код конечной станции.
        date (datetime.date): Дата отправления.
    
    Returns:
        str: Текст ответа от API с предложениями о поездках.
    """
    # Выводим дату запроса в консоль
    print(date)
    
    # Отправляем POST-запрос на API для получения предложений о поездках по железной дороге
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
                  
    # Проверяем успешность запроса по статусу ответа
    if response.status_code == 200:
        # Если запрос успешен, возвращаем текст ответа
        return response.text
    else:
        # Если запрос неудачен, возвращаем сообщение об ошибке с указанием статуса ответа
        return f"Error {response.status_code}: Unable to fetch the data."




def read_station_data_from_csv(file_path):
    """
    Функция для чтения данных о станциях из CSV файла.

    Parameters:
        file_path (str): Путь к CSV файлу.

    Returns:
        dict: Словарь данных о станциях, где ключи - названия станций, значения - коды станций.

    """
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



def main(start_station, finish_station, date: datetime.date, type: TransportType):
    """
    Основная функция программы для получения и обработки маршрутов между двумя станциями.

    Parameters:
        start_station (str): Название начальной станции.
        finish_station (str): Название конечной станции.
        date (datetime.date): Дата отправления.
        type (TransportType): Тип транспорта (например, поезд).

    Returns:
        list: Список маршрутов с информацией о поездках между указанными станциями.
    """
    # Чтение данных о станциях из CSV файла и преобразование в словарь
    station_name_to_number_dict = read_station_data_from_csv("routes.csv")
    
    # Глобальное сохранение словаря станций для последующего использования
    global stations
    stations = station_name_to_number_dict
    
    # Отправка запроса к API для получения предложений о поездках между станциями
    response_str = get_response(station_name_to_number_dict[start_station], station_name_to_number_dict[finish_station], date.strftime("%Y-%m-%d"))
    
    # Преобразование текстового ответа в формат JSON
    data = json.loads(response_str)
    
    # Вывод полученных маршрутов в консоль в виде отформатированного JSON
    print(json.dumps(collect_routes(data, type), indent=4, ensure_ascii=False))
    
    # Возвращение списка маршрутов
    return collect_routes(data, type)


stations: List = []


def suggest(sample: str):
    """
    Функция для предложения станций на основе введенного образца.

    Parameters:
        sample (str): Образец для поиска станций.

    Returns:
        list: Список станций, содержащих введенный образец.
    """
    result = []  # Инициализация списка для результатов
    if stations:  # Проверка наличия данных о станциях
        for station in stations:
            if sample.lower() in station.lower():  # Проверка соответствия образца названию станции
                result.append(station)  # Добавление станции в результаты
    return result  # Возврат списка станций, содержащих образец


main("Брянск", "Воркута", datetime.date.fromisoformat("2024-06-04"), TransportType.TRAIN)

