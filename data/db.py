import datetime
import sqlite3
from sqlite_utils import Database

TABLE_SCHEDULE = "schedules"


def setup_table_schedule():
    db_conn = Database(r"../my_database.db", recreate=True)
    db_conn[TABLE_SCHEDULE].create({
        "id_schedule": int,
        "title": str,
        "time_start": datetime.time,
        "time_end": datetime.time,
        "day": int,
        "link": str,
    }, pk="id_schedule")


def drop_table(db_name):
    db_conn = Database(r"../my_database.db")
    try:
        db_conn[db_name].drop()
        return True
    except sqlite3.OperationalError:
        return False


def insert_schedule(title: str, time_start: datetime.time, time_end: datetime.time, day: int, link: str):
    db_conn = Database(r"../my_database.db")
    db_conn[TABLE_SCHEDULE].insert(
        {
            "title": title,
            "time_start": time_start,
            "time_end": time_end,
            "day": day,
            "link": link
        }
    )


def delete_schedule(id_schedule: int):
    db_conn = Database(r"../my_database.db")
    try:
        db_conn[TABLE_SCHEDULE].delete(id_schedule)
        return True
    except sqlite3.OperationalError:
        return False


def get_schedule():
    db_conn = Database(r"../my_database.db")
    return db_conn[TABLE_SCHEDULE].rows


def get_schedule_id(id_schedule):
    db_conn = Database(r"../my_database.db")
    return db_conn[TABLE_SCHEDULE].get(id_schedule)


def get_schedule_day(day):
    db_conn = Database(r"../my_database.db")
    return db_conn[TABLE_SCHEDULE].rows_where("day = ?", [day])


drop_table("TABLE_SCHEDULE")
# setup_table_schedule()
# insert_schedule("Test", datetime.time(hour=4, minute=1), 1, "Test")
# insert_schedule("Test", datetime.time(hour=00, minute=32), 1, "Test")
# insert_schedule("Test", datetime.time(hour=00, minute=40), 1, "Test")
# insert_schedule("Test", datetime.time(hour=6, minute=15), 1, "Test")

# for row in get_schedule():
#     print(row)
#
# print((5))
# for row in db_conn["schedules"].rows:
#     print(row)
#     print(dt.strptime(row["time"], "%H:%M:%S").time())
