import random

import config
import telebot, wikipedia, re
import os
from fuzzywuzzy import fuzz
from telebot import types
import time
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import  requests
from bs4 import BeautifulSoup as b


bot = telebot.TeleBot(config.token)
############################# МОДУЛЬ WIKI ################################################
# Устанавливаем русский язык в Wikipedia
wikipedia.set_lang("ru")
# Чистим текст статьи в Wikipedia и ограничиваем его тысячей символов
def getwiki(s):
    try:
        ny = wikipedia.page(s)
        # Получаем первую тысячу символов
        wikitext=ny.content[:1000]
        # Разделяем по точкам
        wikimas=wikitext.split('.')
        # Отбрасываем всЕ после последней точки
        wikimas = wikimas[:-1]
        # Создаем пустую переменную для текста
        wikitext2 = ''
        # Проходимся по строкам, где нет знаков «равно» (то есть все, кроме заголовков)
        for x in wikimas:
            if not('==' in x):
                    # Если в строке осталось больше трех символов, добавляем ее к нашей переменной и возвращаем утерянные при разделении строк точки на место
                if(len((x.strip()))>3):
                   wikitext2=wikitext2+x+'.'
            else:
                break
        # Теперь при помощи регулярных выражений убираем разметку
        wikitext2=re.sub('\([^()]*\)', '', wikitext2)
        wikitext2=re.sub('\([^()]*\)', '', wikitext2)
        wikitext2=re.sub('\{[^\{\}]*\}', '', wikitext2)
        # Возвращаем текстовую строку
        return wikitext2
    # Обрабатываем исключение, которое мог вернуть модуль wikipedia при запросе
    except Exception as e:
        return 'В энциклопедии нет информации об этом'

 ################################################## МОДУЛЬ ДИАЛОГА #########################################################################
# Загружаем список фраз и ответов в массив
mas = []
if os.path.exists('data/boltun.txt'):
    f = open('data/boltun.txt', 'r', encoding='UTF-8')
    for x in f:
        if (len(x.strip()) > 2):
            mas.append(x.strip().lower())
    f.close()


# С помощью fuzzywuzzy вычисляем наиболее похожую фразу и выдаем в качестве ответа следующий элемент списка
def answer(text):
    try:
        text = text.lower().strip()
        if os.path.exists('data/boltun.txt'):
            a = 0
            n = 0
            nn = 0
            for q in mas:
                if ('u: ' in q):
                    # С помощью fuzzywuzzy получаем, насколько похожи две строки
                    aa = (fuzz.token_sort_ratio(q.replace('u: ', ''), text))
                    if (aa > a and aa != a):
                        a = aa
                        nn = n
                n = n + 1
            s = mas[nn + 1]
            return s
        else:
            return 'Умный дохуя? я такого еще не знаю'
    except:
        return 'Умный дохуя? я такого еще не знаю'


####################################################ЦИТАТЫ ГОБЛИНА####################################################
URL = 'https://bbf.ru/quotes/?author=34102'
def parser(url):
    r = requests.get(url)
    soup = b(r.text, 'html.parser')
    anekdots = soup.find_all('div', class_='sentence__body')
    return [c.text for c in anekdots]

def list_of_j(message):
    if message.text in '1234567890':
        msg = int(message.text)
        list_of_jokes = parser(URL)
        random.shuffle(list_of_jokes)
        bot.send_message(message.chat.id, list_of_jokes[msg] + "\n (C) Дмитрий Юрьевич Пучков")
        del list_of_jokes[msg]
        bot.register_next_step_handler(message, list_of_j)
    elif message.text == "стоп":
        bot.send_message(message.chat.id, 'Пока.')
    else:
        bot.send_message(message.chat.id, 'Введи либо цифрцу,либо стоп, от тебя другого тут не требуется')


######################################################################################################################


@bot.message_handler(commands=['start'])
def welcome_start(message):
    bot.send_message(message.chat.id, 'Приветствую тебя ' + message.from_user.first_name + '! Я бот Тохсырорв! \n И пока что я имею несколько функций поиск, общение и цитирывание Дим Юрича Гоблина \n Для того чтобы что-то найти введи - Найти \n Для того чтобы пообщаться введди - Общение \n Для того что бы тебе малолетнему дебилу почитать цитаты гоблина введи -Цитаты' )
    # keyboard = types.InlineKeyboardMarkup()
    # key_telec = types.InlineKeyboardButton(text='Поиск')
    # keyboard.add(key_telec)

@bot.message_handler(commands=['help'])
def welcome_help(message):
    bot.send_message(message.chat.id, 'Чем я могу тебе помочь? Ничем, запусти меня заново (пропиши /start)')


@bot.message_handler(content_types=["text"])
def get_text(message):
    if message.text == "Найти":
        bot.send_message(message.chat.id, 'Введи нужную информацию для поиска. \n Если все нашел, тогда напиши - стоп')
        bot.register_next_step_handler(message, handle_text)
    elif  message.text == "Цитаты":
        bot.send_message(message.chat.id, 'Категорически приветствую. Напиши мне любую цифру. \n Если захочешь прекратить  напиши - стоп')
        bot.register_next_step_handler(message, list_of_j)
    elif message.text == "Общение":
        bot.send_message(message.chat.id, 'Напиши мне привет. \n Если захочешь прекратить разговор напиши - стоп')
        bot.register_next_step_handler(message, handle_text2)





def handle_text(message):
    msg = message.text
    if msg == "стоп":
        bot.send_message(message.chat.id, 'Поиск окончен')
    else:
        bot.send_message(message.chat.id, getwiki(msg))
        bot.register_next_step_handler(message, handle_text)

def handle_text2(message):
        # Запись логов
        msg = message.text
        f = open('data/' + str(message.chat.id) + '_log.txt', 'a', encoding='UTF-8')
        s = answer(msg)
        f.write('u: ' + msg + '\n' + s + '\n')
        f.close()
        if msg == "стоп":
            bot.send_message(message.chat.id, 'Пока.Спасибо за беседу!')
        else:
            # Отправка ответа
            bot.send_message(message.chat.id, s)
            bot.register_next_step_handler(message, handle_text2)





# @bot.message_handler(commands=['wiki'])
# def welcome_wiki(message):
#     bot.send_message(message.chat.id, 'Введи нужную информацию для поиска')
#     @bot.message_handler(content_types=["text"])
#     def handle_text(message):
#            bot.send_message(message.chat.id, getwiki(message.text))
#
# @bot.message_handler(commands=['raz'])
# def welcome_raz(message):
#     bot.send_message(message.chat.id, 'Напиши мне привет и начнем общение')
#
#     def handle_text2(message):
#         # Запись логов
#         f = open('data/' + str(message.chat.id) + '_log.txt', 'a', encoding='UTF-8')
#         s = answer(message.text)
#         f.write('u: ' + message.text + '\n' + s + '\n')
#         f.close()
#         # Отправка ответа
#         bot.send_message(message.chat.id, s)


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
     # bot.infinity_polling()