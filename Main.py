import telebot
from telebot import types
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import schedule
import threading
import time
import sys
import traceback
import logging

BOT_TOKEN = "5455058686:AAERZFY3MTaFocCaWaz-8gqEYXPr3gvk-sU"

bot = telebot.TeleBot(BOT_TOKEN)

# Завантаження файлу з ключем доступу до Гугл таблиці (credentials.json)
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(credentials)
# Відкриття Гугл таблиці за допомогою ідентифікатора
sheet = client.open_by_key('1LWJJDsalSaKXUcJnRjxzozbD7QGdxeTt_l1nlvXYlMM').sheet1
# Отримання аркуша Sheet2 за індексом
sheet2 = client.open_by_key('1LWJJDsalSaKXUcJnRjxzozbD7QGdxeTt_l1nlvXYlMM').get_worksheet(1)
sheet3 = client.open_by_key('1LWJJDsalSaKXUcJnRjxzozbD7QGdxeTt_l1nlvXYlMM').get_worksheet(2)

# Обробник натискання кнопок в меню з перевіркою наявності користувача в таблиці
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    # Перевірка, чи є користувач в таблиці
    user_id = str(message.from_user.id)
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    username = message.from_user.username

    user_found = False
    rows = sheet.get_all_values()
    for row in rows:
        if row[0] == user_id or (row[1] == f"{first_name} {last_name}") or row[2] == username:
            user_found = True
            if not row[0]:
                sheet.update_cell(rows.index(row) + 1, 1, user_id)
            if not row[1]:
                if last_name:
                    sheet.update_cell(rows.index(row) + 1, 2, f"{first_name} {last_name}")
                else:
                    sheet.update_cell(rows.index(row) + 1, 2, first_name)
            if not row[2]:
                sheet.update_cell(rows.index(row) + 1, 3, username)
            break

    if user_found:
        # Користувач присутній в таблиці
        if message.text == "Покращити роботу":
            markup = create_improve_menu_markup()
            bot.send_message(message.chat.id, "Тут ти можеш запропонувати додати сервіс або скрипт, обери що саме тебе цікавить:", reply_markup=markup)
        elif message.text == "Організація роботи":
            markup = create_work_organization_menu_markup()
            bot.send_message(message.chat.id, "Обери пункт меню:", reply_markup=markup)
        elif message.text == "Відділ комунікації":
            markup = create_main_communication_issue()
            bot.send_message(message.chat.id, "Обери пункт меню:", reply_markup=markup)
        elif message.text == "Адміністративна панель":
            markup = create_main_admin_issue()
            bot.send_message(message.chat.id, "Обери пункт меню:", reply_markup=markup)
        elif message.text == "Відправити всім користувачам":
            handle_menu_callback(callback_query)
        elif message.text == "Поділитись випадком":
            markup = create_input_message_markup()
            bot.send_message(message.chat.id, "Поділись своїм крутим або складним випадком, щоб команда комунікації могла оцінити його в 1 повідомленні:", reply_markup=markup)
            bot.register_next_step_handler(message, handle_input_message4)
        elif message.text == "Поставити питання":
            markup = create_input_message_markup()
            bot.send_message(message.chat.id, "Напиши своє питання команді комунікації в 1 повідомленні і команда надасть тобі розгорнуту відповідь:", reply_markup=markup)
            bot.register_next_step_handler(message, handle_input_message5)
        elif message.text == "Анонімно поскаржитись":
            markup = create_input_message_markup()
            bot.send_message(message.chat.id, "Поділись в 1 повідомленні, що саме тебе образило або що ти хочеш змінити", reply_markup=markup)
            bot.register_next_step_handler(message, handle_input_message3)
        elif message.text == "Графік відпусток":
            handle_vacation_schedule_button(message)
        elif message.text == "Робочі дні":
            handle_working_days(message)
        elif message.text == "Питання оплати":
            markup = create_main_payment_issue()
            bot.send_message(message.chat.id, "Обери, розрахунок чого тебе цікавить:", reply_markup=markup)
        elif message.text == "Зразки заяв":
            markup = create_application_samples_menu_markup()
            bot.send_message(message.chat.id, "Обери зразок заяви:", reply_markup=markup)
        elif message.text == "Відпустка 14 днів":
            with open('one.png', 'rb') as file:
                bot.send_photo(message.chat.id, file)
        elif message.text == "Відпустка 10 днів":
            with open('two.png', 'rb') as file:
                bot.send_photo(message.chat.id, file)
        elif message.text == "Відпустка 10 днів на 2 дати":
            with open('three.png', 'rb') as file:
                bot.send_photo(message.chat.id, file)
        elif message.text == "Відпустка в честь ДР":
            with open('four.png', 'rb') as file:
                bot.send_photo(message.chat.id, file)
        elif message.text == "За власний рахунок":
            with open('five.png', 'rb') as file:
                bot.send_photo(message.chat.id, file)
        elif message.text == "Зміна реквізитів":
            with open('six.png', 'rb') as file:
                bot.send_photo(message.chat.id, file)
        elif message.text == "Заробітна плата":
            salary_data = sheet3.cell(1, 1).value
            bot.send_message(message.chat.id, f"{salary_data}", parse_mode="HTML")
        elif message.text == "Лікарняні":
            salary_data = sheet3.cell(2, 1).value
            bot.send_message(message.chat.id, f"{salary_data}", parse_mode="HTML")
        elif message.text == "Відпустки":
            salary_data = sheet3.cell(3, 1).value
            bot.send_message(message.chat.id, f"{salary_data}", parse_mode="HTML")
        elif message.text == "Запропонувати скрипт":
            markup = create_input_message_markup()
            bot.send_message(message.chat.id, "Напиши свою пропозицію в 1 повідомленні:", reply_markup=markup)
            bot.register_next_step_handler(message, handle_input_message1)
        elif message.text == "Запропонувати сервіс":
            markup = create_input_message_markup()
            bot.send_message(message.chat.id, "Напиши свою пропозицію в 1 повідомленні:", reply_markup=markup)
            bot.register_next_step_handler(message, handle_input_message2)
        elif message.text == "Анонімно поскаржитись":
            markup = create_input_message_markup()
            bot.send_message(message.chat.id, "Поділись в 1 повідомленні, що саме тебе образило або що ти хочеш змінити", reply_markup=markup)
            bot.register_next_step_handler(message, handle_input_message3)
        elif message.text == "Відправити пост":
            markup = create_input_message_markup()
            bot.send_message(message.chat.id, "Напишипост в 1 повідомленні, та я відправлю його всім менеджерам", reply_markup=markup)
            bot.register_next_step_handler(message, handle_input_message6)
        else:
            markup = create_main_menu_markup(user_id)
            bot.send_message(message.chat.id, 'Обери категорію, і я допоможу тобі.', reply_markup=markup)
    else:
        # Користувач відсутній в таблиці
        bot.send_message(message.chat.id, 'Дякую, що цікавитесь. Якщо бажаєте приєднатись до команди, переходьте на портал вакансій – https://company.diia.gov.ua/vacancies')

user_state = {}
user_prev_message = {}
#Обробник відповіді адміністратором
@bot.callback_query_handler(func=lambda call: call.data.startswith("reply_"))
def handle_reply_button(call):
    user_id = call.data.split("_")[1]
    admin_chat_id = call.from_user.id
    markup = create_output_message_markup()
    bot.send_message(admin_chat_id, "Введіть повідомлення:", reply_markup=markup)
    bot.register_next_step_handler(call.message, lambda message: handle_admin_reply(message, user_id, admin_chat_id))

def handle_admin_reply(message, user_id, admin_chat_id):
    if message.text == "Скасувати":
        bot.send_message(message.chat.id, "Процес скасовано.")
        bot.clear_step_handler_by_chat_id(message.chat.id)
        markup = create_main_menu_markup(user_id)
        bot.send_message(message.chat.id, "Обери пункт меню:", reply_markup=markup)
    else:
        bot.send_message(int(user_id), f"<b>Адміністратор вам відповів:</b>\n\n{message.text}", parse_mode="HTML")
        bot.send_message(message.chat.id, "Повідомлення надіслано користувачу.")
        admin_message_id = None
        if message.reply_to_message:
            admin_message_id = message.reply_to_message.message_id
            try:
                bot.get_chat_member(admin_chat_id, admin_message_id)
                bot.edit_message_reply_markup(admin_chat_id, admin_message_id, reply_markup=None)
            except telebot.apihelper.ApiTelegramException:
                pass
        markup = create_main_menu_markup(user_id)
        bot.send_message(message.chat.id, "Обери пункт меню:", reply_markup=markup)

#Обробник відправки пропозиції скрипта
@bot.message_handler(content_types=['text', 'photo', 'video'])
def handle_input_message1(message):
    user_id = str(message.from_user.id)
    user_message = message.text if message.text else ''

    # Перевірка, чи є користувач в таблиці
    user_found = False
    rows = sheet.get_all_values()
    user_row = None
    for row in rows:
        if row[0] == user_id:
            user_found = True
            user_row = row
            break

    if message.text == "Назад":
        markup = create_improve_menu_markup()
        bot.send_message(message.chat.id, "Обери пункт меню:", reply_markup=markup)
    elif user_found:
        admin_chat_id = user_row[4]  # Значення п'ятого стовпця рядка - ADMIN_CHAT_ID
        admin_markup = types.InlineKeyboardMarkup()
        reply_button = types.InlineKeyboardButton(text="Відповісти", callback_data=f"reply_{user_id}")
        admin_markup.add(reply_button)

        if message.photo:
            photo_id = message.photo[-1].file_id
            photo_caption = f"<b>Користувач {user_row[3]} пропонує скрипт та надсилає фото з описом:</b>"
            if message.caption:
                photo_caption += f"\n\n{message.caption}"
            bot.send_photo(admin_chat_id, photo_id, caption=photo_caption, reply_markup=admin_markup, parse_mode="HTML")
        elif message.video:
            video_id = message.video.file_id
            video_caption = f"<b>Користувач {user_row[3]} пропонує скрипт та надсилає відео з описом:</b>"
            if message.caption:
                video_caption += f"\n\n{message.caption}"
            bot.send_video(admin_chat_id, video_id, caption=video_caption, reply_markup=admin_markup, parse_mode="HTML")
        else:
            admin_message = f"<b>Користувач {user_row[3]} надіслав пропозицію додати скрипт:</b>\n\n{user_message}"
            bot.send_message(admin_chat_id, admin_message, reply_markup=admin_markup, parse_mode="HTML")

        bot.send_message(message.chat.id, "Дякую за ваше повідомлення. Адміністратор отримав повідомлення і відповість найближчим часом.")
        markup = create_main_menu_markup(user_id)
        bot.send_message(message.chat.id, "Обери пункт меню:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Дякую, що цікавитесь. Якщо бажаєте приєднатись до команди, переходьте на портал вакансій – https://company.diia.gov.ua/vacancies')

#Обробник відправки пропозиції сервіса
@bot.message_handler(content_types=['text', 'photo', 'video'])
def handle_input_message2(message):
    user_id = str(message.from_user.id)
    user_message = message.text if message.text else ''

    # Перевірка, чи є користувач в таблиці
    user_found = False
    rows = sheet.get_all_values()
    user_row = None
    for row in rows:
        if row[0] == user_id:
            user_found = True
            user_row = row
            break

    if message.text == "Назад":
        markup = create_improve_menu_markup()
        bot.send_message(message.chat.id, "Обери пункт меню:", reply_markup=markup)
    elif user_found:
        admin_chat_id = user_row[4]  # Значення п'ятого стовпця рядка - ADMIN_CHAT_ID
        admin_markup = types.InlineKeyboardMarkup()
        reply_button = types.InlineKeyboardButton(text="Відповісти", callback_data=f"reply_{user_id}")
        admin_markup.add(reply_button)

        if message.photo:
            photo_id = message.photo[-1].file_id
            photo_caption = f"<b>Користувач {user_row[3]} пропонує сервіс та надсилає фото з описом:</b>"
            if message.caption:
                photo_caption += f"\n\n{message.caption}"
            bot.send_photo(admin_chat_id, photo_id, caption=photo_caption, reply_markup=admin_markup, parse_mode="HTML")
        elif message.video:
            video_id = message.video.file_id
            video_caption = f"<b>Користувач {user_row[3]} пропонує сервіс та надсилає з описом:</b>"
            if message.caption:
                video_caption += f"\n\n{message.caption}"
            bot.send_video(admin_chat_id, video_id, caption=video_caption, reply_markup=admin_markup, parse_mode="HTML")
        else:
            admin_message = f"<b>Користувач {user_row[3]} надіслав пропозицію додати сервіс:</b>\n\n{user_message}"
            bot.send_message(admin_chat_id, admin_message, reply_markup=admin_markup, parse_mode="HTML")

        bot.send_message(message.chat.id, "Дякую за ваше повідомлення. Адміністратор отримав повідомлення і відповість найближчим часом.")
        markup = create_main_menu_markup(user_id)
        bot.send_message(message.chat.id, "Обери пункт меню:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Дякую, що цікавитесь. Якщо бажаєте приєднатись до команди, переходьте на портал вакансій – https://company.diia.gov.ua/vacancies')

#Обробник відправки скарги
@bot.message_handler(content_types=['text', 'photo', 'video'])
def handle_input_message3(message):
    user_id = str(message.from_user.id)
    user_message = message.text if message.text else ''

    # Перевірка, чи є користувач в таблиці
    user_found = False
    rows = sheet.get_all_values()
    user_row = None
    for row in rows:
        if row[0] == user_id:
            user_found = True
            user_row = row
            break

    if message.text == "Назад":
        markup = create_improve_menu_markup()
        bot.send_message(message.chat.id, "Обери пункт меню:", reply_markup=markup)
    elif user_found:
        admin_chat_id = user_row[4]  # Значення п'ятого стовпця рядка - ADMIN_CHAT_ID
        admin_markup = types.InlineKeyboardMarkup()
        reply_button = types.InlineKeyboardButton(text="Відповісти", callback_data=f"reply_{user_id}")
        admin_markup.add(reply_button)

        if message.photo:
            photo_id = message.photo[-1].file_id
            photo_caption = f"<b>Користувач {user_row[3]} надіслав фото скарги з описом:</b>"
            if message.caption:
                photo_caption += f"\n\n{message.caption}"
            bot.send_photo(admin_chat_id, photo_id, caption=photo_caption, reply_markup=admin_markup, parse_mode="HTML")
        elif message.video:
            video_id = message.video.file_id
            video_caption = f"<b>Користувач {user_row[3]} надіслав відео скарги з описом:</b>"
            if message.caption:
                video_caption += f"\n\n{message.caption}"
            bot.send_video(admin_chat_id, video_id, caption=video_caption, reply_markup=admin_markup, parse_mode="HTML")
        else:
            admin_message = f"<b>Користувач {user_row[3]} надсилає скаргу:</b>\n\n{user_message}"
            bot.send_message(admin_chat_id, admin_message, reply_markup=admin_markup, parse_mode="HTML")

        bot.send_message(message.chat.id, "Дякую за ваше повідомлення. Адміністратор отримав повідомлення і відповість найближчим часом.")
        markup = create_main_menu_markup(user_id)
        bot.send_message(message.chat.id, "Обери пункт меню:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Дякую, що цікавитесь. Якщо бажаєте приєднатись до команди, переходьте на портал вакансій – https://company.diia.gov.ua/vacancies')

def handle_input_message4(message):
    user_id = str(message.from_user.id)
    user_message = message.text if message.text else ''

    # Перевірка, чи є користувач в таблиці
    user_found = False
    rows = sheet.get_all_values()
    user_row = None
    for row in rows:
        if row[0] == user_id:
            user_found = True
            user_row = row
            break

    if message.text == "Назад":
        markup = create_improve_menu_markup()
        bot.send_message(message.chat.id, "Обери пункт меню:", reply_markup=markup)
    elif user_found:
        admin_chat_id = user_row[7]  # Значення сьомого стовпця рядка - ADMIN_CHAT_ID
        admin_markup = types.InlineKeyboardMarkup()
        reply_button = types.InlineKeyboardButton(text="Відповісти", callback_data=f"reply_{user_id}")
        admin_markup.add(reply_button)

        if message.photo:
            photo_id = message.photo[-1].file_id
            photo_caption = f"<b>Користувач {user_row[3]} ділиться з тобою фото випадку:</b>"
            if message.caption:
                photo_caption += f"\n\n{message.caption}"
            bot.send_photo(admin_chat_id, photo_id, caption=photo_caption, reply_markup=admin_markup, parse_mode="HTML")
        elif message.video:
            video_id = message.video.file_id
            video_caption = f"<b>Користувач {user_row[3]} ділиться з тобою відео випадку:</b>"
            if message.caption:
                video_caption += f"\n\n{message.caption}"
            bot.send_video(admin_chat_id, video_id, caption=video_caption, reply_markup=admin_markup, parse_mode="HTML")
        else:
            admin_message = f"<b>Користувач {user_row[3]} ділиться з тобою випадком:</b>\n\n{user_message}"
            bot.send_message(admin_chat_id, admin_message, reply_markup=admin_markup, parse_mode="HTML")

        bot.send_message(message.chat.id, "Дякую за твоє повідомлення. Команда комунікації отримала повідомлення і відповість найближчим часом.")
        markup = create_main_menu_markup(user_id)
        bot.send_message(message.chat.id, "Обери пункт меню:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Дякую, що цікавитесь. Якщо бажаєте приєднатись до команди, переходьте на портал вакансій – https://company.diia.gov.ua/vacancies')

def handle_input_message5(message):
    user_id = str(message.from_user.id)
    user_message = message.text if message.text else ''

    # Перевірка, чи є користувач в таблиці
    user_found = False
    rows = sheet.get_all_values()
    user_row = None
    for row in rows:
        if row[0] == user_id:
            user_found = True
            user_row = row
            break

    if message.text == "Назад":
        markup = create_improve_menu_markup()
        bot.send_message(message.chat.id, "Обери пункт меню:", reply_markup=markup)
    elif user_found:
        admin_chat_id = user_row[7]  # Значення сьомого стовпця рядка - ADMIN_CHAT_ID
        admin_markup = types.InlineKeyboardMarkup()
        reply_button = types.InlineKeyboardButton(text="Відповісти", callback_data=f"reply_{user_id}")
        admin_markup.add(reply_button)

        if message.photo:
            photo_id = message.photo[-1].file_id
            photo_caption = f"<b>Користувач {user_row[3]} ставить питання та надсилає фото:</b>"
            if message.caption:
                photo_caption += f"\n\n{message.caption}"
            bot.send_photo(admin_chat_id, photo_id, caption=photo_caption, reply_markup=admin_markup, parse_mode="HTML")
        elif message.video:
            video_id = message.video.file_id
            video_caption = f"<b>Користувач {user_row[3]} ставить питання та ділиться з тобою відео:</b>"
            if message.caption:
                video_caption += f"\n\n{message.caption}"
            bot.send_video(admin_chat_id, video_id, caption=video_caption, reply_markup=admin_markup, parse_mode="HTML")
        else:
            admin_message = f"<b>Користувач {user_row[3]} ставить питання:\n\n{user_message}</b>"
            bot.send_message(admin_chat_id, admin_message, reply_markup=admin_markup, parse_mode="HTML")

        bot.send_message(message.chat.id, "Дякую за твоє повідомлення. Команда комунікації отримала повідомлення і відповість найближчим часом.")
        markup = create_main_menu_markup(user_id)
        bot.send_message(message.chat.id, "Обери пункт меню:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Дякую, що цікавитесь. Якщо бажаєте приєднатись до команди, переходьте на портал вакансій – https://company.diia.gov.ua/vacancies')

# Змінна для зберігання кількості натискань для кожного користувача під кожним постом
post_click_counts = {}

# Функція для оновлення кількості натискань на кнопку 🔥 для кожного користувача під кожним постом
def update_button_counts():
    for post_id, user_counts in post_click_counts.items():
        total_clicks = sum(user_data["click_count"] for user_data in user_counts.values())
        admin_markup = types.InlineKeyboardMarkup()
        reply_button = types.InlineKeyboardButton(text=f"🔥 {total_clicks}", callback_data=f"click_{post_id}")
        admin_markup.add(reply_button)

        for user_id, data in user_counts.items():
            message_id = data["message_id"]
            # Перевіряємо, чи змінилась кількість натискань перед оновленням повідомлення
            if data["click_count"] != total_clicks:
                try:
                    bot.edit_message_reply_markup(user_id, message_id, reply_markup=admin_markup)
                except telebot.apihelper.ApiTelegramException as e:
                    if "message is not modified" in str(e).lower():
                        # Ігноруємо помилку, якщо повідомлення не змінилося
                        pass
                    else:
                        # Якщо відбулася інша помилка, можна додати код для обробки цієї помилки (за потреби)
                        pass

def handle_input_message6(message):
    user_id = str(message.from_user.id)
    user_message = message.text if message.text else ''

    # Перевірка, чи є користувач в таблиці
    user_found = False
    rows = sheet.get_all_values()
    user_row = None
    for row in rows:
        if row[0] == user_id:
            user_found = True
            user_row = row
            break

    if message.text == "Назад":
        markup = create_improve_menu_markup()
        bot.send_message(message.chat.id, "Обери пункт меню:", reply_markup=markup)
    elif user_found:
        admin_chat_id = user_row[7]  # Значення сьомого стовпця рядка - ADMIN_CHAT_ID
        post_id = message.message_id  # Унікальний ID кожного посту, який відправляємо
        user_counts = post_click_counts.setdefault(post_id, {})
        click_count = user_counts.get(user_id, {"click_count": 0, "message_id": None})["click_count"]
        reply_button = types.InlineKeyboardButton(text=f"🔥 {click_count}", callback_data=f"click_{post_id}")
        admin_markup = types.InlineKeyboardMarkup()
        admin_markup.add(reply_button)

        # Замінюємо надсилання повідомлень звичайному повідомленню користувача на масове надсилання всім користувачам
        user_ids = [row[0] for row in rows if row[0]]  # Всі ID користувачів з першого стовпчика таблиці
        for user_id in user_ids:
            try:
                if message.photo:
                    photo_id = message.photo[-1].file_id
                    photo_caption = f""
                    if message.caption:
                        photo_caption += f"\n{message.caption}"
                    bot.send_photo(user_id, photo_id, caption=photo_caption, reply_markup=admin_markup)
                elif message.video:
                    video_id = message.video.file_id
                    video_caption = f""
                    if message.caption:
                        video_caption += f"\n{message.caption}"
                    bot.send_video(user_id, video_id, caption=video_caption, reply_markup=admin_markup)
                else:
                    admin_message = f"{user_message}"
                    bot.send_message(user_id, admin_message, reply_markup=admin_markup)

            except telebot.apihelper.ApiTelegramException as e:
                if "chat not found" in str(e).lower():
                    # Ігноруємо помилку, якщо чат не знайдено
                    pass
                else:
                    # Якщо відбулася інша помилка, можна додати код для обробки цієї помилки (за потреби)
                    pass

        bot.send_message(message.chat.id, "Дякую за твоє повідомлення. Я надіслав його всім менеджерам")
        markup = create_main_admin_issue()
        bot.send_message(message.chat.id, "Обери пункт меню:", reply_markup=markup)

        # Пауза у 1 секунду перед надсиланням наступного повідомлення
        time.sleep(0.5)

    else:
        bot.send_message(message.chat.id, 'Дякую, що цікавитесь. Якщо бажаєте приєднатись до команди, переходьте на портал вакансій – https://company.diia.gov.ua/vacancies')

@bot.callback_query_handler(func=lambda call: call.data.startswith("click_"))
def handle_click_button(call):
    user_id = str(call.from_user.id)
    post_id = call.data.replace("click_", "")

    # Перевірка, чи існує запис про кількість натискань для цього користувача та поста
    user_counts = post_click_counts.get(post_id, {})
    click_count = user_counts.get(user_id, {"click_count": 0, "message_id": None})["click_count"]

    # Перевірка, чи користувач вже натиснув кнопку 🔥
    if click_count >= 1:
        bot.answer_callback_query(call.id, "Ви вже натиснули кнопку 🔥", show_alert=True, cache_time=1)
    else:
        # Збільшення кількості натискань для користувача під цим постом
        user_counts[user_id] = {"click_count": click_count + 1, "message_id": call.message.message_id}
        post_click_counts[post_id] = user_counts

        # Оновлення кількості натискань на кнопку 🔥
        update_button_counts()

        # Відповідь користувачеві про успішне натискання
        bot.answer_callback_query(call.id, "Ви натиснули кнопку 🔥", cache_time=1)


# Обробник натискання кнопки "Організація роботи"
@bot.message_handler(func=lambda message: message.text == "Організація роботи")
def handle_work_organization_button(message):
    chat_id = message.chat.id
    if user_exists(chat_id):
        markup = create_work_organization_menu_markup()
        bot.send_message(chat_id, "Обери пункт меню:", reply_markup=markup)
    else:
        bot.send_message(chat_id, 'Дякую, що цікавитесь. Якщо бажаєте приєднатись до команди, переходьте на портал вакансій – https://company.diia.gov.ua/vacancies')

# Перевірка, чи користувач присутній в таблиці
def user_exists(user_id):
    user_id = str(user_id)
    rows = sheet.get_all_values()
    for row in rows:
        if row[0] == user_id:
            return True
    return False

# Обробник кнопки "Назад" у підменю "Запропонувати скрипт", "Запропонувати сервіс", "Анонімно поскаржитись"
@bot.message_handler(func=lambda message: message.text == "Назад")
def handle_back_button(message):
    markup = create_improve_menu_markup()
    bot.send_message(message.chat.id, "Обери пункт меню:", reply_markup=markup)

# Обробник натискання кнопки "Графік відпусток"
@bot.message_handler(func=lambda message: message.text == "Графік відпусток")
def handle_vacation_schedule_button(message):
    user_id = str(message.from_user.id)
    rows = sheet.get_all_values()
    user_row = None
    for row in rows:
        if row[0] == user_id:
            user_row = row
            break

    if user_row:
        vacation_schedule = user_row[5]  # Значення 6-ої колонки рядка - Графік відпусток
        if vacation_schedule:
            bot.send_message(message.chat.id, f"Твій графік відпусток:\n\n{vacation_schedule}")
        else:
            bot.send_message(message.chat.id, "Ти ще не зареєстрований. Звернися до тімліда.")
        markup = create_work_organization_menu_markup()
        bot.send_message(message.chat.id, "Памʼятай, заява пишеться за 15 робочих днів до відпустки", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Дякую, що цікавитесь. Якщо бажаєте приєднатись до команди, переходьте на портал вакансій – https://company.diia.gov.ua/vacancies")
        markup = create_main_menu_markup(user_id)
        bot.send_message(message.chat.id, "Обери пункт меню:", reply_markup=markup)


# Обробник натискання кнопки "Робочі дні"
@bot.message_handler(func=lambda message: message.text == "Робочі дні")
def handle_working_days(message):
    # Перевірка, чи є користувач в таблиці
    user_id = str(message.from_user.id)
    first_name = message.from_user.first_name
    username = message.from_user.username

    user_found = False
    rows = sheet.get_all_values()
    for row in rows:
        if row[0] == user_id or row[1] == first_name or row[2] == username:
            user_found = True
            if not row[0]:
                row[0] = user_id
            if not row[1]:
                row[1] = first_name
            if not row[2]:
                row[2] = username
            sheet.update(f'D{rows.index(row) + 1}', [[row[3]]])
            break

    if user_found:
        # Користувач присутній в таблиці
        cell_value = sheet.acell('G' + str(rows.index(row) + 1)).value
        if cell_value == '1':
            bot.send_message(message.chat.id, f"В цьому місяці ми працюємо в такі дні:\n\n{sheet2.acell('A2').value}")
        elif cell_value == '2':
            bot.send_message(message.chat.id, f"В цьому місяці ми працюємо в такі дні:\n\n{sheet2.acell('B2').value}")
        else:
            bot.send_message(message.chat.id, "На жаль, не вдалось визначити з якої ти зміни.")
    else:
        # Користувач відсутній в таблиці
        bot.send_message(message.chat.id, 'Дякую, що цікавитесь. Якщо бажаєте приєднатись до команди, переходьте на портал вакансій – https://company.diia.gov.ua/vacancies')

# Обробник натискання кнопки "Поділитись випадком"
@bot.message_handler(func=lambda message: message.text == "Поділитись випадком")
def handle_share_case(message):
    user_id = str(message.from_user.id)
    user_message = message.text

    # Перевірка, чи є користувач в таблиці
    user_found = False
    rows = sheet.get_all_values()
    user_row = None
    for row in rows:
        if row[0] == user_id:
            user_found = True
            user_row = row
            break

    if user_found:
        admin_chat_id = user_row[7]  # Значення восьмого стовпця рядка - ID адміністратора
        admin_message = f"Користувач {user_row[3]} надіслав повідомлення з проблемою:\n\n{user_message}"
        admin_markup = types.InlineKeyboardMarkup()
        reply_button = types.InlineKeyboardButton(text="Відповісти", callback_data=f"reply_{user_id}")
        admin_markup.add(reply_button)
        bot.send_message(admin_chat_id, admin_message, reply_markup=admin_markup)
        bot.send_message(message.chat.id, "Дякуємо за ваше повідомлення. Адміністратор отримав повідомлення і відповість найближчим часом.")
        markup = create_main_menu_markup(user_id)
        bot.send_message(message.chat.id, "Оберіть пункт меню:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Дякуємо, що цікавитесь. Якщо бажаєте приєднатись до команди, переходьте на портал вакансій – https://company.diia.gov.ua/vacancies')

# Обробник натискання кнопки "Поставити питання"
@bot.message_handler(func=lambda message: message.text == "Поставити питання")
def handle_ask_question(message):
    user_id = str(message.from_user.id)
    user_message = message.text

    # Перевірка, чи є користувач в таблиці
    user_found = False
    rows = sheet.get_all_values()
    user_row = None
    for row in rows:
        if row[0] == user_id:
            user_found = True
            user_row = row
            break

    if user_found:
        admin_chat_id = user_row[7]  # Значення восьмого стовпця рядка - ID адміністратора
        admin_message = f"Користувач {user_row[3]} надіслав повідомлення з питанням:\n\n{user_message}"
        admin_markup = types.InlineKeyboardMarkup()
        reply_button = types.InlineKeyboardButton(text="Відповісти", callback_data=f"reply_{user_id}")
        admin_markup.add(reply_button)
        bot.send_message(admin_chat_id, admin_message, reply_markup=admin_markup)
        bot.send_message(message.chat.id, "Дякуємо за ваше повідомлення. Адміністратор отримав повідомлення і відповість найближчим часом.")
        markup = create_main_menu_markup(user_id)
        bot.send_message(message.chat.id, "Оберіть пункт меню:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Дякуємо, що цікавитесь. Якщо бажаєте приєднатись до команди, переходьте на портал вакансій – https://company.diia.gov.ua/vacancies')

# Обробник натискання кнопки "Назад"
@bot.message_handler(func=lambda message: message.text == "Назад")
def handle_back(message):
    markup = create_improve_menu_markup()
    bot.send_message(message.chat.id, "Оберіть пункт меню:", reply_markup=markup)

# Обробник введення повідомлення користувача
@bot.message_handler(content_types=['text'])
def handle_input_message(message):
    user_id = str(message.from_user.id)
    user_message = message.text

    # Перевірка, чи є користувач в таблиці
    user_found = False
    rows = sheet.get_all_values()
    user_row = None
    for row in rows:
        if row[0] == user_id:
            user_found = True
            user_row = row
            break

    if user_found:
        admin_chat_id = user_row[4]  # Значення восьмого стовпця рядка - ID адміністратора
        admin_message = f"Користувач {user_row[3]} надіслав повідомлення:\n\n{user_message}"
        admin_markup = types.InlineKeyboardMarkup()
        reply_button = types.InlineKeyboardButton(text="Відповісти", callback_data=f"reply_{user_id}")
        admin_markup.add(reply_button)
        bot.send_message(admin_chat_id, admin_message, reply_markup=admin_markup)
        bot.send_message(message.chat.id, "Дякуємо за ваше повідомлення. Адміністратор отримав повідомлення і відповість найближчим часом.")
        markup = create_main_menu_markup(user_id)
        bot.send_message(message.chat.id, "Оберіть пункт меню:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Дякуємо, що цікавитесь. Якщо бажаєте приєднатись до команди, переходьте на портал вакансій – https://company.diia.gov.ua/vacancies')

@bot.callback_query_handler(func=lambda call: call.data == "send_to_all")
def handle_menu_callback(callback_query):
    chat_id = callback_query.message.chat.id

    # Відправка повідомлення адміністратором
    bot.send_message(chat_id, "Введіть повідомлення для користувачів:")

    # Зберігання стану "очікування повідомлення від користувача"
    bot.register_next_step_handler_by_chat_id(chat_id, handle_admin_message)

def handle_admin_message(message):
    # Отримання повідомлення від адміністратора
    admin_message = message.text if message.text else ''
    admin_chat_id = message.chat.id

    # Отримання медіаматеріалів, якщо вони є
    media = []
    if message.photo:
        media = message.photo
    elif message.video:
        media = [message.video]

    # Відправка повідомлення користувачам
    send_message_to_users(admin_message, media)

    # Відправка підтвердження адміністратору
    markup = types.InlineKeyboardMarkup()
    send_button = types.InlineKeyboardButton(text="Відправити", callback_data="confirm_send")
    cancel_button = types.InlineKeyboardButton(text="Скасувати", callback_data="cancel_send")
    markup.row(send_button, cancel_button)
    bot.send_message(admin_chat_id, f"{admin_message}", reply_markup=markup)

def send_message_to_users(message, media):
    # Отримання списку користувачів з першого стовпця таблиці
    user_ids = get_user_ids()

    # Відправка повідомлення кожному користувачу
    for user_id in user_ids:
        # Відправка повідомлення без медіа
        if not media:
            bot.send_message(user_id, message)
        else:
            # Відправка повідомлення з медіа
            for media_item in media:
                if isinstance(media_item, types.PhotoSize):
                    bot.send_photo(user_id, media_item.file_id, caption=message)
                elif isinstance(media_item, types.Video):
                    bot.send_video(user_id, media_item.file_id, caption=message)

#Обробка натискання кнопки Назад
@bot.message_handler(func=lambda message: message.text == "Назад")
def handle_back_button(message):
    markup = create_improve_menu_markup()
    bot.send_message(message.chat.id, "Обери пункт меню:", reply_markup=markup)

# Створення розмітки для основного меню
def create_main_menu_markup(user_id):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(types.KeyboardButton("Покращити роботу"), types.KeyboardButton("Організація роботи"))
    markup.add(types.KeyboardButton("Відділ комунікації"))
    # Перевірка, чи є користувач в таблиці
    user_found = False
    rows = sheet.get_all_values()
    for row in rows:
        if row[8] == user_id:  # Перевірка у стовпці 3 (ADMIN_CHAT_ID)
            user_found = True
            break

    if user_found:
        markup.add(types.KeyboardButton("Адміністративна панель"))

    return markup

# Створення розмітки для підменю "Запропонувати скрипт", "Запропонувати сервіс", "Анонімно поскаржитись"
def create_improve_menu_markup():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(types.KeyboardButton("Запропонувати скрипт"), types.KeyboardButton("Запропонувати сервіс"))
    markup.add(types.KeyboardButton("Анонімно поскаржитись"))
    markup.add(types.KeyboardButton("Назад"))
    return markup

#Створення меню розділу Організація роботи
def create_work_organization_menu_markup():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(types.KeyboardButton("Графік відпусток"), types.KeyboardButton("Зразки заяв"))
    markup.add(types.KeyboardButton("Робочі дні"), types.KeyboardButton("Питання оплати"))
    markup.add(types.KeyboardButton("Назад"))
    return markup

# Створення розмітки для введення повідомлення
def create_input_message_markup():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add(types.KeyboardButton("Назад"))
    return markup

# Створення розмітки для відправки повідомлення
def create_output_message_markup():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add(types.KeyboardButton("Скасувати"))
    return markup

# Створення меню зразків заяв
def create_application_samples_menu_markup():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(types.KeyboardButton("Відпустка 14 днів"), types.KeyboardButton("Відпустка 10 днів"))
    markup.add(types.KeyboardButton("Відпустка 10 днів на 2 дати"), types.KeyboardButton("Відпустка в честь ДР"))
    markup.add(types.KeyboardButton("За власний рахунок"), types.KeyboardButton("Зміна реквізитів"))
    markup.add(types.KeyboardButton("Назад"))
    return markup

# Створення розмітки для Питання оплати
def create_main_payment_issue():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(types.KeyboardButton("Заробітна плата"), types.KeyboardButton("Лікарняні"))
    markup.add(types.KeyboardButton("Відпустки"), types.KeyboardButton("Назад"))
    return markup

# Створення розмітки для Відділ Комунікації
def create_main_communication_issue():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(types.KeyboardButton("Поділитись випадком"), types.KeyboardButton("Поставити питання"))
    markup.add(types.KeyboardButton("Назад"))
    return markup

# Створення розмітки для Адміністративної панелі
def create_main_admin_issue():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(types.KeyboardButton("Відправити пост"))
    markup.add(types.KeyboardButton("Назад"))
    return markup


# Функція для надсилання повідомлення про помилку адміністратору
def send_error_message(exc_type, exc_value, exc_traceback):
    # Отримуємо рядок з трейсбеком помилки
    traceback_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))

    # Ідентифікатор адміністратора, якому буде надіслано повідомлення про помилку
    admin_chat_id = 335223450  # Замініть на ідентифікатор свого адміністратора

    # Відправляємо повідомлення про помилку адміністратору
    bot.send_message(admin_chat_id, f"Сталася помилка:\n\n{traceback_str}")


# Встановлюємо send_error_message як глобальний обробник винятків
sys.excepthook = send_error_message

# Змінна для збереження кількості користувачів
users_count = 0

def send_continuation_message(admin_chat_id):
    global users_count  # Позначаємо, що будемо використовувати глобальну змінну

    # Тут ви можете створити повідомлення, яке буде нагадувати про продовження роботи
    message = f"✅ Бот продовжує працювати!\nКількість користувачів, що користувалися ботом: {users_count}"
    bot.send_message(admin_chat_id, message)

def check_continuation():
    global users_count  # Позначаємо, що будемо використовувати глобальну змінну

    # Збільшуємо кількість користувачів на 1 після кожної успішної взаємодії з ботом
    users_count += 1
    admin_chat_id = 335223450  # Замініть на відповідний chat_id адміністратора
    send_continuation_message(admin_chat_id)

# Розклад для нагадування про продовження роботи кожні 4 години
schedule.every(6).hours.do(check_continuation)

def bot_polling():
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(e)
            time.sleep(15)

# Запускаємо метод bot_polling у фоновому режимі
polling_thread = threading.Thread(target=bot_polling)
polling_thread.daemon = True
polling_thread.start()

# Цикл для перевірки розкладу кожну хвилину
while True:
    try:
        schedule.run_pending()
        time.sleep(180)
    except KeyboardInterrupt:
        break
