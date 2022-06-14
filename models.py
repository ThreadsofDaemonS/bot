#!/usr/bin/python
# _*_ coding: utf-8 _*_

from app import db
import datetime as dt
from flask_security import UserMixin, RoleMixin

# перевести в str?
# now = dt.datetime.now(dt.timezone.utc).astimezone() # f
# time_format = "%Y-%m-%d %H:%M:%S"
# now = f"{now:{time_format}}"    # 3.6

class TimestampMixin(object):

    created = db.Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    updated = db.Column(db.DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)


roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)


class Role(db.Model, RoleMixin, TimestampMixin):  # Посада
    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __repr__(self):
        return "Роль: %r" % self.name

class User(db.Model, UserMixin, TimestampMixin):

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    fullname = db.Column(db.String(140))
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean())
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(100))
    current_login_ip = db.Column(db.String(100))
    login_count = db.Column(db.Integer)
    # confirmed_at = db.Column(db.DateTime())

    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

    # Custom User Payload
    def get_security_payload(self):
        return {
            'id': self.id,
            'name': self.fullname,
            'email': self.email
        }

    def __repr__(self):
        return 'Ім\'я: %r, Почта: %r' % (self.fullname, self.email)


class Workers(db.Model, TimestampMixin):

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    fullname = db.Column(db.String(140), nullable=False)
    phone_number = db.Column(db.VARCHAR(20), nullable=False, unique=True)
    fine_count = db.Column(db.Integer, default=0)  # очки штрафу
    salary = db.Column(db.Integer, default=0)  # зарплатня
    # id_card - passport

    departments_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'))

    report = db.relationship('Reports', backref=db.backref('workers', lazy=True))
    fine = db.relationship('Fines', backref=db.backref('workers', lazy=True))

    bot = db.relationship("Bot_info", backref=db.backref('workers', uselist=False))

    def __repr__(self):
        return 'ПІБ: %r' % self.fullname

class Bot_info(db.Model, TimestampMixin):

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    chat_id = db.Column(db.Integer, nullable=False, unique=True)
    authorized_in_bot = db.Column(db.Boolean, nullable=False, default=False)
    username = db.Column(db.String(60), nullable=False, unique=True)
    first_name = db.Column(db.String(60))
    last_name = db.Column(db.String(60))

    workers_id = db.Column(db.Integer, db.ForeignKey('workers.id'))

    def __repr__(self):
        return 'Username: %r' % self.username

class Status(db.Model, TimestampMixin):

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    status = db.Column(db.String(60))
    salary_tot = db.Column(db.Integer, default=0)  # зарплатня
    vacation = db.Column(db.DateTime)  # відпустка в днях(Коли закінчується)

    worker = db.relationship('Workers', backref=db.backref('status', lazy=True))

    def __repr__(self):
        return '%r' % self.status

class Departments(db.Model, TimestampMixin):

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    department = db.Column(db.String(60), nullable=False, unique=True)
    department_code = db.Column(db.Integer, nullable=False, default=0, unique=True)
    description = db.Column(db.String(255))
    amount_of_workers = db.Column(db.Integer)

    workers = db.relationship('Workers', backref=db.backref('departments', lazy=True))

    def __repr__(self):
        return '%r' % self.department

class Reports(db.Model, TimestampMixin):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    report = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('workers.id'), nullable=False, index=True)

    created = db.Column(db.DateTime, nullable=False, default=dt.datetime.utcnow, index=True)


    def __repr__(self):
        return 'Звіт: %r' % self.report

class Fines(db.Model, TimestampMixin):

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    fine = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('workers.id'), nullable=False, index=True)

    created = db.Column(db.DateTime, nullable=False, default=dt.datetime.utcnow, index=True)


    def __repr__(self):
        return 'Штраф: %r' % self.fine

class FAQ(db.Model):

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    question = db.Column(db.String)
    answer = db.Column(db.String)

