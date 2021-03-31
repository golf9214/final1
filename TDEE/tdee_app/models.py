from tdee_app import db, login_manager
from datetime import datetime
from flask_login import UserMixin
# graphql
import graphene
from graphene.types import Scalar
from graphql.language import ast
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    start_date = db.Column(db.Date, nullable=False, default=datetime.today().date())
    start_weight = db.Column(db.Float, nullable=False, default=0)

    daily_stats = db.relationship('DailyStats', backref='name', lazy=True)

    def __repr__(self):
        return f'User("{self.username}","{self.start_date}")'

class DailyStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    calories = db.Column(db.Integer())
    weight = db.Column(db.Float())
    date = db.Column(db.Date, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    days = db.Column(db.Integer(), nullable=False, default=0)
    
    def __repr__(self):
        return f'DailyStats("{self.calories}", "{self.weight}, "{self.days}", {self.date}")'

class UserObject(SQLAlchemyObjectType):
   class Meta:
       model = User
       interfaces = (graphene.relay.Node, )

class DailyStatsObject(SQLAlchemyObjectType):
    class Meta:
        model = DailyStats
        interfaces = (graphene.relay.Node, )
# GRAPHQL stuff
class Query(graphene.ObjectType):
    node = graphene.relay.Node.Field()
    all_stats = SQLAlchemyConnectionField(DailyStatsObject)
    all_users = SQLAlchemyConnectionField(UserObject)
    
schema = graphene.Schema(query=Query)

class Date(Scalar):
    @staticmethod
    def serialize(dt):
        return dt.isoformat()
    @staticmethod
    def parse_literal(node):
        if isinstance(node, ast.StringValue):
            return datetime.strptime(node.value, "%Y-%m-%d")
    @staticmethod
    def parse_value(value):
        return datetime.strptime(value, "%Y-%m-%d")


class InsertStats(graphene.Mutation):
    class Arguments:
        calories = graphene.Int(required=True)
        weight = graphene.Float(required=True) 
        date = Date(required=True)
        username = graphene.String(required=True)
    data = graphene.Field(lambda: DailyStatsObject)
    def mutate(self, info, calories, weight, username, date):
        user = User.query.filter_by(username=username).first()
        stats = DailyStats(calories=calories, weight=weight, date=date)
        if user is not None:
            DailyStats.name = user
        db.session.add(stats)
        db.session.commit()
        return InsertStats(stats=stats)

class Mutation(graphene.ObjectType):
    insert_stats = InsertStats.Field()
    
schema = graphene.Schema(query=Query, mutation=Mutation)