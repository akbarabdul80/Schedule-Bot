from datetime import timedelta, datetime as dt
import datetime

# Telegram
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler
import telegram
import pytz
from data import db_schedule as db
import app
from conf import conf_bot
import data.model.data_db as model

days = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
num_days = [0, 1, 2, 3, 4, 5, 6]
emoji_day = ["😭", "😫", "😣", "😟", "☺️", "🤩", "🥰"]

LINE = "\n--------------------------------------------------------------------------\n"
SCHEDULE = range(1)


def daily_job(update, context):
    for id_chat in conf_bot.id_chat_admin:
        context.bot.send_message(chat_id=id_chat, text='Setting a daily notifications!')
        time = datetime.time(hour=9, minute=49, tzinfo=pytz.timezone('asia/jakarta'))
        context.job_queue.run_daily(notify_assignees, time, context=update.message.chat_id)


def notify_assignees(context: CallbackContext):
    for id_chat in conf_bot.id_chat_admin:
        exec_time = (dt.now() + timedelta(hours=7)).strftime("%H:%M:%S")
        context.bot.send_message(chat_id=id_chat, text="Some text!" + exec_time)


def update_schedule(update, context: CallbackContext):
    if app.get_access(update.message.chat_id, 1):
        for id_chat in conf_bot.id_chat_admin:
            context.bot.send_message(chat_id=id_chat, text='🥰 Setting a schedules daily notifications!')
            update.message.reply_text('🥰 Setting a schedules daily notifications!')

        remove_update_schedule(context)

        # time = dt(year=2021, month=10, day=30, hour=16, minute=50, second=0, tzinfo=pytz.timezone('Asia/Jakarta'))
        # dtm = datetime.datetime(year=2021, month=11, day=2, hour=18, minute=55)
        # tzinfo = pytz.timezone('asia/jakarta')
        # aware_time = tzinfo.localize(dtm)
        # context.job_queue.run_once(notify_schedule, aware_time, context=update.message.chat_id,
        #                            name=str(1))
    else:
        app.report(update, context, "update_schedule")


def remove_update_schedule(context: CallbackContext):
    for job in context.job_queue.jobs():
        if job.name != "never_sleep":
            print("Jadwal ", job.name, job.next_t)
            job.schedule_removal()

    data = db.get_schedule()
    for row in data:
        hour = int(str(data[row]["time_start"]).split(":")[0])
        minute = int(str(data[row]["time_start"]).split(":")[1])
        day = int(data[row]["day"])
        if minute - conf_bot.REMAINDER_TIME >= 0:
            minute -= conf_bot.REMAINDER_TIME
        else:
            hour -= 1
            minute = minute - conf_bot.REMAINDER_TIME + 60
            if hour == -1:
                hour = 23
                day -= 1
                if day < 0:
                    day = 6

        if hour - 7 < 0:
            day = day - 1
        time = datetime.time(hour=hour, minute=minute, tzinfo=pytz.timezone('asia/jakarta'))
        context.job_queue.run_daily(notify_schedule, time, days=(day,), context=context,
                                    name=str(row))


def notify_schedule(context: CallbackContext):
    row = db.get_schedule_id(context.job.name)
    tmp_jadwal = "⚠️ <b>Ada Jadwal MATKUL Guys!!</b> ⚠️\n\n"
    tmp_jadwal += "⚡ " + row["title"] + " - (" + row["time_start"] + " - " + row["time_end"] + ")\n"
    tmp_jadwal += "🔗 " + row["link"] + "\n\n"
    tmp_jadwal += "➡️ " + "Kelas selanjutnya : " + context.job.next_t.strftime("%d %b %Y %H:%M") + "\n\n"
    tmp_jadwal += "Jangan lupa berdo'a agar tidak ditunjuk untuk menjawab pertanyaan yang kita tidap paham" + "☺️"

    for id_chat in conf_bot.id_chat_group:
        context.bot.send_message(chat_id=id_chat, text=tmp_jadwal, parse_mode=telegram.ParseMode.HTML)


def insert_schedule(update: Update, context: CallbackContext):
    if app.get_access(update.message.chat_id, 1):
        update.message.reply_text(
            '<b>📝 Menambah Jadwal Kuliah 📝</b>\n\n'
            'Format : title_time.start_time.end_day_link\n\n'
            '<b>Parameters</b> : \n'
            '<b>title</b> : str\n'
            '<b>time.start</b> : datetime.time()\n'
            '<b>time.end</b> : datetime.time()\n'
            '<b>day</b> : int [0 -> Senin, 1 -> Selasa, dst]\n'
            '<b>link</b> : str\n\n'
            'e.g : Praktikum WEB_12:15_1_https://meet.google.com/ric-jwgv-dtj?pli=1&authuser=0\n\n'
            'Untuk membatalkan dapat menggunakan command /cancel \n\n',
            parse_mode=telegram.ParseMode.HTML
        )

        update.message.reply_text(
            'title_time.start_time.end_day_link',
            parse_mode=telegram.ParseMode.HTML
        )

    else:
        app.report(update, context, "update_schedule")

    return SCHEDULE


def schedule_text(update: Update, context: CallbackContext):
    if app.get_access(update.message.chat_id, 1):
        message = update.message.text.split("_")

        # title_19:00:00_1_link
        if message[0] == "/cancel":
            app.cancel(update)
        elif len(message) != 5:
            update.message.reply_text("Pastikan format anda benar")
            update.message.reply_text("Format : title_time.start_time.end_day_link")
        else:
            title = message[0]
            time_start = message[1]
            time_end = message[2]
            day = message[3]
            link = message[4]

            format_time = "%H:%M"
            try:
                time_start = datetime.datetime.strptime(time_start, format_time).time()
                time_end = datetime.datetime.strptime(time_end, format_time).time()
                day = int(day)
                db.insert_schedule(model.DataSchedule(title, time_start, time_end, day, link))
                update.message.reply_text(
                    "✅" + " Berhasil menambahkan jadwal\n\n" +
                    "🧑‍💻" + " <b>Title</b> : " + title + "\n" +
                    "🕐" + " <b>Time</b> : " + str(time_start) + " - " + str(time_end) + "\n" +
                    "⚡" + " <b>Day</b> : " + days[day] + "\n" +
                    "🔗" + " <b>Link</b> : " + link + "\n",
                    "🚀" + " <b>Pengingat a</b> : " + link + "\n",
                    telegram.ParseMode.HTML
                )
            except ValueError:
                update.message.reply_text("Pastikan format anda benar")
                update.message.reply_text("Format : title_time.start_time.end_day_link")
    else:
        app.report(update, context, "schedule_text")
    return ConversationHandler.END


def get_schedule(update, context: CallbackContext):
    tmp_message = "<b>⚡ Jadwal Kuliah ⚡</b>\n\n"

    for day in num_days:
        tmp_jadwal = ""
        data = db.get_schedule_day(day)

        # data_now = ()
        # for key, value in data.items():
        #     print(value)
        #     data_now += value
        #
        # print(sorted(data_now, key=lambda x: dt.strptime(x[0], '%H:%M')))
        for row in data:
            tmp_jadwal += "⚡ " + data[row]["title"] + " - (" + data[row]["time_start"] + " - " + data[row][
                "time_end"] + ")\n"
            tmp_jadwal += "🔗 " + data[row]["link"] + "\n\n"

        if tmp_jadwal != "":
            tmp_message += "<b>" + emoji_day[day] + " " + days[day].upper() + "</b>\n\n" + tmp_jadwal + LINE + "\n"

    update.message.reply_text(
        tmp_message,
        telegram.ParseMode.HTML
    )

    # for id_chat in conf.id_chat_admin:
    #     context.bot.send_document(chat_id=id_chat, document=open("../my_database.db", 'rb'), caption="Backup")


def get_schedule_today(update, context: CallbackContext):
    tmp_message = "<b>⚡ Jadwal Kuliah ⚡</b>\n\n"

    tmp_jadwal = ""

    day = datetime.datetime.now(pytz.timezone(conf_bot.TIME_ZONE)).weekday()
    data = db.get_schedule_day(day)

    for row in data:
        tmp_jadwal += "⚡ " + data[row]["title"] + " - (" + data[row]["time_start"] + " - " + data[row][
            "time_end"] + ")\n"
        tmp_jadwal += "🔗 " + data[row]["link"] + "\n\n"

    if tmp_jadwal != "":
        tmp_message += "<b>" + emoji_day[day] + " " + days[day].upper() + "</b>\n\n" + tmp_jadwal + LINE + "\n"

    update.message.reply_text(
        tmp_message,
        telegram.ParseMode.HTML
    )
