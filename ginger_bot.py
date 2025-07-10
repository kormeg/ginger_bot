# import sys
# # sys.path.append("D:/code/python/projects/trading/serious_bot")
import pkg_resources
import subprocess
import sys
import datetime as dt
import time
import asyncio
import api

modules = ["telebot"]

for m in modules:
    try:
        pkg_resources.get_distribution(m)
    except pkg_resources.DistributionNotFound:
        subprocess.run([sys.executable, '-m', 'pip', 'install', m])

import telebot
from telebot import types



TOKEN = "8158212209:AAGYHNwv5wUOi5NmKmIDnyD1fnK_d3hJmMk"
MEAN_LENGTH = 15
LIMIT = 24

bot = telebot.TeleBot(TOKEN)
cl = api.API("demo_api")

stairs_steps = [2, 3, 4, 5, 6, 7, 8, 9, 10]
breakdown_percs = [5, 10, 20, 30, 40, 50]
volume_percs = [1000, 2000, 3000, 4000, 5000]
oi_percs = [5, 10, 20, 30, 40, 50]

bbs = cl.get_symbol_list()
try:
    f = open("D:/code/python/projects/trading/ginger_bot/last_symbols.txt","r")
except:
    f = open("C:/ginger_bot/last_symbols.txt","r")
last_symbols = [x for x in f.read().split(", ") if x in bbs]
f.close()

if last_symbols:
    def_symbols = last_symbols
else:
    def_symbols = ["BTCUSDT"]

def_intervals = {"5 минут" : 5,
                 "15 минут" : 15,
                 "1 час" : 60,
                 "2 часа" : 120,
                 "4 часа" : 240, 
                 "День" : "D"}

settings = {
    "menu_step" : "main_menu",

    "stairs" : True, 
    "stairs_steps" : 2,
    "stairs_perc" : 400,
    "stairs_vol_cut" : 10000000,

    "breakdown" : False,
    "breakdown_perc" : 10,

    "volume" : True, 
    "volume_perc" : 5000,
    "volume_vol_cut" :10000000,

    "oi" : False,
    "oi_perc" : 10,

    "symbols" : def_symbols,
    "temp_symbols" : def_symbols,
    "chosen_symbols" : [],

    # "intervals" : {k:v for k, v in def_intervals.items() if k in ["1 час", "День"]},
    # "temp_intervals" : {k:v for k, v in def_intervals.items() if k in ["1 час", "День"]},
    "chosen_intervals" :[],
    
}
try:
    f = open("D:/code/python/projects/trading/ginger_bot/last_intervals.txt","r")
except:
    f = open("C:/ginger_bot/last_intervals.txt","r")
last_intervals = [x for x in f.read().split(", ") if x in def_intervals.keys()]
f.close()
if last_intervals:
    settings["intervals"] = {k:v for k, v in def_intervals.items() if k in last_intervals}
    settings["temp_intervals"] = {k:v for k, v in def_intervals.items() if k in last_intervals}
else:
    settings["intervals"] = {k:v for k, v in def_intervals.items() if k in ["1 час", "День"]}
    settings["temp_intervals"] = {k:v for k, v in def_intervals.items() if k in ["1 час", "День"]}





# Главное Меню
settings_btn = types.KeyboardButton("Настройки")
start_signals = types.KeyboardButton("Погнали")
cur_settings = types.KeyboardButton("Посмотреть мои текущие настройки")
# Меню Настроек
signals = types.KeyboardButton("Сигналы")
coins = types.KeyboardButton("Монеты")
intervals = types.KeyboardButton("Интервалы")
# Меню Сигналов
stairs_sig = types.KeyboardButton("Лесенка")
vol_sig = types.KeyboardButton("Скачок объема")
# Меню Монет
keep_coins = types.KeyboardButton("Оставить")
del_coins = types.KeyboardButton("Удалить")
drop_selected = types.KeyboardButton("Отменить выбранное")
bb_coins = types.KeyboardButton("Список Bybit")
add_coins = types.KeyboardButton("Добавить")
all_of_symbs = types.KeyboardButton("ДОБАВИТЬ ВСЕ ДОСТУПНЫЕ")
next_sym = types.KeyboardButton("Следующие")
prev_sym = types.KeyboardButton("Предыдущие")
to_letters = types.KeyboardButton("Другая буква")
# Меню Лесенки
steps_num = types.KeyboardButton("Количество ступеней")
# trigger_vol = types.KeyboardButton("Объем первой свечи")
mean_vol_perc = types.KeyboardButton("Задать процент от среднего")
min_vol = types.KeyboardButton("Отсечь минимальный объем")
# Дополнительное Для Сигналов
off_signal = types.KeyboardButton("Отключить уведомления")
on_signal = types.KeyboardButton("Включить уведомления")
ok_btn = types.KeyboardButton("Ok")
# Назад
back = types.KeyboardButton("Назад")
to_mm = types.KeyboardButton("В главное меню")
# Включить Бота
start_bot = types.KeyboardButton("Включить бота")

main_menu = [settings_btn, cur_settings]
settings_menu = [signals, coins, intervals, back, to_mm]
signals_menu = [stairs_sig, vol_sig, back, to_mm]
coins_menu  = [keep_coins, del_coins, add_coins, drop_selected, bb_coins, all_of_symbs, back, to_mm]
stairs_menu = [steps_num, mean_vol_perc, min_vol]
volume_menu = [mean_vol_perc, min_vol]


@bot.message_handler(content_types=['text'])
def go_bot(message):

    if message.text in ["/start", "start", "Start", "START", "старт", "Старт", "СТАРТ"]:
        print("Нажал'Старт'")
        if not settings.get("bot_status"):
            settings["bot_status"] = "off"
            settings["owner"] = message.chat.id
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            markup.add(*main_menu, start_bot)
            bot.send_message(message.chat.id, text="Приветики!", reply_markup=markup)
        elif message.chat.id == settings.get("owner", ""):
            print("ломится владелец")
        else:
            print("ломятся")
            bot.send_message(message.chat.id, text="Бот занят другим пользователем")

    if settings.get("bot_status", False):

# Главное меню
        if settings["menu_step"] == "main_menu":

# Настройки  
            if message.text == "Настройки":
                print("нажал 'Настройки'")
                settings["menu_step"] = "settings"
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                markup.add(*settings_menu)
                bot.send_message(message.chat.id, text="Что настроим?", reply_markup=markup)

# Текущие настройки
            elif message.text == "Посмотреть мои текущие настройки":
                print("нажал 'Посмотреть мои текущие настройки'")
                vol_cuts = [str(k) + " : " + str((round(settings["volume_vol_cut"]/1440) * v)) + "$" if v !="D" else str(k) + " : " + str(settings["volume_vol_cut"]) + "$" for k,v in settings["temp_intervals"].items()]
                stairs_cuts = [str(k) + " : " + str((round(settings["stairs_vol_cut"]/1440) * v)) + "$" if v !="D" else str(k) + " : " + str(settings["stairs_vol_cut"]) + "$" for k,v in settings["temp_intervals"].items()]
                bot.send_message(message.chat.id, text=
                                 "ИНТТЕРВАЛЫ:\n\n" + "\n".join(settings["temp_intervals"].keys()) +
                                 "\n\nСИГНАЛЫ:" + 
                                 "\n\n"
                                 "### Скачок Объема ###\n Статус: " + 
                                 ("вкл" if settings["volume"] else "выкл") + 
                                 "\n\n Минимальный скачок: " + str(settings["volume_perc"]) + 
                                 "%\n Минимальный объем свечи,\n исходя из установленного дневного \n" + 
                                 str(settings["volume_vol_cut"]) +"$:\n\n" + "\n".join(vol_cuts)+
                                 "\n\n### Лесенка ###\n Статус: " +
                                 ("вкл" if settings["stairs"] else "выкл") + 
                                 "\n\n Кол-во ступеней: " + str(settings["stairs_steps"]) +
                                 "\n Минимальный скачок\n для первой ступени: " + str(settings["stairs_perc"]) + 
                                 "%\n Минимальный объем первой свечи,\n исходя из установленного дневного \n" + 
                                 str(settings["stairs_vol_cut"]) +"$:\n\n" + "\n".join(stairs_cuts))

                
# Меню Настроек
        elif settings["menu_step"] == "settings":

  # Сигналы
            if message.text == "Сигналы":
                print("нажал 'Сигналы'")
                settings["menu_step"] = "signals"
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                markup.add(*signals_menu)
                bot.send_message(message.chat.id, text="Выбирай", reply_markup=markup)

  # Монеты
            elif message.text == "Монеты":
                print("нажал 'Монеты'")
                settings["menu_step"] = "coins"
                settings["symbs_page"] = 0
                settings["bybit_symbols"] = cl.get_symbol_list()
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
                if len(settings["temp_symbols"]) <= 100:
                    symbols = [types.KeyboardButton(x) for x in settings["temp_symbols"]]
                    markup.add(*symbols, *coins_menu)
                    bot.send_message(message.chat.id, text="На клавишах ниже перечень монет, которые я мониторю для тебя сейчас." 
                                    "\nДля редактирования списка выбери монеты из текущего списка или полного перечня инструментов"
                                    "от Bybit, а затем нажми \"Удалить\"/\"Оставить\"/\"Добавить\"."
                                    "\nМожно очистить список выбранных монет, нажав соответствующую кнопку, или удалить выбранный элемент повторным нажатием."
                                    "\nтак же можно ввести символы вручную через запятую. Например \"blablausdt, trallallausdt\"", reply_markup=markup)
                else:
                    settings["symbs_page"] = 1
                    symbols = [types.KeyboardButton(x) for x in settings["temp_symbols"][:100]]
                    markup.add(next_sym, back, *symbols, next_sym, *coins_menu)
                    bot.send_message(message.chat.id, text="На клавишах ниже перечень монет, которые я мониторю для тебя сейчас." 
                                    "\nДля редактирования списка выбери монеты из текущего списка или полного перечня инструментов"
                                    "от Bybit, а затем нажми \"Удалить\"/\"Оставить\"/\"Добавить\"."
                                    "\nМожно очистить список выбранных монет, нажав соответствующую кнопку, или удалить выбранный элемент повторным нажатием."
                                    "\nтак же можно ввести символы вручную через запятую. Например \"blablausdt, trallallausdt\"", reply_markup=markup)
                    bot.send_message(message.chat.id, text="Список длинный. Это его часть. Есть кнопка, чтобы увидеть следующую часть")
                bot.send_message(message.chat.id, text="!!!ПОСЛЕ РЕДАКТИРОВАНИЯ СПИСКА ИНТЕРВАЛОВ ИЛИ МОНЕТ МОНИТОРИНГ ОСТАНОВИТСЯ. НЕ ЗАБУДЬ ЕГО СНОВА ВКЛЮЧИТЬ!!!")
                if settings["chosen_symbols"]:
                    bot.send_message(message.chat.id, text="Сейчас выбрано: " + ", ".join(settings["chosen_symbols"]))
                
  # Интервалы
            elif message.text == "Интервалы":
                print("нажал 'Интервалы'")
                settings["menu_step"] = "intervals"
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                inters = [types.KeyboardButton(x) for x in def_intervals.keys()]
                markup.add(*inters, ok_btn, back, to_mm)
                bot.send_message(message.chat.id, text="В данный момент мониторятся:\n" + ",\n".join(settings["temp_intervals"].keys()) + 
                                "\nЕсли некоторые из них не нужны, выбери интересующие и нажми \"Ok\"", reply_markup=markup)
                bot.send_message(message.chat.id, text="!!!ПОСЛЕ РЕДАКТИРОВАНИЯ СПИСКА ИНТЕРВАЛОВ ИЛИ МОНЕТ МОНИТОРИНГ ОСТАНОВИТСЯ. НЕ ЗАБУДЬ ЕГО СНОВА ВКЛЮЧИТЬ!!!")

# Меню сигналов
        elif settings["menu_step"] == "signals":

  # Лесенка
            if message.text == "Лесенка":
                print("нажал 'Лесенка'")
                settings["menu_step"] = "stairs_settings"
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                if settings["stairs"] == True:
                    markup.add(*stairs_menu, off_signal, back, to_mm)
                else:
                    markup.add(*stairs_menu, on_signal, back, to_mm)
                bot.send_message(message.chat.id, text="В данный момент установлено " + str(settings["stairs_steps"]) + " ступеней.", reply_markup=markup)

  # Скачок объема
            elif message.text == "Скачок объема":
                print("нажал 'Скачок объема'")
                settings["menu_step"] = "volume_settings"
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                if settings["volume"] == True:
                    markup.add(*volume_menu, off_signal, back, to_mm)
                else:
                    markup.add(*volume_menu, on_signal, back, to_mm)
                bot.send_message(message.chat.id, text=f"На сколько процентов должен вырасти объем текущей свечи относительно среднего,"
                                    "чтобы я тебе об этом сообщил? \nВыбери значение из тех, что на кнопочках или введи любое от 0.1 до разумных пределов)."
                                    "\nПо-умолчанию я запраграммирован на 1000%", reply_markup=markup)
    
# Настройки лесенки
        elif settings["menu_step"] == "stairs_settings" and message.text not in ["Назад", "В главное меню"]:
            
  # вкл/выкл  
            if message.text == "Отключить уведомления":
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                markup.add(*stairs_menu, on_signal, back, to_mm)
                settings["stairs"] = False
                bot.send_message(message.chat.id, text="Сигнал Лесенка отключен.", reply_markup=markup)
            elif message.text == "Включить уведомления":
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                markup.add(*stairs_menu, off_signal, back, to_mm)
                settings["stairs"] = True
                bot.send_message(message.chat.id, text="Сигнал Лесенка по среднему объему включен.", reply_markup=markup)

  # Ступени 
            elif message.text == "Количество ступеней":
                print("Нажал \"Количество ступеней\"")
                settings["menu_step"] = "stairs_steps"
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                btns = [types.KeyboardButton(x) for x in stairs_steps]
                markup.add(*btns, back)
                bot.send_message(message.chat.id, text="Выбери количество ступеней из значений на кнопочках ниже "
                                "или введи любое от 1 до разумных пределов)."
                                "\nВ данный момент установлено " + 
                                str(settings["stairs_steps"]) + ".", reply_markup=markup)
                
  # Процент превышения среднего объема
            elif message.text == "Задать процент от среднего":
                print("Нажал \"Задать процент от среднего\"")
                settings["menu_step"] = "stairs_perc_enter"
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                markup.add(back)
                bot.send_message(message.chat.id, 
                                text="Введи процент превышения среднего объема, после которого я буду начинать мониторить лестницы", 
                                reply_markup=markup)
  # Фиксированный объем
            elif message.text == "Отсечь минимальный объем":
                print("Нажал \"Отсечь минимальный объем\"")
                settings["menu_step"] = "stairs_vol_cut_enter"
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                markup.add(back)
                bot.send_message(message.chat.id, 
                                text="Введи объем торгов за день, выше которого я буду начинать мониторить лестницы. Для остальных таймфреймов он будет расчитан автоматически", 
                                reply_markup=markup)
                
# Настройка количества ступеней
        elif settings["menu_step"] == "stairs_steps":
            if message.text not in ["Назад", "В главное меню"]:
                try:
                    if 2 <= int(message.text) <=10:
                            settings["stairs_steps"] = int(message.text)
                            bot.send_message(message.chat.id, text=f"Целевое значение кол-ва ступеней для Лесенки с фиксированным объемом изменено на {message.text}.")
                            if not settings["stairs"]:
                                bot.send_message(message.chat.id, text="Однако на данный момент сигнал отключен, если хочешь, получать уведомления, включи их в настройках")
                    else:
                        bot.send_message(message.chat.id, text="Я мониторю от 2-х до 10-ти ступеней, но это ограничение можно снять. Ты знаешь, кого об этом спросить")
                except:
                    bot.send_message(message.chat.id, text="Это некорректное значение. Настройки не изменились")

# Настройка процента превышения среднего
        elif settings["menu_step"] == "stairs_perc_enter":
            if message.text not in ["Назад", "В главное меню"]:
                try:
                    settings["stairs_perc"] = float(message.text)
                    bot.send_message(message.chat.id, text=f"Целевое значение процента превышения среднего объема для первой свечи Лесенки изменено на {message.text}.")
                    if not settings["stairs"]:
                        bot.send_message(message.chat.id, text="Однако на данный момент сигнал отключен, если хочешь, получать уведомления, включи их в настройках")
                except:
                    bot.send_message(message.chat.id, text="Это некорректное значение. Настройки не изменились")   

# Настройка фиксированного объема
        elif settings["menu_step"] == "stairs_vol_cut_enter":
            if message.text not in ["Назад", "В главное меню"]:
                try:
                    settings["stairs_vol_cut"] = float(message.text.replace(",", "."))
                    bot.send_message(message.chat.id, text=f"Отсекли лесенки первая ступень которых не превышает {message.text}.")
                    if not settings["stairs"]:
                        bot.send_message(message.chat.id, text="Однако на данный момент сигнал отключен, если хочешь, получать уведомления, включи их в настройках")
                except:
                    bot.send_message(message.chat.id, text="Это некорректное значение. Настройки не изменились")            


# Настройки скачка объема
        elif settings["menu_step"] == "volume_settings" and message.text not in ["Назад", "В главное меню"]:

            if message.text == "Отключить уведомления":
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                markup.add(*volume_menu, on_signal, back, to_mm)
                settings["volume"] = False
                bot.send_message(message.chat.id, text="Сигнал Скачок Объема отключен.", reply_markup=markup)
            elif message.text == "Включить уведомления":
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                markup.add(*volume_menu, off_signal, back, to_mm)
                settings["volume"] = True
                bot.send_message(message.chat.id, text="Сигнал Скачок Объема включен.", reply_markup=markup)
            
  # Процент превышения среднего объема
            elif message.text == "Задать процент от среднего":
                print("Нажал \"Задать процент от среднего\"")
                settings["menu_step"] = "volume_perc_enter"
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                markup.add(back)
                bot.send_message(message.chat.id, 
                                text="Введи процент превышения среднего объема, после которого я буду ", 
                                reply_markup=markup)
  # Фиксированный объем
            elif message.text == "Отсечь минимальный объем":
                print("Нажал \"Отсечь минимальный объем\"")
                settings["menu_step"] = "volume_vol_cut_enter"
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                markup.add(back)
                bot.send_message(message.chat.id, 
                                text="Введи объем торгов за день, выше которого я буду начинать мониторить объм. Для остальных таймфреймов он будет расчитан автоматически", 
                                reply_markup=markup)
                
# Настройка процента превышения среднего
        elif settings["menu_step"] == "volume_perc_enter":
            if message.text not in ["Назад", "В главное меню"]:
                try:
                    settings["volume_perc"] = float(message.text)
                    bot.send_message(message.chat.id, text=f"Целевое значение процента превышения среднего для Скачка объема {message.text}.")
                    if not settings["volume"]:
                        bot.send_message(message.chat.id, text="Однако на данный момент сигнал отключен, если хочешь, получать уведомления, включи их в настройках")
                except:
                    bot.send_message(message.chat.id, text="Это некорректное значение. Настройки не изменились")   

# Настройка фиксированного объема
        elif settings["menu_step"] == "volume_vol_cut_enter":
            if message.text not in ["Назад", "В главное меню"]:
                try:
                    settings["volume_vol_cut"] = float(message.text.replace(",", "."))
                    bot.send_message(message.chat.id, text=f"Отсекли лесенки первая ступень которых не превышает {message.text}.")
                    if not settings["volume"]:
                        bot.send_message(message.chat.id, text="Однако на данный момент сигнал отключен, если хочешь, получать уведомления, включи их в настройках")
                except:
                    bot.send_message(message.chat.id, text="Это некорректное значение. Настройки не изменились")     

# Настройки роста открытого интереса

# Меню монет
        elif settings["menu_step"] in ["coins", "letters"]:

  # выбор монет
            if message.text.upper() in settings["bybit_symbols"]:        

  # выбрали
                if message.text.upper() not in settings["chosen_symbols"]:
                    settings["chosen_symbols"].append(message.text.upper())
                    settings["chosen_symbols"] = sorted(settings["chosen_symbols"])
                    try:
                        bot.send_message(message.chat.id, text="Выбрано: " + ", ".join(settings["chosen_symbols"]).upper())
                    except:
                        bot.send_message(message.chat.id, text="Ты выбрал слишком много. Сделай с выбранными то, что намеревался, а затем можешь продолжить выбирать")
  # убрали из выбранного
                else: 
                    settings["chosen_symbols"].remove(message.text)
                    settings["chosen_symbols"] = sorted(settings["chosen_symbols"])
                    if settings["chosen_symbols"]:
                        bot.send_message(message.chat.id, text="Выбрано: " + ", ".join(settings["chosen_symbols"]).upper())
                    else:
                        bot.send_message(message.chat.id, text="Выбирай уже чего-нибудь, или иди к какой-то матери")
            
  # удалить
            elif message.text == "Удалить":
                settings["menu_step"] = "coins"
                if settings["chosen_symbols"]:
                    deleted = [x for x in settings["temp_symbols"] if x in settings["chosen_symbols"]]
                    if deleted:
                        settings["temp_symbols"] = [x for x in settings["temp_symbols"] if x not in settings["chosen_symbols"]]
                        try:
                            f = open("D:/code/python/projects/trading/ginger_bot/last_symbols.txt","w")
                        except:
                            f = open("C:/ginger_bot/last_symbols.txt","w")
                        f.write(", ".join(settings["temp_symbols"]))
                        f.close()
                        settings["chosen_symbols"] = []
                        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
                        symbols = [types.KeyboardButton(x) for x in settings["temp_symbols"][:100]]
                        if len(settings["temp_symbols"]) > 100:
                            settings["symbs_page"] = 1
                            markup.add(next_sym, back, *symbols, next_sym, *coins_menu) 
                        else:
                            markup.add(*symbols, *coins_menu)   
                    
                        bot.send_message(message.chat.id, text="Готово")
                        bot.send_message(message.chat.id, text="Удалил: " + str(deleted).\
                                        replace("[", "").replace("]", "").replace("'", ""), reply_markup=markup)
                        if settings["bot_status"] in ["on", "wait"]:
                            bot.send_message(message.chat.id, text="Настройки вступят в силу, когда бот закончит текущий цикл запросов к Bybit")
                            settings["bot_status"] = "wait"
                    else:
                        bot.send_message(message.chat.id, text="Ты ничего не поменял")            

  # оставить   
            elif message.text == "Оставить":
                settings["menu_step"] = "coins"
                if  settings["chosen_symbols"]:
                    if settings["chosen_symbols"]!= settings["temp_symbols"]:
                        settings["temp_symbols"] = settings["chosen_symbols"]
                        try:
                            f = open("D:/code/python/projects/trading/ginger_bot/last_symbols.txt","w")
                        except:
                            f = open("C:/ginger_bot/last_symbols.txt","w")
                        f.write(", ".join(settings["temp_symbols"]))
                        f.close()
                        settings["chosen_symbols"] = []
                        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
                        symbols = [types.KeyboardButton(x) for x in settings["temp_symbols"][:100]]
                        if len(settings["temp_symbols"]) > 100:
                            settings["symbs_page"] = 1
                            markup.add(next_sym, back, *symbols, next_sym, *coins_menu) 
                        else:
                            markup.add(*symbols, *coins_menu)   
                        bot.send_message(message.chat.id, text="Готово", reply_markup=markup)
                        if settings["bot_status"] in ["on", "wait"]:
                            bot.send_message(message.chat.id, text="Настройки вступят в силу, когда бот закончит текущий цикл запросов к Bybit")
                            settings["bot_status"] = "wait"
                    else:
                        bot.send_message(message.chat.id, text="Ты ничего не поменял")

  # добавить
            elif message.text == "Добавить":
                settings["menu_step"] = "coins"
                if settings["chosen_symbols"]:
                    settings["temp_symbols"] = sorted(list(set(settings["temp_symbols"] + settings["chosen_symbols"])))
                    if settings["temp_symbols"]!= settings["symbols"]:
                        try:
                            f = open("D:/code/python/projects/trading/ginger_bot/last_symbols.txt","w")
                        except:
                            f = open("C:/ginger_bot/last_symbols.txt","w")
                        f.write(", ".join(settings["temp_symbols"]))
                        f.close()
                        settings["chosen_symbols"] = []
                        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
                        symbols = [types.KeyboardButton(x) for x in settings["temp_symbols"][:100]]
                        if len(settings["temp_symbols"]) > 100:
                            settings["symbs_page"] = 1
                            markup.add(next_sym, back, *symbols, next_sym, *coins_menu)
                        else:
                            markup.add(*symbols, *coins_menu)   
                        bot.send_message(message.chat.id, text="Готово", reply_markup=markup)
                        if settings["bot_status"] in ["on", "wait"]:
                            bot.send_message(message.chat.id, text="Настройки вступят в силу, когда бот закончит текущий цикл запросов к Bybit")
                            settings["bot_status"] = "wait"
                    else:
                        bot.send_message(message.chat.id, text="Ты ничего не поменял")

  # отменить выбранное
            elif message.text == "Отменить выбранное":
                if settings["chosen_symbols"]:
                    settings["chosen_symbols"] = []
                    bot.send_message(message.chat.id, text="Миша, давай по новой!")

  # Добавить все
            elif message.text == "ДОБАВИТЬ ВСЕ ДОСТУПНЫЕ":
                settings["menu_step"] = "settings"
                settings["temp_symbols"] = settings["bybit_symbols"]
                try:
                    f = open("D:/code/python/projects/trading/ginger_bot/last_symbols.txt","w")
                except:
                    f = open("C:/ginger_bot/last_symbols.txt","w")
                f.write(", ".join(settings["temp_symbols"]))
                f.close()
                settings["chosen_symbols"] = []
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                markup.add(*settings_menu)
                bot.send_message(message.chat.id, text="Добавил все, что есть на байбит. Когда я буду тупить, знай, это не я туплю, это ты тупишь))) ", reply_markup=markup)
                if settings["bot_status"] in ["on", "wait"]:
                    bot.send_message(message.chat.id, text="Настройки вступят в силу, когда бот закончит текущий цикл запросов к Bybit")
                    settings["bot_status"] = "wait"

  # Список bybit
            elif message.text == "Список Bybit" or message.text == "Другая буква":
                print("Нажал 'Список Bybit'")
                
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
                first_letters = sorted(set([x[0] for x in settings["bybit_symbols"]]))
                btns = [types.KeyboardButton(x) for x in settings["bybit_symbols"] if x[0] == message]
                markup.add(*first_letters, back)
                bot.send_message(message.chat.id, text="Выбери буковку", reply_markup=markup)
                settings["menu_step"] = "letters"

# разбор набранного с клавиатуры на символы
            elif settings["menu_step"] == "coins" and message.text not in ["Назад", "В главное меню"]:
                symbs = [x.strip(" ,") for x in message.text.upper().split(",") if x not in ["" , " "]]
                for symb in symbs:
                    if symb in settings["bybit_symbols"]:
# добавили в выбранное
                        if symb not in settings["chosen_symbols"]:
                            settings["chosen_symbols"].append(symb)
                            bot.send_message(message.chat.id, text="Выбрано: " + ", ".join(settings["chosen_symbols"]).upper())
# убрали из выбранного
                        else: 
                            settings["chosen_symbols"].remove(message.text)
                            if settings["chosen_symbols"]:
                                bot.send_message(message.chat.id, text="Выбрано: " + ", ".join(settings["chosen_symbols"]).upper())
                            else:
                                bot.send_message(message.chat.id, text="Выбирай уже чего-нибудь, или иди к какой-то матери")
                    else:
                        bot.send_message(message.chat.id, text=f"{symb} не выбирается. Такого нет на Bybit")

            elif settings["menu_step"] == "letters":
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
                b = [types.KeyboardButton(x) for x in settings["bybit_symbols"] if x[0] == message.text]
                markup.add(to_letters, *b, *coins_menu)
                bot.send_message(message.chat.id, text="Выбирай", reply_markup=markup)
                # settings["menu_step"] = "coins"
            
  # Следующая/предыдущая страница
            elif settings["symbs_page"]:
                if message.text in ["Следующие", "Предыдущие"]:
                    if message.text == "Следующие":
                        settings["symbs_page"] +=1
                    if message.text == "Предыдущие":
                        settings["symbs_page"] -=1
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
                    page = settings["symbs_page"]
                    symbols = [types.KeyboardButton(x) for x in settings["temp_symbols"][(page-1)*100:page*100]]
                    if page > 1:
                        if page * 100 < len(settings["temp_symbols"]):
                            markup.add(next_sym, prev_sym, back, *symbols, next_sym, prev_sym, *coins_menu)
                        else:
                            markup.add(prev_sym, back, *symbols, prev_sym, *coins_menu)
                    else:
                        markup.add(next_sym, back, *symbols, next_sym, *coins_menu)
                    bot.send_message(message.chat.id, text="Список длинный. Это его часть. Есть кнопка, чтобы увидеть следующую/предыдущую часть", reply_markup=markup)
                    bot.send_message(message.chat.id, text="!!!ПОСЛЕ РЕДАКТИРОВАНИЯ СПИСКА ИНТЕРВАЛОВ ИЛИ МОНЕТ БОТА НЕОБХОДИМА ПЕРЕЗАПУСКАТЬ!!!")
                    if settings["chosen_symbols"]:
                        bot.send_message(message.chat.id, text="Сейчас выбрано: " + ", ".join(settings["chosen_symbols"]))

# Меню интервалов
        elif settings["menu_step"] == "intervals":
  # выбор интервалов
            if message.text in def_intervals.keys():
  # добавили
                if message.text not in settings["chosen_intervals"]:
                    settings["chosen_intervals"].append(message.text)
                    bot.send_message(message.chat.id, text="Выбрано: " + ", ".join(settings["chosen_intervals"]))
  # убрали
                else: 
                    settings["chosen_intervals"].remove(message.text)
                    if settings["chosen_intervals"]:
                        bot.send_message(message.chat.id, text="Выбрано: " + ", ".join(settings["chosen_intervals"]))
                    else:
                        bot.send_message(message.chat.id, text="Выбирай уже чего-нибудь, или иди к какой-то матери")
  # Зафиксировали изменения 
            elif message.text == "Ok":
                if settings["chosen_intervals"]:
                    settings["temp_intervals"] = {k:v for k,v in def_intervals.items() if k in settings["chosen_intervals"]}
                    try:
                        f = open("D:/code/python/projects/trading/serious_bot/telegram/last_intervals.txt","w")
                    except:
                            f = open("C:/ginger_bot/last_intervals.txt","w")
                    f.write(", ".join(settings["temp_intervals"].keys()))
                    f.close()
                    settings["chosen_intervals"] = []
                    if len(settings["temp_intervals"]) == 6:
                        bot.send_message(message.chat.id, text="Будем мониторить всё")
                    else:
                        bot.send_message(message.chat.id, text="Будем мониторить только " + ", ".join(settings["temp_intervals"].keys()))
                    if settings["bot_status"] in ["on", "wait"]:
                        bot.send_message(message.chat.id, text="Настройки вступят в силу, когда бот закончит текущий цикл запросов к Bybit")
                        settings["bot_status"] = "wait"

# Назад
        if message.text == "Назад":
            print("Нажал 'назад'")
            if settings["menu_step"] == "settings":
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                if settings["bot_status"] == "off":
                    markup.add(*main_menu, start_bot)
                else:
                    markup.add(*main_menu)
                bot.send_message(message.chat.id, text="Вернулись в главное меню", reply_markup=markup)
                settings["menu_step"] = "main_menu"
                
            elif settings["menu_step"] in ["signals", "coins", "intervals"]:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                markup.add(*settings_menu)
                bot.send_message(message.chat.id, text="Вернулись в настройки", reply_markup=markup)
                settings["menu_step"] = "settings"
                
            elif settings["menu_step"] == "letters":
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
                symbols = [types.KeyboardButton(x) for x in settings["temp_symbols"][:100]]
                if len(settings["temp_symbols"]) > 100:
                    settings["symbs_page"] = 1
                    markup.add(next_sym, back, *symbols, next_sym, *coins_menu) 
                else:
                    markup.add(*symbols, *coins_menu)   
                bot.send_message(message.chat.id, text="Вернулись в твои монеты.", reply_markup=markup)
                settings["menu_step"] = "coins"

            elif settings["menu_step"] in ["stairs_settings", "breakdown_settings", "volume_settings", "oi_settings"]:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                markup.add(*signals_menu)
                bot.send_message(message.chat.id, text="Вернулись к выбору сигналов", reply_markup=markup)
                settings["menu_step"] = "signals"

            elif settings["menu_step"] in ["stairs_steps", "stairs_vol_cut_enter", "stairs_perc_enter" ]:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                if settings["stairs"] == True:
                    markup.add(*stairs_menu, off_signal, back, to_mm)
                else:
                    markup.add(*stairs_menu, on_signal, back, to_mm)
                bot.send_message(message.chat.id, text="Вернулись в настройки Лесенки", reply_markup=markup)
                settings["menu_step"] = "stairs_settings"

            elif settings["menu_step"] in ["volume_vol_cut_enter", "volume_perc_enter" ]:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                if settings["volume"] == True:
                    markup.add(*volume_menu, off_signal, back, to_mm)
                else:
                    markup.add(*volume_menu, on_signal, back, to_mm)
                bot.send_message(message.chat.id, text="Вернулись в настройки Скачка Объема", reply_markup=markup)
                settings["menu_step"] = "stairs_settings"

# В главное меню
        if message.text == "В главное меню":
            print("нажал 'В главное меню'")
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            if settings["bot_status"] == "off":
                markup.add(*main_menu, start_bot)
            else:
                markup.add(*main_menu)
            bot.send_message(message.chat.id, text="Вернулись в главное меню", reply_markup=markup)
            settings["menu_step"] = "main_menu"

# Запуск бота
        if message.text == "Включить бота":
            settings["bot_status"] = "on"
            print("On")
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            markup.add(*main_menu)
            bot.send_message(message.chat.id, text="Окей! Поработаем!", reply_markup=markup)
            settings["menu_step"] = "main_menu"
            settings["symbols"] = settings["temp_symbols"]
            settings["intervals"] = settings["temp_intervals"]
                
            
            # cl.get_data(settings["symbols"], list(settings["intervals"].values()), limit=LIMIT, volume=True, last_closed=False)
            asyncio.run(cl.a_get_data(settings["symbols"], list(settings["intervals"].values()), limit=LIMIT, volume=True, last_closed=False))
            while True:
                message_list = []
                # cl.update_data()
                print("ok")
                for symb, inter in cl.data.items():
                    for i, data in inter.items():
                        volumes = list(data["data"]["volume"])
                        if len(volumes) == 24:
                            if settings["volume"]:
                                last_vol = volumes[0]
                                pre_last_vol = volumes[1]
                                previous_mean = data["data"][1:16]["volume"].median()
                                try:
                                    fix_vol = round(settings["volume_vol_cut"]/1440) * int(i)
                                except:
                                    fix_vol = settings["volume_vol_cut"]
                                if last_vol >= fix_vol:
                                    if int(previous_mean):
                                        diff = round(last_vol/previous_mean*100) - 100
                                        if diff > settings["volume_perc"] and last_vol > pre_last_vol:
                                            date = data["data"].index[0]
                                            if data.get("vol_last_mess", 0) != date:
                                                mess = f"{symb}\n{date}\nINTERVAL : {i}\nОбъём последнего закрытого торгового периода вырос на:\n{diff}% относительно среднего за предыдущие {MEAN_LENGTH}"
                                                # print(mess)
                                                message_list.append(mess)
                                                data["vol_last_mess"] = date
                            if settings["stairs"]:
                                last_steps = volumes[:settings["stairs_steps"]+1]
                                first_step = last_steps[-1]
                                previous_mean = data["data"][settings["stairs_steps"]+1:settings["stairs_steps"]+15]["volume"].median()
                                try:
                                    fix_vol = round(settings["stairs_vol_cut"]/1440) * int(i)
                                except:
                                    fix_vol = settings["stairs_vol_cut"]                            
                                if (first_step >= fix_vol):
                                    if int(previous_mean):
                                        diff = round(first_step/previous_mean*100) - 100
                                        if (diff > settings["stairs_perc"]) and (sorted(last_steps, reverse=True) == last_steps) and (len(last_steps) == len(set(last_steps))):
                                            date = data["data"].index[0]
                                            if data.get("stairs_last_mess", 0) != date:
                                                mess = f"{symb}\n{date}\nINTERVAL : {i}\nРост объема в течение " + str(settings["stairs_steps"]) + " свечей"
                                                print(mess)
                                                bot.send_message(message.chat.id, text=mess)
                                                data["stairs_last_mess"] = date

                mess_num = 0
                for mess in message_list:
                    mess_num +=1
                    if mess_num <= 20:
                        bot.send_message(message.chat.id, text=mess)
                        time.sleep(0.2)
                        
                    else:
                        time.sleep(56)
                        mess_num = 1
                        bot.send_message(message.chat.id, text=mess)

                if settings["bot_status"] == "wait":
                    bot.send_message(message.chat.id, text="Настройки изменены")
                    
                    if settings["menu_step"] == "main_menu":
                        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                        markup.add(*main_menu, start_bot)
                        bot.send_message(message.chat.id, text="БОТ ВЫКЛЮЧЕН! НЕ ЗАБУДЬ ЕГО ВКЛЮЧИТЬ!", reply_markup=markup)
                    else:
                        bot.send_message(message.chat.id, text="БОТ ВЫКЛЮЧЕН! НЕ ЗАБУДЬ ЕГО ВКЛЮЧИТЬ!")
                    settings["bot_status"] = "off"
                    print("off")
                    break

                time.sleep(5)

# bot.polling(none_stop=True)
bot.infinity_polling()