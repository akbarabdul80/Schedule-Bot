from firebase_admin import db
import conf.conf_db as conf
import data.model.data_db as model


def drop_table(db_name):
    ref = db.reference(db_name)
    return ref.delete()


def insert_schedule(data: model.DataSchedule):
    ref = db.reference(conf.TABLE_SCHEDULE)
    # print(str(time_start))
    ref.push({
        'title': data.title,
        'time_start': str(data.time_start),
        'time_end': str(data.time_end),
        'day': data.day,
        'link': data.link
    })


def delete_schedule(id_schedule):
    ref = db.reference(conf.TABLE_SCHEDULE + "/" + id_schedule)
    return ref.delete()


def get_schedule():
    ref = db.reference(conf.TABLE_SCHEDULE)
    return ref.get()


def get_schedule_id(id_schedule):
    ref = db.reference(conf.TABLE_SCHEDULE)
    return ref.get()[id_schedule]


def get_schedule_day(day):
    ref = db.reference(conf.TABLE_SCHEDULE)
    return ref.order_by_child('day').equal_to(day).get()
