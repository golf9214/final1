from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField, DecimalField, DateField
from wtforms.validators import NumberRange, DataRequired, ValidationError
from tdee_app.models import DailyStats
from flask_login import current_user

class NewData(FlaskForm):
    calories = IntegerField('Calories Eaten Today', validators=[NumberRange(min=1000)])
    weight = DecimalField('Weight in LB', places=1, validators=[NumberRange(min=100, max=500)])
    submit = SubmitField('Submit Data')

class AddData(FlaskForm):
    date = DateField('Date: y-m-d', format='%Y-%m-%d', validators=[DataRequired()])
    calories = IntegerField('Calories Eaten', validators=[NumberRange(min=1000)])
    weight = DecimalField('Weight in LB', places=1, validators=[NumberRange(min=100, max=500)])
    submit = SubmitField('Submit Data')
    def validate_date(self, date):
        date = DailyStats.query.filter_by(user_id=current_user.id, date=date.data).first()
        if date:
            raise ValidationError('Data For Date Already Exists!')