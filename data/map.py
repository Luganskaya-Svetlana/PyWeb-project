import os
import pygame
import requests


def if_country(country):
    try:
        response = requests.get(
            f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={country}&format=json")
        if response:
            json_response = response.json()
            return json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["metaDataProperty"][
                       "GeocoderMetaData"]["kind"] == 'country'
    except IndexError:
        return False
    return False


def map_image(country):
    if if_country(country):
        response = requests.get(f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={country}&format=json")
        if response:
            json_response = response.json()
            latitude, longitude = list(map(float, (
                json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"]).split()))
            response = requests.get(
                f"https://static-maps.yandex.ru/1.x/?ll={latitude},{longitude}&spn=25,25&l=map&pt={latitude},{longitude},pm2vvm")
            return response.content
        print("Http статус:", response.status_code, "(", response.reason, ")")


'''Для тестирования'''
if __name__ == '__main__':
    print(if_country(''))
    print(if_country('-'))
    print(if_country('россия'))
    print(if_country('Австралия'))
#     map_file1 = "map1.png"
#     with open(map_file1, "wb") as file:
#         file.write(map_image('Италия'))
#
#     pygame.init()
#     screen = pygame.display.set_mode((600, 450))
#     screen.blit(pygame.image.load(map_file1), (0, 0))
#     pygame.display.flip()
#     running = True
#     while running:
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 running = False
#         pygame.display.flip()
#
#     pygame.quit()
#     os.remove(map_file1)

