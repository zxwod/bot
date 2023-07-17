import telebot
from telebot import types
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import qrcode
import cv2
from datetime import datetime
from pyzbar.pyzbar import decode
from pyzbar import pyzbar
import urllib
import os
import time
from PIL import Image


BOT_TOKEN = "5675907613:AAETwaa8fJlZnMF0FmfCO-nrgy-WZwdrKIg"

bot = telebot.TeleBot(BOT_TOKEN)

# Функція для отримання даних з Google Таблиці
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(credentials)
# Відкриття Гугл таблиці за допомогою ідентифікатора
sheet1 = client.open_by_key('1L2_iDAMn8L5mFrZ9iIkOFESOy7VlkWuLED4Gk33JxKo').sheet1

# Обробник натискання кнопки Старт
@bot.message_handler(commands=['start'])
def handle_start(message):
    # Текст повідомлення
    text = "<b>Я твій помічник в реєстрації гостей на цьому заході.</b>\n\n"\
           "Щоб зареєструвати користувача в цьому заході, натисни кнопку Сканувати QR, відкрий камеру та сфотографуй QR код гостя та надійшли його в цей чат."

    # Створення клавіатури з кнопкою "Сканувати QR"
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    scan_button = types.KeyboardButton("Сканувати QR")
    keyboard.add(scan_button)

    # Перевірка ідентифікатора користувача
    if message.from_user.id == 335223450:
        # Додавання кнопки "Згенерувати QR" для певного ідентифікатора користувача
        generate_button = types.KeyboardButton("Згенерувати QR")
        keyboard.add(generate_button)

    # Відправлення повідомлення з виділеним текстом
    bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=keyboard)

def is_user_registered(user_id):
    # Отримання всіх значень з першої колонки аркуша
    column_values = sheet1.col_values(1)
    # Перевірка, чи є Id користувача серед значень
    return str(user_id) in column_values

def delete_previous_messages(chat_id, message_id, count=3):
    for _ in range(count):
        try:
            bot.delete_message(chat_id, message_id - 1)
            message_id -= 1
        except Exception as e:
            print(f"Помилка видалення повідомлення: {e}")
            break

# Обробник події для кнопки "Сканувати QR"
@bot.message_handler(func=lambda message: message.text == 'Сканувати QR')
def handle_scan_qr_button(message):
    chat_id = message.chat.id
    # Видалення клавіатури
    remove_keyboard = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, "Будь ласка, надішліть фото QR-коду для сканування.", reply_markup=remove_keyboard)

    # Відправлення файлу 1.gif разом з повідомленням
    gif_path = '1.mp4'
    with open(gif_path, 'rb') as file:
        bot.send_document(chat_id, file)

    # Очікування фото від адміністратора
    bot.register_next_step_handler(message, process_qr_photo)

# Метод для обробки отриманого фото з QR-кодом
def process_qr_photo(message):
    chat_id = message.chat.id

    # Перевірка, чи було надіслано фото
    if message.photo:
        # Отримання об'єкту фото
        photo_obj = message.photo[-1]

        # Отримання ідентифікатора фото
        photo_id = photo_obj.file_id

        # Отримання фото за допомогою методу `download`
        photo_file = bot.get_file(photo_id)
        photo_content = bot.download_file(photo_file.file_path)

        # Збереження фото на сервері
        photo_path = f'qr_code_photos/{photo_id}.jpg'
        with open(photo_path, 'wb') as file:
            file.write(photo_content)

        # Видалення попередніх повідомлень в чаті
        delete_previous_messages(chat_id, message.message_id)

        # Аналіз QR-коду
        qr_code_data = scan_qr_code(photo_path)

        if qr_code_data:
            process_qr_code(qr_code_data, chat_id)
        else:
            # Якщо QR-код не розпізнано, повідомляємо про помилку
            keyboard = create_keyboard()
            bot.send_message(chat_id, '😭Помилка: QR-код не знайдено на фото', reply_markup=keyboard)

        # Видалення збереженого фото
        os.remove(photo_path)

    else:
        # Видалення попередніх повідомлень в чаті
        delete_previous_messages(chat_id, message.message_id)

        # Якщо адміністратор не надіслав фото, відправити повідомлення про помилку
        bot.send_message(chat_id, '😭Помилка: Будь ласка, надішліть фото з QR-кодом для сканування.')

    # Очікування наступного фото
    wait_for_qr_photo(chat_id)

# Оновлений метод для очікування фото від адміністратора
def wait_for_qr_photo(chat_id):
    # Видалення клавіатури
    remove_keyboard = types.ReplyKeyboardRemove()
    bot.send_message(chat_id, "Будь ласка, надішліть наступне фото QR-коду для сканування.", reply_markup=remove_keyboard)

    # Очікування фото від адміністратора
    bot.register_next_step_handler_by_chat_id(chat_id, process_qr_photo)

# Функція для видалення попередніх повідомлень
def delete_previous_messages(chat_id, message_id, count=3):
    for _ in range(count):
        try:
            bot.delete_message(chat_id, message_id - 1)
            message_id -= 1
        except Exception as e:
            print(f"Помилка видалення повідомлення: {e}")
            break

# Функція для створення клавіатури
def create_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    scan_button = types.KeyboardButton("Сканувати QR")
    keyboard.add(scan_button)
    return keyboard

# Метод для аналізу QR-коду на фото
def scan_qr_code(photo_path):
    image = cv2.imread(photo_path)
    qr_codes = decode(image)
    qr_code_data = None

    for qr_code in qr_codes:
        qr_code_data = qr_code.data.decode("utf-8")
        break

    return qr_code_data

def process_qr_code(qr_code_data, chat_id):
    if qr_code_data:
        user_id = qr_code_data
        if is_user_registered(user_id):
            # Перевірка значення в 5-му стовпчику рядка користувача
            column_index = 5
            user_row = sheet1.find(str(user_id)).row
            cell_value = sheet1.cell(user_row, column_index).value

            if cell_value:
                # Якщо значення вже присутнє, повідомляємо про заборону проходу
                name, surname, profession = get_user_data(user_id)
                message = f'🚨Прохід заборонено – QR код вже був відсканованим\n\n'
                message += f'Користувач: {surname} {name}\n'
                message += f'Професія: {profession}'
                bot.send_message(chat_id, message)
            else:
                # Записуємо значення в 5-й стовпчик рядка користувача
                current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                user_row = sheet1.find(str(user_id)).row
                sheet1.update_cell(user_row, column_index, f'Arrived')

                # Виконуємо інші дії, які потрібно виконати при успішному скануванні
                name, surname, profession = get_user_data(user_id)
                message = f'✅Прохід дозволено, зафіксовано відвідування заходу\n\n'
                message += f'Користувач: {surname} {name}\n'
                message += f'Професія: {profession}'
                bot.send_message(chat_id, message)
        else:
            # Якщо користувач не зареєстрований, повідомляємо про помилку
            bot.send_message(chat_id, '🚨Помилка: QR-код не зареєстровано в системі та заборонене відвідування заходу')
    else:
        # Якщо ключ 'user_id' відсутній у qr_code_data, повідомляємо про помилку
        bot.send_message(chat_id, '🚨Помилка: Невірний формат QR-коду')

# Функція для отримання даних користувача з таблиці
def get_user_data(user_id):
    # Отримання рядка користувача за допомогою його ID
    user_row = sheet1.find(str(user_id)).row

    # Отримання значень з потрібних стовпчиків
    name = sheet1.cell(user_row, 2).value
    surname = sheet1.cell(user_row, 3).value
    profession = sheet1.cell(user_row, 4).value

    return name, surname, profession

# Оновлений метод для очікування фото від адміністратора
def wait_for_qr_photo(chat_id):
    # Видалення клавіатури
    remove_keyboard = types.ReplyKeyboardRemove()
    bot.send_message(chat_id, "Будь ласка, надішліть наступне фото QR-коду для сканування.", reply_markup=remove_keyboard)

    # Очікування фото від адміністратора
    bot.register_next_step_handler_by_chat_id(chat_id, process_qr_photo)


# Налаштування обробки натискання кнопки "Згенерувати QR"
@bot.message_handler(func=lambda message: message.text == "Згенерувати QR")
def generate_qr_button_handler(message):
    generate_images()
    bot.reply_to(message, "Всі QR-коди згенеровано.")

# Перевірка наявності папки "qr_code_photos"
if not os.path.exists("qr_code_photos"):
    os.makedirs("qr_code_photos")

# Завантаження даних з Google Sheets
def load_user_data():

    # Отримання значень з першої колонки (ID користувачів)
    id_values = sheet1.col_values(1)

    # Отримання значень з інших колонок (інші дані про користувачів)
    name_values = sheet1.col_values(2)
    last_name_values = sheet1.col_values(3)

    # Створення списку словників з даними користувачів
    user_data = []
    for i in range(1, len(id_values)):
        user_data.append({
            "id": id_values[i],
            "first_name": name_values[i],
            "last_name": last_name_values[i]
        })

    return user_data

# Функція для генерації QR-коду з логотипом
def generate_qr_code(user_id, first_name, last_name):
    qr_data = f"{user_id}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_img = qr_img.resize((450, 450))  # Зміна розміру QR-коду

    # Завантаження логотипу
    logo_path = os.path.join(os.getcwd(), "logo.png")
    logo = Image.open(logo_path)
    logo = logo.resize((225, 165))  # Зміна розміру логотипу

    # Створення нового зображення з необхідними розмірами
    image_width = 500
    image_height = 750
    new_image = Image.new("RGBA", (image_width, image_height), "white")

    # Розміщення QR-коду у верхній частині зображення
    qr_x = int((image_width - qr_img.width) / 2)
    qr_y = 25
    new_image.paste(qr_img, (qr_x, qr_y))

    # Розміщення логотипу у нижній частині зображення
    logo_x = int((image_width - logo.width) / 2)
    logo_y = image_height - logo.height - 75
    new_image.paste(logo, (logo_x, logo_y), logo)

    # Збереження зображення з назвою прізвище+ім'я+id.png
    image_filename = f"{last_name}_{first_name}_{user_id}.png"
    image_path = os.path.join(os.getcwd(), "qr_code_photos", image_filename)
    new_image.save(image_path)

    return image_path

# Генерація зображень для всіх користувачів
def generate_images():
    # Отримання даних про користувачів
    user_data = load_user_data()

    # Генерація зображення для кожного користувача
    for user in user_data:
        generate_qr_code(user["id"], user["first_name"], user["last_name"])

# Запуск бота
if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(e)
            time.sleep(15)