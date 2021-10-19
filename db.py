import sqlite3
from sqlite3 import Error
import datetime
import sys
from PIL import Image
import io

create_poi_table_query = """
CREATE TABLE IF NOT EXISTS poi (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  chat_id INTEGER NOT NULL,
  address  TEXT,
  description TEXT,
  photo BLOB,
  location_lat  TEXT,
  location_lon TEXT,
  date_creation TEXT NOT NULL,
  time_creation TEXT NOT NULL
)
"""

insert_poi_query = """
INSERT INTO 
    poi (chat_id, address, description, photo, location_lat, location_lon, date_creation, time_creation)
    VALUES(?, ?, ?, ?, ?, ?, ?, ?)
"""

select_poi_query = """
SELECT address, description, photo, location_lat, location_lon, date_creation, time_creation
    FROM poi 
    WHERE chat_id = ? 
    ORDER BY id DESC
"""

delete_poi_query = """
DELETE FROM poi 
    WHERE chat_id = ? 
"""


def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path, check_same_thread=False)
        # print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection


def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        # print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")


def execute_query_with_param(connection, query, values):
    cursor = connection.cursor()
    try:
        cursor.execute(query, values)
        connection.commit()
        # print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")


def execute_read_query(connection, query, values, limit=1):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query, values)
        result = cursor.fetchmany(limit)
        # result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")


def read_image(filename):
    try:
        fin = open(filename, "rb")
        img = fin.read()
        # img = Image.open(filename)
        return img
    except IOError as e:
        # В случае ошибки, выводим ее текст
        print("Error %d: %s" % (e.args[0], e.args[1]))
        sys.exit(1)
    finally:
        if fin:
            # Закрываем подключение с файлом
            fin.close()


def resize_image(original_image):
    max_size = (320, 240)
    image = Image.open(io.BytesIO(original_image))
    image.thumbnail(max_size, Image.ANTIALIAS)
    # image.show()
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    small_image = img_byte_arr.read()
#    return small_image
    return sqlite3.Binary(small_image)


# connection = create_connection('poi.db')
# execute_query(connection, create_poi_table_query)
#
# chat_id = '12345678'
# chat_id = '454724133'

# address = 'Москва4'
# description = 'Хорошее место4'
# image = read_image('anypics.ru-5050-480.jpg')
# small_image = resize_image(image)
# photo = sqlite3.Binary(small_image)
# location_lat = '55.753707'
# location_lon = '37.62003'
# cur_date_time = datetime.datetime.now()
# cur_date = cur_date_time.date()
# cur_time = cur_date_time.time()
# date_creation = str(cur_date)
# time_creation = cur_time.strftime('%H:%M:%S')

# execute_query_with_param(connection, insert_poi_query,
# (chat_id, address, description, photo, location_lat, location_lon, date_creation, time_creation))

# execute_query_with_param(connection, delete_poi_query, (chat_id,))

# pois = execute_read_query(connection, select_poi_query, (chat_id,/), limit=1)

# for poi in pois:
#     print(poi[0], poi[1])

# poi = pois[0]
# print(poi[0], poi[1])
# photo = poi[2]
# fout = open('output1.jpg', 'wb')
# fout.write(photo)
# fout.close()
# print('OK')
