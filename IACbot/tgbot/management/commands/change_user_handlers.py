from .bot import *


logging.basicConfig(level=logging.WARNING, filename="tgbot/management/logs/bot_change.log",
                    format="%(asctime)s %(levelname)s %(message)s")


def start_change(message):

    try:
        user = TgUser.objects.get(pk=message.text)

    except Exception as ex:

        bot.send_message(message.chat.id, 'Пользователь не найден', reply_markup=markup)

    else:
        search_report(message, [user])

        change_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        full_name = types.KeyboardButton('ФИО')
        status = types.KeyboardButton('Статус')
        phone_number = types.KeyboardButton('Телефон')
        phone_number_work = types.KeyboardButton('Рабочий телефон')
        email = types.KeyboardButton('E-mail')
        organization = types.KeyboardButton('Организация')
        job_title = types.KeyboardButton('Должность')
        description = types.KeyboardButton('Описание')
        tg_id = types.KeyboardButton('ID телеграм')
        photo = types.KeyboardButton('Фото')
        ext = types.KeyboardButton('Выйти')
        change_markup.add(full_name, status, phone_number, phone_number_work, email, organization,
                          job_title, description, tg_id, photo, ext)

        bot.send_message(message.chat.id, 'Выберите необходимое поле',
                         reply_markup=change_markup)

        bot.register_next_step_handler(message, change_choice, user)


def change_choice(message, user):

    if message.text == 'ФИО':
        bot.send_message(message.chat.id, 'Введите новое ФИО')
        bot.register_next_step_handler(message, change_full_name, user)

    elif message.text == 'Статус':
        user_role_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        admin = types.KeyboardButton('Админ')
        basic = types.KeyboardButton('Обычный')
        user_role_markup.add(admin, basic)
        bot.send_message(message.chat.id, 'Выберите роль пользователя', reply_markup=user_role_markup)
        bot.register_next_step_handler(message, change_status, user)

    elif message.text == 'Телефон':
        bot.send_message(message.chat.id, 'Введите новый телефон')
        bot.register_next_step_handler(message, change_phone_number, user)

    elif message.text == 'Рабочий телефон':
        bot.send_message(message.chat.id, 'Введите новый телефон')
        bot.register_next_step_handler(message, change_phone_number_work, user)

    elif message.text == 'E-mail':
        bot.send_message(message.chat.id, 'Введите новый e-mail')
        bot.register_next_step_handler(message, change_email, user)

    elif message.text == 'Организация':

        bot.send_message(message.chat.id, 'Введите новую организацию')
        bot.register_next_step_handler(message, change_organization, user)

    elif message.text == 'Должность':

        bot.send_message(message.chat.id, 'Введите новую должность')
        bot.register_next_step_handler(message, change_job_title, user)

    elif message.text == 'Описание':

        bot.send_message(message.chat.id, 'Введите новое описание')
        bot.register_next_step_handler(message, change_description, user)

    elif message.text == 'ID телеграм':

        bot.send_message(message.chat.id, 'Введите новый ID телеграмм')
        bot.register_next_step_handler(message, change_tg_id, user)

    elif message.text == 'Фото':

        bot.send_message(message.chat.id, 'Отправьте в чат новую фотографию')
        bot.register_next_step_handler(message, change_photo, user)

    else:
        bot.send_message(message.chat.id, 'Выберите что вам надо', reply_markup=markup)


def change_full_name(message, user):

    user.full_name = message.text
    user_db_save(message, user)


def change_status(message, user):

    if message.text == 'Админ':
        user.user_role = 'AD'
    else:
        user.user_role = 'BS'

    user_db_save(message, user)


def change_phone_number(message, user):

    user.phone_number = message.text
    user_db_save(message, user)


def change_phone_number_work(message, user):

    user.phone_number_work = message.text
    user_db_save(message, user)


def change_email(message, user):

    user.email_address = message.text
    user_db_save(message, user)


def change_organization(message, user):
    try:
        organization = Organization.objects.get(organization_name=message.text)

    except Exception as ex:
        print('ORG ERROR:', ex)
        bot.send_message(message.chat.id, 'Такой орагнизации нет \nВведите организацию')
        bot.register_next_step_handler(message, change_organization, user)
    else:
        user.user_organization = organization
        user_db_save(message, user)


def change_job_title(message, user):

    user.job_title = message.text
    user_db_save(message, user)


def change_description(message, user):

    user.description = message.text
    user_db_save(message, user)


def change_tg_id(message, user):

    user.tg_id = message.text
    user_db_save(message, user)


def change_photo(message, user):

    path = 'media/tgbot/images/' + str(user.pk) + '.jpg'

    try:
        Image.open(requests.get(bot.get_file_url(message.photo[-1].file_id), stream=True).raw).save(path)

    except Exception as err:
        bot.send_message(message.chat.id, 'Что-то пошло не так', reply_markup=markup)

    else:
        user.user_photo = path
        user_db_save(message, user)

