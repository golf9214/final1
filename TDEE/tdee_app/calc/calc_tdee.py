# cannot import models
from tdee_app.models import DailyStats
from flask_login import current_user
from collections import namedtuple


cal_conver = 3500
Data =  namedtuple('Data', ['calories', 'weight'])

def list_past_week(day):
    ' takes in day and returns list of data for past 7 days if applicable'
    d = Data([],[])
   
    if day - 6 >= 0:
        for i in range(day - 6, day + 1):
            stats = DailyStats.query.filter_by(days=i, user_id=current_user.id).first()
            if stats:
                d.calories.append(stats.calories)
                d.weight.append(stats.weight)
    else:
        for i in range(day + 1):
            stats = DailyStats.query.filter_by(days=i, user_id=current_user.id).first()
            if stats:
                d.calories.append(stats.calories)
                d.weight.append(stats.weight)
    return d

def list_past_month(day):
    d = Data([],[])
    if day - 30 >= 0:
        for i in range(day - 30, day + 1):
            stats = DailyStats.query.filter_by(days=i, user_id=current_user.id).first()
            if stats:
                d.calories.append(stats.calories)
                d.weight.append(stats.weight)
    else:
        for i in range(day):
            stats = DailyStats.query.filter_by(days=i, user_id=current_user.id).first()
            if stats:
                d.calories.append(stats.calories)
                d.weight.append(stats.weight)
    return d

def tdee_week(data):
    ' returns weekly tdee given calories and weight throughout a week '
    if len(data.weight) > 1:
        delta = data.weight[-1] - data.weight[0]
    else:
        delta = 0
    tdee = (sum(data.calories)/7) - ((delta * cal_conver) / 7)
    return tdee

def tdee_month(data):
    if len(data.weight) > 1:
        delta = data.weight[-1] - data.weight[0]
    else:
        delta = 0
    tdee = (sum(data.calories)/len(data.calories)) - ((delta * cal_conver) / len(data.weight))
    return tdee

def this_day_week_tdee(day):
    Data = list_past_week(day)
    return str(tdee_week(Data))

def this_day_month_tdee(day):
    Data = list_past_week(day)
    return str(tdee_month(Data))

