from firebase_admin import db
import model.data_db as model

import conf.conf_db as conf


def drop_table(db_name):
    ref = db.reference(db_name)
    return ref.delete()


def insert_schedule(data: model.DataHomework):
    ref = db.reference(conf.TABLE_HOMEWORK)
    # print(str(time_start))
    ref.push({
        'title': data.title,
        'datetime_assignment': str(data.assignment),
        'collect': data.collect
    })


def delete_schedule(id_homework):
    ref = db.reference(conf.TABLE_HOMEWORK + "/" + id_homework)
    return ref.delete()


def get_schedule():
    ref = db.reference(conf.TABLE_HOMEWORK)
    return ref.get()


def get_schedule_id(id_homework):
    ref = db.reference(conf.TABLE_HOMEWORK)
    return ref.get()[id_homework]


def get_schedule_day(day):
    ref = db.reference(conf.TABLE_HOMEWORK)
    return ref.order_by_child('day').equal_to(day).get()
