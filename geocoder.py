import requests

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


def get_coordinates(address):
    a = geocode(address)
    if not a:
        return None, None
    coordinates = a['Point']['pos']
    print(coordinates)
    dolgota, shirota = coordinates.split()
    return float(dolgota), float(shirota)


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


def get_nearest_object(point, kind):
    info = '{0},{1}'.format(point[0], point[1])
    geocoder_params = {'apikey': key, 'geocode': info, 'format': 'json'}
    if kind:
        geocoder_params['kind'] = kind

    response = requests.get('http://geocode-maps.yandex.ru/1.x/', params=geocoder_params)
    if not response:
        raise RuntimeError(f"""Ошибка выполнения запроса. 
        Http статус: {response.status_code,} ({response.reason})""")

    json_response = response.json()
    features = json_response['response']['GeoObjectCollection']['featureMember']
    return features[0]['GeoObject']['name'] if features else None
