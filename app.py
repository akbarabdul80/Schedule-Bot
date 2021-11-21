import logging
# System libraries
import os

# Scheduler
from time import sleep
import schedule

# Telegram
import telegram
from telegram.ext import Updater, Filters, MessageHandler, CommandHandler, ConversationHandler, CallbackContext

import firebase_admin
from firebase_admin import credentials

from schedules import schedule as sc

# Conf
from conf import conf_bot, conf_db

PORT = int(os.environ.get('PORT', 80))
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def get_access(id_chat, access) -> bool:
    # 0 -> admin
    # 1 -> admin & Group
    # 2 -> all

    if access == 0:
        return id_chat in conf_bot.id_chat_admin
    if access == 1:
        return id_chat in conf_bot.id_chat_group or id_chat in conf_bot.id_chat_admin
    if access == 2:
        return True
    return False


def report(update, context: CallbackContext, access: str):
    update.message.reply_text("Maaf bos tidak boleh akses kesini, silahkan lewat group!")
    tmp_message = "⚠️ <b>Lapor BOSS!!</b> ⚠️\n\n"
    tmp_message += f"💀 Ada yang coba akses ke function {access}!!\n\n"
    tmp_message += "😎 " + "Username : " + str(update.message.from_user.username) + "\n"
    tmp_message += "🆔 " + "User ID : " + str(update.message.chat_id) + "\n"
    for id_chat in conf_bot.id_chat_admin:
        context.bot.send_message(chat_id=id_chat, text=tmp_message, parse_mode=telegram.ParseMode.HTML)


def schedule_checker():
    while True:
        schedule.run_pending()
        sleep(1)


def cancel(update):
    update.message.reply_text('canceled')

    # end of conversation
    return ConversationHandler.END


def never_sleep(context: CallbackContext):
    count_job = len(context.job.job_queue.jobs())

    context.bot.send_message(chat_id=-776645059,
                             text='Never Sleep, Schedule Count = ' + str(count_job))

    if count_job == 1:
        sc.remove_update_schedule(context)


def main():
    # Fetch the service account key JSON file contents
    cred = credentials.Certificate(conf_db.CRED_FIREBAE)
    # Initialize the app with a service account, granting admin privileges
    firebase_admin.initialize_app(cred, {
        'databaseURL': conf_db.DATABASE_URL
    })

    updater = Updater(conf_bot.TOKEN, request_kwargs={'read_timeout': 20, 'connect_timeout': 20}, use_context=True)
    dip = updater.dispatcher

    # Never Sleep Heroku
    job = updater.job_queue
    job.run_repeating(never_sleep, interval=240, first=120)

    # Schedule
    dip.add_handler(CommandHandler('schedule', sc.get_schedule))
    dip.add_handler(CommandHandler('schedule_today', sc.get_schedule_today))
    dip.add_handler(CommandHandler('update_schedule', sc.update_schedule, pass_job_queue=True))
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('add_schedule', sc.insert_schedule)],

        states={
            sc.SCHEDULE: [MessageHandler(Filters.text, sc.schedule_text)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dip.add_handler(conv_handler)

    if os.environ["DEBUG"] == 'true':
        # Start the Bot Heroku
        updater.start_webhook(listen="0.0.0.0",
                              port=PORT,
                              url_path=conf_bot.TOKEN,
                              webhook_url='https://ugmbot.herokuapp.com/' + conf_bot.TOKEN)
    else:
        # Start the Bot Local
        updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
