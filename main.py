import telebot

API_TOKEN = '1826894325:AAFbdkJPrUSfQ9rP5oap20tASUXXvZsNczs'
shop_list_bot = telebot.TeleBot(API_TOKEN)

# telebot.types.ReplyKeyboardMarkup   чтобы появились кнопки для юзера
# telebot.types.ReplyKeyboardMarkup

command = ["Добавить в список", "Показать список", "Удалить из списка"]
key_boards = telebot.types.ReplyKeyboardMarkup()
key_boards.row(*command)

# chat_id = {shop_list, current_op, last_message_id}
shop_list = []
# current_op = None  # Текущая операция 'добавить'.'показать'
# last_message_id = None

# словарь нужен, если появляется новый юзер то мы будем обновлять данные
user_data = {}


# Логика
# 1. Прописываем команду старт. она ответит сообщением
@shop_list_bot.message_handler(commands=['start'])
def start(message):
    # передаем reply_markup, как параметр. не просто приветсвие, но и поле для навигации
    shop_list_bot.reply_to(message, "Привет, дорогой!", reply_markup=key_boards)


# Команды бота для списка(добавить. показать. удалить)
@shop_list_bot.message_handler(content_types=['text'])
def commands(message):
    # global current_op  # Почему глобал потому что будем менять в процессе написания
    # global shop_list  # Почему глобал потому что будем менять в процессе написания
    # global last_message_id
    print(user_data)
    if message.chat.id not in user_data:
        user_data[message.chat.id] = [[], None, None]  # значением будет список
    if message.text == "Добавить в список":
        user_data[message.chat.id][1] = 'добавить'
        # current_op = 'добавить'
        shop_list_bot.reply_to(message, "Теперь добавьте продукты в список")
    elif message.text == 'Показать список':
        user_data[message.chat.id][1] = 'показать'
        # current_op = 'показать'  # если лист пустой то вернет ' ' пустую строку
        shop_list_bot.reply_to(message, ", ".join(user_data[message.chat.id][0]) if user_data[message.chat.id][0] else 'empty')
        # сообщение кленту, когда он
        # запросил показать что в списке. метод .join достает элементы из списка и записывает их через запятую
        # если что-то есть нулевым элементом мы это покажем если нет, то не покажем(или покажем сообщение )
    elif message.text == "Удалить из списка":
        user_data[message.chat.id][1] = 'удалить'
        # current_op = 'удалить'
        key_boards_rm = telebot.types.InlineKeyboardMarkup()  # Кнопка удалить
        for elem in user_data[message.chat.id][0]:
            key_boards_rm.add(telebot.types.InlineKeyboardButton(elem, callback_data=elem))  # когда мы клацаем на
            # элемент  он выделяется
        response = shop_list_bot.reply_to(message, "Теперь вы можете удалить элементы", reply_markup=key_boards_rm)
        user_data[message.chat.id][2] = response.message_id  # чтобы потом потом можно было удалить
        # информация персонализирована под человека
    else:
        if user_data[message.chat.id][1] == "добавить":
            user_data[message.chat.id][0].append(message.text)
            shop_list_bot.reply_to(message, f"успешно добавлено {message.text}")


@shop_list_bot.callback_query_handler(func=lambda x: True)  # лямбдой говорим что будем всегда заходить в этот декоратор
def callback_handler(call):  # а зайду я когда нажму на элемент. потому что есть режим сallback_data
    # global shop_list
    index_remove = None
    for i in range(len(user_data[call.message.chat.id][0])):  # удаляем по индексу
        if user_data[call.message.chat.id][0][i] == call.data:
            index_remove = i
            break
    if index_remove is not None:
        del user_data[call.message.chat.id][0][index_remove]

    key_boards_rm = telebot.types.InlineKeyboardMarkup()  # Кнопка удалить
    for elem in shop_list:
        key_boards_rm.add(telebot.types.InlineKeyboardButton(elem, callback_data=elem))
        # Чтобы обновить структуру(markup), где указаны элементы нужно знать id-cообщения(удалить из листа).
    shop_list_bot.edit_message_reply_markup(call.message.chat.id, user_data[call.message.chat.id][2], reply_markup=key_boards_rm)


shop_list_bot.polling()


# после пробы работы для мульти-юзера  не добавляет в список
# ошибка была , что поставил неправильный индекс словаря в 59 строке
# проблема не удаляет из списка. просто пропадает
# в 79 строке пропустил мусорную переменную из-за этого условие не срабатывало
# user_data это словарь и он изменяемый. поэтому если там есть ключик мы просто
# добавил ссылку ввиде 'add'