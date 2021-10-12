import telebot
token = '2009877076:AAHhpG8YNtcJpVEQQldWCBWjMCEfNmKjlCQ'

bot = telebot.TeleBot(token)

currencies = ['евро', 'доллар']


def chek_currency(message):
    for c in currencies:
        if c in message.text.lower():
            return True
    return False


@bot.message_handler(commands=['rate'])
@bot.message_handler(func=chek_currency)
def handle_message(message):
    currency = 'евро'
    value = 70
    text = f'Курс {currency} равен {value}'
    bot.send_message(chat_id=message.chat.id, text=text)


@bot.message_handler()
def handle_message(message):
    print(message.text)
    bot.send_message(chat_id=message.chat.id, text='Проверка')


bot.polling()
