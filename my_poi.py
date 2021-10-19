import telebot
from telebot import types
import datetime

import settings
import db

connection = ''
chat_ids = {}
bot = telebot.TeleBot(settings.TOKEN_TELEGRAMM_POI)


def create_keyboard_count():
    keyboard = types.InlineKeyboardMarkup()
    key_1 = types.InlineKeyboardButton(text='1', callback_data='1')
    key_5 = types.InlineKeyboardButton(text='5', callback_data='5')
    key_10 = types.InlineKeyboardButton(text='10', callback_data='10')
    keyboard.row(key_1, key_5, key_10)
    return keyboard


def create_keyboard_input_poi():
    keyboard = types.InlineKeyboardMarkup()
    key_address = types.InlineKeyboardButton(text='Адрес', callback_data='address')
    key_description = types.InlineKeyboardButton(text='Описание', callback_data='description')
    key_photo = types.InlineKeyboardButton(text='Фото', callback_data='photo')
    key_location = types.InlineKeyboardButton(text='Локация', callback_data='location')
    key_save = types.InlineKeyboardButton(text='Сохранить', callback_data='save')
    key_notsave = types.InlineKeyboardButton(text='Отмена', callback_data='notsave')

    # keyboard.add(key_address)
    # keyboard.add(key_photo)
    # keyboard.add(key_description)
    # keyboard.add(key_location)
    # keyboard.add(key_save)

    keyboard.row(key_address, key_description)
    keyboard.row(key_photo, key_location)
    keyboard.row(key_save)
    keyboard.row(key_notsave)

    return keyboard


@bot.message_handler(commands=['start'])
def start_command(message):
    text = 'Привет!\n' + \
           'Этот бот уменеет запоминать интересные места\n' + \
           'Выберите команду из списка или нажмите /help'

    bot.send_message(chat_id=message.chat.id, text=text)


@bot.message_handler(commands=['help'])
def help_command(message):
    text = 'Используйте следующие команды\n' + \
           '/add - Добавить новое место\n' + \
           '/list - Показать мои места\n' + \
           '/reset - Удалить все добавленные места'

    bot.send_message(chat_id=message.chat.id, text=text)


@bot.message_handler(commands=['add'])
# @bot.message_handler(func=chek_currency)
def add_command(message):
    # text = 'Выбрана команда /add'
    # bot.send_message(chat_id=message.chat.id, text=text)
    chat_id = message.chat.id
    chat_ids[chat_id] = {}
    clear_input_state(chat_id)
    chat_ids[chat_id]['is_input_poi'] = True
    # print(chat_ids)

    keyboard = create_keyboard_input_poi()
    text = 'Заполните все или некоторые данные и нажмите Сохранить'
    bot.send_message(chat_id=message.chat.id, text=text, reply_markup=keyboard)


@bot.message_handler(commands=['list'])
def list_command(message):
    # text = 'Выбрана команда /list'
    # bot.send_message(chat_id=message.chat.id, text=text)
    keyboard = create_keyboard_count()
    text = 'Сколько точек показать?'
    bot.send_message(chat_id=message.chat.id, text=text, reply_markup=keyboard)


@bot.message_handler(commands=['reset'])
def reset_command(message):
    chat_id = message.chat.id
    db.execute_query_with_param(connection, db.delete_poi_query, (chat_id,))
    text = 'Выбрана команда /reset Все Ваши места удалены'
    bot.send_message(chat_id=message.chat.id, text=text)


@bot.message_handler(content_types=['location'])
def send_location_command(message):
    chat_id = message.chat.id
    if chat_id not in chat_ids or not chat_ids[chat_id]['is_input_poi']:
        bot.send_message(chat_id=message.chat.id, text='Вначале выберите команду из списка')
        return

    print(message.location)
    print(message.location.latitude)
    print(message.location.longitude)
    chat_ids[chat_id]['location_lat'] = message.location.latitude
    chat_ids[chat_id]['location_lon'] = message.location.longitude

    print('Локация принята')


@bot.message_handler(content_types=['photo'])
def send_photo_command(message):
    chat_id = message.chat.id
    if chat_id not in chat_ids or not chat_ids[chat_id]['is_input_poi']:
        bot.send_message(chat_id=message.chat.id, text='Вначале выберите команду из списка')
        return

    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    rphoto = db.resize_image(downloaded_file)
    chat_ids[chat_id]['photo'] = rphoto
    print('Фото принято')


@bot.message_handler()
def handle_message(message):
    # print(message.text)
    chat_id = message.chat.id
    if chat_id not in chat_ids or not chat_ids[chat_id]['is_input_poi']:
        bot.send_message(chat_id=message.chat.id, text='Выберите команду из списка')
    elif chat_ids[chat_id]['input_poi_step'] == 'address':
        chat_ids[chat_id]['address'] = message.text
    # elif chat_ids[chat_id]['input_poi_step'] == 'photo':
    #     photo = message.image
    #     rphoto = db.resize_image(photo)
    #     chat_ids[chat_id]['photo'] = rphoto
    elif chat_ids[chat_id]['input_poi_step'] == 'description':
        chat_ids[chat_id]['description'] = message.text
    # elif chat_ids[chat_id]['input_poi_step'] == 'location':
    #     chat_ids[chat_id]['location_lat'] = message.location['latitude']
    #     chat_ids[chat_id]['location_lon'] = message.location['longitude']

    # print(chat_ids)


@bot.callback_query_handler(func=lambda x: True)
def callback_worker(callback_query):
    input_poi_step = callback_query.data
    message = callback_query.message
    chat_id = message.chat.id

    if callback_query.data in ['1', '5', '10']:
        pois = db.execute_read_query(connection, db.select_poi_query, (chat_id,), limit=int(callback_query.data))
        if len(pois) == 0:
            bot.send_message(chat_id=message.chat.id, text='Ничего нет')
            return
        # text = f'Показываю {callback_query.data} мест'
        # bot.send_message(chat_id=message.chat.id, text=text)
        for poi in pois:
            text = f'Сохранено {poi[5]} в {poi[6]}'
            bot.send_message(chat_id=message.chat.id, text=text)
            bot.send_message(chat_id=message.chat.id, text=poi[0])
            if poi[1]:
                bot.send_message(chat_id=message.chat.id, text=poi[1])
            # print(poi[0], poi[1])
            photo = poi[2]
            if photo:
                bot.send_photo(chat_id, photo)
            if poi[3] and poi[3]:
                bot.send_location(chat_id, poi[3], poi[4])
        return

    chat_ids[chat_id]['input_poi_step'] = input_poi_step

    if input_poi_step == 'address':
        bot.send_message(chat_id=message.chat.id, text='Введите адрес :')
    if input_poi_step == 'photo':
        bot.send_message(chat_id=message.chat.id, text='Добавьте фото :')
    if input_poi_step == 'description':
        bot.send_message(chat_id=message.chat.id, text='Введите описание :')
    if input_poi_step == 'location':
        bot.send_message(chat_id=message.chat.id, text='Добавьте локацию :')
    if input_poi_step == 'save':
        if not chat_ids[chat_id]['address']:
            bot.send_message(chat_id=message.chat.id, text='Адрес не может быть пустым')
            return
        save_poi(chat_id)
        bot.send_message(chat_id=message.chat.id, text='Место сохранено')
    if input_poi_step == 'notsave':
        notsave_poi(chat_id)
        bot.send_message(chat_id=message.chat.id, text='Место не сохранено')


def clear_input_state(chat_id):
    chat_ids[chat_id]['is_input_poi'] = False
    chat_ids[chat_id]['input_poi_step'] = ''
    chat_ids[chat_id]['address'] = ''
    chat_ids[chat_id]['photo'] = ''
    chat_ids[chat_id]['description'] = ''
    chat_ids[chat_id]['location_lat'] = ''
    chat_ids[chat_id]['location_lon'] = ''


def save_poi(chat_id):
    # print(chat_ids[chat_id])
    cur_date_time = datetime.datetime.now()
    cur_date = cur_date_time.date()
    cur_time = cur_date_time.time()
    date_creation = str(cur_date)
    time_creation = cur_time.strftime('%H:%M:%S')
    db.execute_query_with_param(connection, db.insert_poi_query,
    (chat_id, chat_ids[chat_id]['address'], chat_ids[chat_id]['description'], chat_ids[chat_id]['photo'], chat_ids[chat_id]['location_lat'], chat_ids[chat_id]['location_lon'], date_creation, time_creation))

    clear_input_state(chat_id)


def notsave_poi(chat_id):
    # print(chat_ids[chat_id])
    clear_input_state(chat_id)


def main():
    global connection
    connection = db.create_connection('poi.db')
    db.execute_query(connection, db.create_poi_table_query)

    print('Start')
    bot.polling()


if __name__ == '__main__':
    main()

'''
{ chat_id: text, 
            {
            is_input_poi: True\False,
            input_poi_step: text,
            address:
            photo:
            description:
            location_lat:                    
            location_lon:
            }

}
'''
