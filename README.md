# PyWeb-project

Весь функционал взаимодействия программы с пользователем реализован в файле main.py - там находятся обработчики путей, а которые способен перейти по ссылкам пользователь. Там же расположены формы регистрации/авторизации пользователя, форма добавления десерта.

Остальной код, ответственный, в частности, за:
1) создание БД (файлы users.py, desserts.py, db_session, __all_models.py)
2) Работу с API Яндекс.Карты (проверка корректности ввода страны, отображение страны на карте; файл map.py)

Расположен в каталоге "data"

База данных располагается в каталоге "db"

Весь статический контент располагается в каталоге static - в частности, файлы css и папка img. 
В папке img содержатся стандартные аватарки и картинки десерта, фавикон и папки dessert_maps, dessert_photos, user_avatars - в них располагаются соответственно изображения карт, фото десертов и аватарки (имя файла соответствует id). Также в img содержится папка start_page - в ней лежат картинки, используемые при отображении стартовой страницы. 

Все используемые html-страницы располагаются в каталоге templates.

Реализован API для дальнейшего расширения функционала проекта - вся 
логика реализации сожержится в файле desserts_resources (применялась библиотека Flask-RESTful)

API предоставляет возможность получения информации о десертах в формате JSON.
Для получения информации об одном дессерте обратитесь по адресу
http://{адрес приложения}/dessert/{id_десерта}

Для получении информации о всех десертах обратитесь по адресу
http://{адрес приложения}/desserts

Дабы добавить новый десерт, отправьте POST-запрос по адресу
http://{адрес приложения}/desserts
С информацией о десерте. Оон должен содержать поля:

~ title

~ country

~ content

~ user_id


