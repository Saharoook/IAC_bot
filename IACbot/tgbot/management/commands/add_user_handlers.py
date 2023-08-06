from .bot import *


logging.basicConfig(level=logging.WARNING, filename="tgbot/management/logs/bot_add_user.log",
                    format="%(asctime)s %(levelname)s %(message)s")


def start_add_user_full_name(message):
    user = TgUser()

    user.full_name = message.text

    bot.send_message(message.chat.id, 'Введите организацию')
    bot.register_next_step_handler(message, add_user_organization, user)


def add_user_organization(message, user):
    try:
        organization = Organization.objects.get(organization_name=message.text)
        user.user_organization = organization

    except Exception as ex:
        logging.info(ex)
        bot.send_message(message.chat.id, 'Такой орагнизации нет \nВведите организацию')
        bot.register_next_step_handler(message, add_user_organization, user)

    else:
        bot.send_message(message.chat.id, 'Введите должность')
        bot.register_next_step_handler(message, add_user_job_title, user)


def add_user_job_title(message, user):
    user.job_title = message.text

    bot.send_message(message.chat.id, 'Введите номер телефона')
    bot.register_next_step_handler(message, add_user_phone_number, user)


def add_user_phone_number(message, user):
    user.phone_number = message.text

    bot.send_message(message.chat.id, 'Введите рабочий номер телефона')
    bot.register_next_step_handler(message, add_user_email, user)


def add_user_email(message, user):
    user.phone_number_work = message.text

    bot.send_message(message.chat.id, 'Введите e-mail')
    bot.register_next_step_handler(message, add_user_tg_id, user)


def add_user_tg_id(message, user):
    user.email_address = message.text

    bot.send_message(message.chat.id, 'Введите ID пользователя в телеграмм')
    bot.register_next_step_handler(message, add_user_description, user)


def add_user_description(message, user):
    user.tg_id = message.text

    user_role_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    admin = types.KeyboardButton('Админ')
    basic = types.KeyboardButton('Обычный')
    user_role_markup.add(admin, basic)

    bot.send_message(message.chat.id, 'Выберите роль пользователя', reply_markup=user_role_markup)

    bot.register_next_step_handler(message, add_user_change_user_role, user)


def add_user_change_user_role(message, user):
    if message.text == 'Админ':
        user.user_role = 'AD'
    else:
        user.user_role = 'BS'

    user_photo_flag_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    yes = types.KeyboardButton('Да')
    no = types.KeyboardButton('Нет')
    user_photo_flag_markup.add(yes, no)

    bot.send_message(message.chat.id, 'Хотите добавить фото?', reply_markup=user_photo_flag_markup)
    bot.register_next_step_handler(message, add_user_photo_change, user)


def add_user_photo_change(message, user):
    if message.text == 'Да':
        bot.send_message(message.chat.id, 'Отправьте фотографию в чат')
        bot.register_next_step_handler(message, add_user_add_photo, user)

    else:
        bot.send_message(message.chat.id, 'Введите описание')
        bot.register_next_step_handler(message, add_user_add_description, user)


def add_user_add_photo(message, user):

    user.save()

    path = 'media/tgbot/images/' + str(user.pk) + '.jpg'

    Image.open(requests.get(bot.get_file_url(message.photo[-1].file_id), stream=True).raw).save(path)
    user.user_photo = path

    bot.send_message(message.chat.id, 'Введите описание')

    bot.register_next_step_handler(message, add_user_add_description, user)


def add_user_add_description(message, user):
    user.description = message.text
    user_db_save(message, user)


