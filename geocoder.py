import requests, math, time

key = '62621221-4d79-48d0-83e1-f7b8aa92eca3'


def geocode(address):
    params = {'apikey': key, 'geocode': address, 'format': 'json'}
    response = requests.get('http://geocode-maps.yandex.ru/1.x/', params=params)
    if response:
        json_response = response.json()
    else:
        raise RuntimeError(f"""Ошибка выполнения запроса.
        Http статус: {response.status_code} ({response.reason})""")

    features = json_response['response']['GeoObjectCollection']['featureMember']
    return features[0]['GeoObject'] if features else None


def get_object_info(address):
    a = geocode(address)
    if not a:
        return (None, None)

    coordinates = a['Point']['pos']
    dolgota, shirota = coordinates.split()

    info = ','.join([dolgota, shirota])
    ramka = a['boundedBy']['Envelope']
    l, b = ramka['lowerCorner'].split()
    r, t = ramka['upperCorner'].split()

    span = f'{abs(float(l) - float(r)) / 2.0},{abs(float(t) - float(b)) / 2.0}'
    return info, span, a


def find_nearest_organization(point):
    all_org = {}

    print('Поиск..')
    for org_name in ['Магазин', 'Супермаркет', 'Заправка', 'Аптека', 'Ресторан', 'Кафе', 'Фастфуд', 'Банк', 'Больница',
                     'Поликлиника',
                     'Остановка', 'Школа', 'Университет', 'Детский сад', 'Почта', 'Метро']:
        search_params = {'apikey': 'dda3ddba-c9ea-4ead-9010-f43fbc15c6e3',
                         'text': org_name, 'lang': 'ru_RU', 'type': 'biz',
                         'll': '{0},{1}'.format(point[0], point[1]), 'results': 1}

        response = requests.get('https://search-maps.yandex.ru/v1/?', params=search_params)
        time.sleep(0.01)
        if response.json()['features']:
            f = response.json()['features'][0]['geometry']['coordinates']
            distance = lonlat_distance(point, f)
            if distance < 50:
                all_org[org_name] = [distance, f]

    try:
        nearest = sorted(all_org, key=lambda x: all_org[x][0])[0]
        obj = get_object_info(f'{all_org[nearest][1][0], all_org[nearest][1][1]}')

        a = obj[2]['metaDataProperty']['GeocoderMetaData']['Address']['Components']
        address = ', '.join(set(a[i]['name'] for i in range(len(a))))
        print(f'Поиск завершён успешно. Найдена "{nearest}".')
        return [all_org[nearest][1], address]
    except IndexError:
        print('Не найдено ничего поблизости.')
    return None


def lonlat_distance(a, b):
    degree_to_meters_factor = 111 * 1000
    a_lon, a_lat = a
    b_lon, b_lat = b

    radians_lattitude = math.radians((a_lat + b_lat) / 2.)
    lat_lon_factor = math.cos(radians_lattitude)

    dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
    dy = abs(a_lat - b_lat) * degree_to_meters_factor

    distance = math.sqrt(dx * dx + dy * dy)

    dx = abs(a_lon - b_lon) * 6371000 * math.pi / 180
    dy = abs(a_lat - b_lat) * 6371000 * math.pi / 180
    return distance
