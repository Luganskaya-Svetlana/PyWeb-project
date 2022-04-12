from flask import url_for
from shutil import copy
import requests
import os.path

DEFAULT_DESSERT_MAP = "default_map_pic.jpg"


def if_country(country):
    try:
        response = requests.get(
            f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={country}&format=json")
        if response:
            json_response = response.json()
            return \
            json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["metaDataProperty"][
                "GeocoderMetaData"]["kind"] == 'country'
    except IndexError:
        return False
    return False


def map_image(country, id):
    if if_country(country):
        response = requests.get(f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={country}&format=json")
        if response:
            json_response = response.json()
            latitude, longitude = list(map(float, (
                json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"]).split()))
            response = requests.get(
                f"https://static-maps.yandex.ru/1.x/?ll={latitude},{longitude}&spn=25,25&l=map&pt={latitude},{longitude},pm2vvm")
            filename = f'{id}.jpg'
            url = url_for('static', filename="img/dessert_maps")[1:]
            with open(url+f'/{filename}', "wb") as file:
                file.write(response.content)
        else:
            url = url_for('static', filename=f"img")[1:]
            copy(url + f"/{DEFAULT_DESSERT_MAP}", url + f"/dessert_maps/{id}.jpg")




