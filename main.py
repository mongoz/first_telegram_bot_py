import telebot

API_TOKEN = '1826894325:AAFbdkJPrUSfQ9rP5oap20tASUXXvZsNczs'
shop_list_bot = telebot.TeleBot(API_TOKEN)
last_message_id = None

# telebot.types.ReplyKeyboardMarkup   чтобы появились кнопки, чтобы была логика
# telebot.types.ReplyKeyboardMarkup

command = ["Добавить в список", "Показать список", "Удалить из списка"]
key_boards = telebot.types.ReplyKeyboardMarkup()
key_boards.row(*command)

shop_list = []
current_op = None  # Текущая операция 'добавить'.'показать'


# Логика
# 1. Прописываем команду старт
@shop_list_bot.message_handler(commands=['start'])
def start(message):
    # передаем reply_markup, как параметр. не просто приветсвие, но и поле для навигации
    shop_list_bot.reply_to(message, "Привет, дорогой!", reply_markup=key_boards)


# Команды бота для списка(добавить. показать. удалить)
@shop_list_bot.message_handler(content_types=['text'])
def commands(message):
    global current_op  # Почему глобал потому что будем менять в процессе написания
    global shop_list  # Почему глобал потому что будем менять в процессе написания
    global last_message_id
    if message.text == "Добавить в список":
        current_op = 'добавить'
        shop_list_bot.reply_to(message, "Теперь добавьте продукты в список")
    elif message.text == 'Показать список':
        current_op = 'показать'                              # если лист пустой то вернет ' ' пустую строку
        shop_list_bot.reply_to(message, ", ".join(shop_list)if shop_list else '')  # сообщение кленту, когда он
        # запросил показать что в списке. метод .join достает элементы из списка и записывает их через запятую
    elif message.text == "Удалить из списка":
        current_op = 'удалить'
        key_boards_rm = telebot.types.InlineKeyboardMarkup()  # Кнопка удалить
        for elem in shop_list:
            key_boards_rm.add(telebot.types.InlineKeyboardButton(elem, callback_data=elem))  # когда мы клацаем на
            # элемент  он выделяется
        response = shop_list_bot.reply_to(message, "Теперь вы можете удалить елементы", reply_markup=key_boards_rm)
        last_message_id = response.message_id  # чтобы потом потом можно было удалить
    else:
        if current_op == "добавить":
            shop_list.append(message.text)
            shop_list_bot.reply_to(message, f"успешно добавлено {message.text}")


@shop_list_bot.callback_query_handler(func=lambda x: True)  # лямбдой говорим что будем всегда заходить в этот декоратор
def callback_handler(call):  # а зайду я когда нажму на элемент. потому что есть режим сallback_data
    global shop_list
    index_remove = None
    for i in range(len(shop_list)):  # удаляем по индексу
        if shop_list[i] == call.data:
            index_remove = i
            break
    if index_remove is not None:
        del shop_list[index_remove]

    key_boards_rm = telebot.types.InlineKeyboardMarkup()  # Кнопка удалить
    for elem in shop_list:
        key_boards_rm.add(telebot.types.InlineKeyboardButton(elem, callback_data=elem))
        # Чтобы обновить структуру(markup), где указаны элементы нужно знать id-cообщения(удалить из листа).
    shop_list_bot.edit_message_reply_markup(call.message.chat.id, last_message_id, reply_markup=key_boards_rm)


shop_list_bot.polling()
