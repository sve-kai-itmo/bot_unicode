import sys
import unicodedata
import telebot
from telebot import types
import param

def create_table():
    table = []
    symbol = ''
    symbol_code = ord(' ')
    end = min(0xD800, sys.maxunicode)

    while symbol_code < end:
        symbol_char = chr(symbol_code)
        symbol_name = unicodedata.name(symbol_char, 'unknown name')
        symbol += f'Символ: {symbol_char}\n'
        symbol += f'Дес. код: {symbol_code}\n'
        symbol += f'Шестн. код: {symbol_code:X}\n'
        symbol += f'Название: {symbol_name.title()}'
        table.append(symbol)
        symbol = ''
        symbol_code += 1
    return table

def match(key_list, entry):
    for key in key_list:
        if key not in entry:
            return False
    return True

def split_message(message):
    table = create_table()
    messages = []
    m = ''
    counter = 0
    for i in table:
        if match(message, i):
            m += i
            m += '\n\n'
            counter += 1
            if counter % 5 == 0:
                messages.append(m)
                m = ''
    if m != '':
        messages.append(m)
    return messages

def pages(message, current_page):
    keyboard = types.InlineKeyboardMarkup()
    buttons = []
    for i in range(len(message)):
        if i != current_page:
            buttons.append(types.InlineKeyboardButton(i, callback_data=str(i)))
    keyboard.add(*buttons)
    return keyboard


bot = telebot.TeleBot(param.TG_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def print_help(message):
    help_message = '''Отправь английское название символа Unicode, а я его найду и выведу сам символ, его кодировку и полное название.'''
    bot.send_message(message.chat.id, help_message)

@bot.message_handler(content_types=['text'])
def print_table(message):
    global text
    text = message.text.title().split()
    text = split_message(text)
    current_page = 0
    bot.send_message(message.chat.id, text[current_page], reply_markup=pages(text, current_page))

@bot.callback_query_handler(lambda call: True)
def turn_pages(call):
    current_page = int(call.data)
    keyboard = pages(text, current_page)
    bot.edit_message_text(text[current_page], call.message.chat.id, call.message.message_id, reply_markup=keyboard)

bot.polling(none_stop=True)