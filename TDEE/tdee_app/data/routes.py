from flask import Blueprint, render_template, url_for, flash, redirect, request
from tdee_app.models import DailyStats, schema
from tdee_app import db
from tdee_app.data.forms import NewData, AddData
from flask_login import current_user, login_required
from flask_graphql import GraphQLView
from datetime import datetime
from collections import namedtuple

data = Blueprint('data', __name__)
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
def get_average_weight_last_week(day):
    d = []
    for i in range(day):
        stats = DailyStats.query.filter_by(days=i-7, user_id=current_user.id).first()
        if stats:
            d.append(stats.weight)
    return sum(d)/len(d)

def tdee_week(d, day):
    ' returns weekly tdee given calories and weight throughout a week '
    if len(d.weight) > 1:
        delta =  get_average_weight_last_week(day) - (sum(d.weight)/len(d.weight))
    else:
        return 0
    tdee = (sum(d.calories)/len(d.calories)) - ((delta * 500 * (day % 7) / len(d.calories)))
    return round(tdee)

def tdee_month(d):
    if len(d.weight) > 1:
        delta = d.weight[-1] - d.weight[0]
    else:
        return 0
    tdee = (sum(d.calories)/len(d.calories)) - ((delta * cal_conver) / len(d.weight))
    return round(tdee)

def this_day_week_tdee(day):
    d = list_past_week(day)
    return str(tdee_week(d, day))

def this_day_month_tdee(day):
    d = list_past_month(day)
    return str(tdee_month(d))
##################################################################################################################
labels = [
    'JAN', 'FEB', 'MAR', 'APR',
    'MAY', 'JUN', 'JUL', 'AUG',
    'SEP', 'OCT', 'NOV', 'DEC'
]


values = []

colors = [
    "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
    "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
    "#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]

@data.route('/graphs', methods=["GET", "POST"])
@login_required
def graphs():
    data = DailyStats.query\
        .filter_by(user_id=current_user.id)\
        .order_by(DailyStats.date.desc()).all()
    for d in data:
        values.append(d.weight)
    line_labels=labels
    line_values=values
    return render_template('graphs.html', title='Graphs', max=17000, labels=line_labels, values=line_values)
##################################################################################################################
@data.route('/stats', methods=["GET", "POST"])
@login_required
def stats():
    data = DailyStats.query\
        .filter_by(user_id=current_user.id)\
        .order_by(DailyStats.date.desc()).all()
    if DailyStats.query.filter_by(date=datetime.today().date(), user_id=current_user.id).first():
        add_text = "Update Today's Data"
    else:
        add_text = 'Add Data'
    return render_template('stats.html', title='Stats', datas=data, text=add_text, calc_month=this_day_month_tdee, calc_week=this_day_week_tdee)


# add data to current date
@data.route('/new', methods=["GET", "POST"])
@login_required
def new():
    form = NewData()
    if form.validate_on_submit():
        stats = DailyStats(calories=form.calories.data, weight=form.weight.data, name=current_user, date=datetime.today().date(), days=(datetime.today().date()-current_user.start_date).days)
        # check if data already exists for current day
        if DailyStats.query.filter_by(date=datetime.today().date(), user_id=current_user.id).first():
            remove_stats = DailyStats.query.filter_by(date=datetime.today().date(), user_id=current_user.id).first()
            db.session.delete(remove_stats)
            flash('Data Updated', 'success')
        else:
            flash('Data Added', 'success')
        db.session.add(stats)
        db.session.commit()
        return redirect(url_for('main.home'))
    elif request.method == 'GET':
        if DailyStats.query.filter_by(date=datetime.today().date(), user_id=current_user.id).first():
            form.calories.data = DailyStats.query\
                .filter_by(date=datetime.today().date(), user_id=current_user.id)\
                .first().calories
            form.weight.data = DailyStats.query\
                .filter_by(date=datetime.today().date(), user_id=current_user.id)\
                .first().weight
            return render_template('new.html', title='New', form=form, text='Update')
    return render_template('new.html', title='New', form=form, text='Add')

# add data to past days
@data.route('/add', methods=["GET", "POST"])
@login_required
def add_data():
    form = AddData()
    if form.validate_on_submit():
        # date_conver = datetime.strptime(form.date.data, '%Y-%m-%d')
        stats = DailyStats(calories=form.calories.data, weight=form.weight.data, name=current_user, date=form.date.data, days=(form.date.data-current_user.start_date).days)
        # removes the previous stats for day if data for day already exists
        # patched out
        if DailyStats.query.filter_by(date=form.date.data, user_id=current_user.id).first():
            remove_stats = DailyStats.query.filter_by(date = form.date.data, user_id=current_user.id).first()
            db.session.delete(remove_stats)
            flash('Data Updated', 'success')
        else:
            flash(f'Data Added for day {stats.days}, ', 'success')
        db.session.add(stats)
        db.session.commit()
        return redirect(url_for('data.add_data'))
  
    return render_template('add.html', title='Add Data', form=form, text='Add')

@data.route('/<int:data_id>/delete', methods=['POST'])
@login_required
def delete_data(data_id):
    data = DailyStats.query.get_or_404(data_id)
    if data.name != current_user:
        abort(403)
    db.session.delete(data)
    db.session.commit()
    flash(f'Data for date {data.date} deleted.', 'danger')
    return redirect(url_for('data.stats'))

    
    
# graphql
data.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True # for having the GraphiQL interface
    )
)

