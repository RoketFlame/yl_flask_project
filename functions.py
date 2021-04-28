import datetime
import json


def make_creation_date():
    cur_time = datetime.datetime.now()
    dt = cur_time.strftime('%H:%M %d/%m/%y')
    return dt


def get_fps(vid_c=None, cpu=None, ram=None, game=None, **kwargs):
    with open('static/computer.json') as cat_file:
        data = json.load(cat_file)
        video_p = data["video_cards"][vid_c]["points"]
        cpu_p = data["cpus"][cpu]["points"]
        ram_p = data["ram"][ram]["points"]
        coef = data["games"][game]["coef"]
        fps = (video_p + cpu_p + ram_p) // coef
        return fps
