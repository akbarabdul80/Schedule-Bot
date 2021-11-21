import datetime
from dataclasses import dataclass


@dataclass
class DataSchedule:
    title: str
    time_start: datetime.time
    time_end: datetime.time
    day: int
    link: str = "Kosong"


@dataclass
class DataHomework:
    title: str
    assignment: datetime.datetime
    collect: str = "Kosong"
