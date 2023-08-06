from .bot import *

logging.basicConfig(level=logging.INFO, filename="tgbot/management/logs/bot_delete.log",
                    format="%(asctime)s %(levelname)s %(message)s")


def start_delete(message):

    try:
        user = TgUser.objects.get(pk=message.text)

    except Exception as ex:
        logging.info(ex)
        bot.send_message(message.chat.id, 'Пользователь не найден', reply_markup=markup)

    else:

        if str(user.tg_id) != message.chat.id:

            search_report(message, [user])

            delete_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            yes = types.KeyboardButton('Да')
            no = types.KeyboardButton('Нет')
            delete_markup.add(yes, no)

            bot.send_message(message.chat.id, 'Вы уверены, что хотите безвозвратно удалить пользователя?',
                             reply_markup=delete_markup)
            bot.register_next_step_handler(message, delete_validation, user)

        else:
            bot.send_message(message.chat.id, 'Вы не можете удалить себя', reply_markup=markup)


def delete_validation(message, user):
    if message.text == 'Да':

        try:
            user.delete()

        except Exception as ex:
            logging.warning(ex)
            bot.send_message(message.chat.id, 'Что-то пошло не так, обратитесь к администратору', reply_markup=markup)

        else:
            bot.send_message(message.chat.id, 'Пользователь удален', reply_markup=markup)

    else:
        bot.send_message(message.chat.id, 'Выберите что вам надо', reply_markup=markup)
