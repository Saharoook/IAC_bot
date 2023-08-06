import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned
from telebot import TeleBot, types
from telebot import ExceptionHandler

from tgbot.models import TgUser, Organization
import logging

from PIL import Image

bot = TeleBot(settings.TELEGRAM_BOT_API_KEY)

logging.basicConfig(level=logging.WARNING, filename="tgbot/management/logs/bot_main.log",
                    format="%(asctime)s %(levelname)s %(message)s")

markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
search = types.KeyboardButton('Поиск')
add = types.KeyboardButton('Добавить')
change = types.KeyboardButton('Изменить')
delete = types.KeyboardButton('Удалить')
markup.add(search, add, change, delete)


class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        try:
            bot.enable_save_next_step_handlers(delay=2)
            bot.load_next_step_handlers()
            bot.infinity_polling()

        except Exception as ex:
            logging.critical(ex)


def verify(message):
    try:
        TgUser.objects.get(tg_id=message.chat.id)

    except MultipleObjectsReturned as error:
        logging.warning(error)
        bot.send_message(message.chat.id, 'Есть несколько аккаунтов с вашим ID. Обратитесь к администратору')
        return False

    except Exception as ex:
        return False

    else:

        return True


@bot.message_handler(commands=['update_nick'])
def update_nick_name(message):

    if verify(message):

        try:
            user = TgUser.objects.get(tg_id=message.chat.id)

            user.nick_name = message.from_user.username

            user.save()

        except Exception as ex:
            logging.info(ex)
            bot.send_message(message.chat.id, 'Произошла ошибка', reply_markup=markup)

        else:
            bot.send_message(message.chat.id, 'Данные успешно обновлены', reply_markup=markup)


@bot.message_handler(commands=['start'])
def start_message(message):

    if verify(message):
        bot.send_message(message.chat.id, 'Выберите что вам надо', reply_markup=markup)


@bot.message_handler(commands=['info'])
def info(message):

    if verify(message):
        bot.send_photo(message.chat.id, open('media/qr-code.gif', 'rb'), reply_markup=markup)


@bot.message_handler(commands=['iam'])
def my_account(message):

    if verify(message):

        try:
            user = TgUser.objects.get(tg_id=message.chat.id)

        except MultipleObjectsReturned as error:
            logging.warning(error)
            bot.send_message(message.chat.id, 'Есть несколько аккаунтов с вашим ID. Обратитесь к администратору')

        else:
            search_report(message, [user])


@bot.message_handler(commands=['org'])
def organization_list(message):
    flag = verify(message)

    if flag:

        organizations = Organization.objects.all()

        if len(organizations) != 0:

            reply = ''

            for organization in organizations:
                reply += organization.organization_name + '\n'

            bot.send_message(message.chat.id, reply, reply_markup=markup)


@bot.message_handler(content_types=['text'])
def message_menu(message):
    flag = verify(message)

    if flag:
        if message.text == 'Поиск':
            bot.send_message(message.chat.id, 'Введите информацию:', reply_markup=markup)
            bot.register_next_step_handler(message, search)

        elif message.text == 'Добавить':

            user = TgUser.objects.get(tg_id=message.chat.id)

            if user.user_role == 'BS':
                bot.send_message(message.chat.id, 'У вас нет доступа к этому функционалу', reply_markup=markup)

            else:
                bot.send_message(message.chat.id, 'Введите ФИО')
                bot.register_next_step_handler(message, start_add_user_full_name)

        elif message.text == 'Изменить':

            user = TgUser.objects.get(tg_id=message.chat.id)

            if user.user_role == 'BS':
                bot.send_message(message.chat.id, 'У вас нет доступа к этому функционалу', reply_markup=markup)

            else:
                bot.send_message(message.chat.id, 'Введите уникальный идентификатор пользователя')
                bot.register_next_step_handler(message, change_user_handlers.start_change)

        elif message.text == 'Удалить':

            user = TgUser.objects.get(tg_id=message.chat.id)

            if user.user_role == 'BS':
                bot.send_message(message.chat.id, 'У вас нет доступа к этому функционалу', reply_markup=markup)

            else:
                bot.send_message(message.chat.id, 'Введите уникальный идентификатор пользователя')
                bot.register_next_step_handler(message, start_delete)

        else:
            bot.send_message(message.chat.id, 'Я вас не понял', reply_markup=markup)


def search_report(message, users):
    chat_user = TgUser.objects.get(tg_id=message.chat.id)

    if chat_user.user_role == 'AD':
        for user in users:
            reply = ('ФИО: ' + user.full_name + '\n' + 'ID в телеграм: ' + str(user.tg_id) + '\n' +
                     'Ник в телеграмм: ' + user.nick_name + '\n' + 'Статус: ' + user.user_role + '\n' +
                     'Уникальный идентификатор: ' + str(user.pk) + '\n' + 'Телефон: ' + user.phone_number +
                     '\n' + 'Рабочий телефон: ' + user.phone_number_work + '\n' + 'e-mail: ' + user.email_address +
                     '\n' + 'Организация: ' + user.user_organization.organization_name + '\n' + 'Должность: ' +
                     user.job_title + '\n' + 'Описание: ' + '\n' + user.description)
            if user.user_photo:
                bot.send_photo(message.chat.id, user.user_photo, reply_markup=markup)
            bot.send_message(message.chat.id, reply, reply_markup=markup)

    else:
        for user in users:
            reply = ('ФИО: ' + user.full_name + '\n' + 'Телефон: ' + user.phone_number + '\n' + 'Рабочий телефон: ' +
                     user.phone_number_work + '\n' + 'e-mail: ' +
                     'Ник в телеграмм: ' + user.nick_name + '\n' + user.email_address + '\n' + 'Организация: ' +
                     user.user_organization.organization_name + '\n' + 'Должность: ' + user.job_title +
                     '\n' + 'Описание: ' + '\n' + user.description)
            if user.user_photo:
                bot.send_photo(message.chat.id, user.user_photo, reply_markup=markup)
            bot.send_message(message.chat.id, reply, reply_markup=markup)


def exclude_replicas(query_sets):
    for i in range(len(query_sets)):

        for user in query_sets[i]:

            for j in range(len(query_sets)):

                if i == j:
                    continue

                else:
                    query_sets[j] = query_sets[j].exclude(pk=user.pk)

    return query_sets


def search(message):
    msg = message.text.split(' ')

    users_phone = TgUser.objects.filter(phone_number__icontains=msg[0])
    users_full_name = TgUser.objects.filter(full_name__icontains=msg[0])
    users_job_title = TgUser.objects.filter(job_title__icontains=msg[0])
    users_description = TgUser.objects.filter(description__icontains=msg[0])
    users_tg_ids = TgUser.objects.filter(tg_id__icontains=msg[0])
    users_emails = TgUser.objects.filter(email_address__icontains=msg[0])
    users_organization_name = TgUser.objects.filter(user_organization__organization_name__icontains=msg[0])

    if len(msg) > 1:
        for i in range(1, len(msg)):
            users_phone = users_phone.filter(phone_number__icontains=msg[i])
            users_full_name = users_full_name.filter(full_name__icontains=msg[i])
            users_job_title = users_job_title.filter(job_title__icontains=msg[i])
            users_description = users_description.filter(description__icontains=msg[i])
            users_tg_ids = users_tg_ids.filter(tg_id__icontains=msg[i])
            users_emails = users_emails.filter(email_address__icontains=msg[i])
            users_organization_name = users_organization_name.filter(
                user_organization__organization_name__icontains=msg[0])

    query_sets = [users_phone, users_full_name, users_job_title, users_description,
                  users_tg_ids, users_emails, users_organization_name]

    query_sets = exclude_replicas(query_sets)

    users_phone = query_sets[0]
    users_full_name = query_sets[1]
    users_job_title = query_sets[2]
    users_description = query_sets[3]
    users_tg_ids = query_sets[4]
    users_emails = query_sets[5]
    users_organization_name = query_sets[6]

    flag = True

    if len(users_phone) != 0:
        bot.send_message(message.chat.id, 'Найдено по номеру телефона:', reply_markup=markup)
        search_report(message, users_phone)
        flag = False

    if len(users_full_name) != 0:
        bot.send_message(message.chat.id, 'Найдено по ФИО:', reply_markup=markup)
        search_report(message, users_full_name)
        flag = False

    if len(users_job_title) != 0:
        bot.send_message(message.chat.id, 'Найдено по должности:', reply_markup=markup)
        search_report(message, users_job_title)
        flag = False

    if len(users_description) != 0:
        bot.send_message(message.chat.id, 'Найдено по описанию:', reply_markup=markup)
        search_report(message, users_description)
        flag = False

    if len(users_emails) != 0:
        bot.send_message(message.chat.id, 'Найдено по e-mail:', reply_markup=markup)
        search_report(message, users_emails)
        flag = False

    if len(users_organization_name) != 0:
        bot.send_message(message.chat.id, 'Найдено по организации', reply_markup=markup)
        search_report(message, users_organization_name)
        flag = False

    if len(users_tg_ids) != 0:
        bot.send_message(message.chat.id, 'Найдено по tg id:', reply_markup=markup)
        search_report(message, users_tg_ids)
        flag = False

    if flag:
        bot.send_message(message.chat.id, 'Ничего не найдено', reply_markup=markup)


def user_db_save(message, user):
    try:
        user.save()

    except Exception as ex:
        logging.warning(ex)
        bot.send_message(message.chat.id, 'Произошла ошибка, обратитесь к администратору', reply_markup=markup)

    else:
        bot.send_message(message.chat.id, 'Данные успешно добавлены', reply_markup=markup)


from tgbot.management.commands import change_user_handlers
from tgbot.management.commands.add_user_handlers import start_add_user_full_name
from tgbot.management.commands.delete_user_handlers import start_delete
