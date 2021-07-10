import telebot
import flask
import time

API_TOKEN = '1826894325:AAFbdkJPrUSfQ9rP5oap20tASUXXvZsNczs'
shop_list_bot = telebot.TeleBot(API_TOKEN)

app = flask.Flask(__name__)

WEBHOOK_HOST = 'ae9a342eb9c4.ngrok.io'
WEBHOOK_PORT = 8088  # 443, 80, 88 or 8443 (port need to be 'open')
WEBHOOK_LISTEN = '0.0.0.0'  # In some VPS you may need to put here the IP address

WEBHOOK_URL_BASE = "https://%s" % WEBHOOK_HOST
WEBHOOK_URL_PATH = "/%s/" % API_TOKEN

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


# индекс страниц
@app.route('/', methods=['GET', 'HEAD'])
def index():
    print("index")
    return 'Привет!'


# Process webhook calls
@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        shop_list_bot.process_new_updates([update])  #
        return ''
    else:
        flask.abort(403)


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
        shop_list_bot.reply_to(message,
                               ", ".join(user_data[message.chat.id][0]) if user_data[message.chat.id][0] else 'empty')
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
    shop_list_bot.edit_message_reply_markup(call.message.chat.id, user_data[call.message.chat.id][2],
                                            reply_markup=key_boards_rm)


# shop_list_bot.polling()
# При перезапуске программы может сохраниться старый веб хук и тогда API cкажет что он ещё есть
# зачем тебе опять веб хук и соответсвенно чтобы не было конфликта нужно удалить
shop_list_bot.remove_webhook()
time.sleep(0.1)  # ничего не делаем на протяжении 0.1 сек

# Set webhook
shop_list_bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH)  # !!!!подпись на веб хук

app.run(host="localhost", port=8088)  # бег по хосту

# после пробы работы для мульти-юзера  не добавляет в список
# ошибка была , что поставил неправильный индекс словаря в 59 строке
# проблема не удаляет из списка. просто пропадает
# в 79 строке пропустил мусорную переменную из-за этого условие не срабатывало
# user_data это словарь и он изменяемый. поэтому если там есть ключик мы просто
# добавил ссылку ввиде 'add'
# Как сделать бот без polling
# shop_list_bot.polling() - API - server . потом сервер что-то отвечал
# развернуть на сервере для этого нужен фреймворк и какой-то ресурс.
# ресурс ngrok и фреймворк фласк

