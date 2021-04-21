import datetime


def make_creation_date():
    cur_time = datetime.datetime.now()
    dt = cur_time.strftime('%H:%M %d/%m/%y')
    return dt
