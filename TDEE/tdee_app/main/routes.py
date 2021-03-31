from flask import render_template, Blueprint
from tdee_app.models import DailyStats
from flask_login import login_required, current_user
from datetime import datetime
# from tdee_app.calc import calc_tdee
from collections import namedtuple


main = Blueprint('main', __name__)
##########################################################################################################################
cal_conver = 3500
Data =  namedtuple('Data', ['calories', 'weight'])

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

def tdee_month(d):
    if len(d.weight) > 1:
        delta = d.weight[-1] - d.weight[0]
    else:
        return 0
    tdee = (sum(d.calories)/len(d.calories)) - ((delta * cal_conver) / len(d.weight))
    return round(tdee)

def this_day_month_tdee(day):
    d = list_past_month(day)
    return str(tdee_month(d))

#################################################################################################

@main.route('/')
@main.route('/home')
@login_required
def home():
    data = DailyStats.query\
        .filter_by(user_id=current_user.id)\
        .order_by(DailyStats.date.desc()).all()
    if DailyStats.query.filter_by(date=datetime.today().date(), user_id=current_user.id).first():
        add_text = "Update Today's Data"
    else:
        add_text = 'Add Data'
    # gets most recent date
    d = data[0].date
    tdee = this_day_month_tdee((d-current_user.start_date).days)
    days = len(DailyStats.query.filter_by(user_id=current_user.id).all())
    return render_template('home.html', datas=data, text=add_text, tdee=tdee, days=days)

@main.route('/about')
def about():
    return render_template('about.html', title='About')