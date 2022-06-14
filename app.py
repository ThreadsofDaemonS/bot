#!/usr/bin/python
# _*_ coding: utf-8 _*_


from flask import Flask, url_for, redirect, request, abort, session ,g
from flask_sqlalchemy import SQLAlchemy


from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from flask_admin.form import SecureForm
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_security import Security, SQLAlchemyUserDatastore, current_user
from flask_admin.contrib.fileadmin import FileAdmin

import os.path as op


from flask_admin import helpers as admin_helpers

from config import ProductionConfig

import datetime as d

from flask_babelex import Babel
from flask_debugtoolbar import DebugToolbarExtension


app = Flask(__name__)
app.config.from_object(ProductionConfig)

babel = Babel(app)
toolbar = DebugToolbarExtension(app)

@babel.localeselector
def get_locale():
    # if a user is logged in, use the locale from the user settings
    user = getattr(g, 'user', None)
    if user is not None:
        return user.locale
    if request.args.get('lang'):
        session['lang'] = request.args.get('lang')
    else:
        return session.get('lang', 'uk')
    return request.accept_languages.best_match(['uk', 'ru', 'de', 'fr', 'en'])

@babel.timezoneselector
def get_timezone():
    user = getattr(g, 'user', None)
    if user is not None:
        return user.timezone

db = SQLAlchemy(app)
db.init_app(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)


from models import User, Role, Workers, Departments, Bot_info, Status, Reports,Fines, FAQ
admin = Admin(app, name='Панель керування', base_template='my_master.html', template_mode='bootstrap3')

class ParentModelView(ModelView):
    form_base_class = SecureForm     # CSRF Protection
    can_view_details = True
    create_modal = True
    can_export = True
    column_exclude_list = ['created', 'updated']


    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('superuser'):
            self.can_create = True
            self.can_edit = True
            self.can_delete = True
            return True

        elif current_user.has_role('user'):
            self.can_create = False
            self.can_edit = False
            self.can_delete = False
            self.can_view_details = False
            return True

        return False

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))


class RoleUsersModelView(ParentModelView):
    column_default_sort = 'created'
    column_labels = {'created': 'Створено', 'updated': 'Останнє оновлення'}
    column_exclude_list = ['password', 'last_login_at', 'current_login_at', 'last_login_ip',
                           'current_login_ip', 'login_count']

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('superuser'):
            self.can_create = True
            self.can_edit = True
            self.can_delete = True
            return True

        elif current_user.has_role('user'):
            return False

        return False

class User_ModelView(RoleUsersModelView):
    column_searchable_list = ['fullname', 'email']
    column_filters = ['fullname', 'email']
    column_editable_list = ['fullname', 'email']

class Bot_ModelView(RoleUsersModelView):
    column_labels = {'workers': 'Співробітник'}
    column_searchable_list = ['username', 'first_name', 'last_name']
    column_filters = ['username', 'first_name', 'last_name', 'chat_id', 'workers']
    column_editable_list = ['username', 'first_name', 'last_name', 'chat_id']


class WorkersModelView(ParentModelView):
    column_labels = {'fullname': 'ПІБ', 'status': 'Посада', 'phone_number': 'Номер телефону',
                     'authorized_in_bot': 'Авторизован', 'departments': 'Відділ',
                     'created': 'Створено', 'updated': 'Останнє оновлення'}

    column_searchable_list = ['fullname', 'phone_number']
    column_filters = ['fullname', 'phone_number']
    column_editable_list = ['fullname', 'phone_number']


class ReportsModelView(ParentModelView):
    column_labels = {'report': 'Звіт', 'users': 'Співробітник', 'created': 'Створено', 'updated': 'Останнє оновлення'}
    column_searchable_list = ['report', 'workers.fullname']
    column_filters = ['workers.fullname']
    column_editable_list = ['report']
    column_default_sort = 'created'


    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('superuser'):
            self.can_create = True
            self.can_edit = True
            self.can_delete = True
            return True

        elif current_user.has_role('user'):
            self.can_edit = True
            self.can_delete = True
            return True

        return False

class FinesModelView(ParentModelView):
    column_labels = {'fine': 'Штраф', 'users': 'Співробітник', 'created': 'Створено', 'updated': 'Останнє оновлення'}
    column_searchable_list = ['fine', 'workers.fullname']
    column_filters = ['workers.fullname']
    column_editable_list = ['fine']
    column_default_sort = 'created'

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('superuser'):
            self.can_create = True
            self.can_edit = True
            self.can_delete = True
            return True

        elif current_user.has_role('user'):
            self.can_create = True
            self.can_edit = True
            return True

        return False

class InfoModelView(ParentModelView):
    column_labels = {'question': 'Питання', 'answer': 'Відповідь', 'created': 'Створено', 'updated': 'Останнє оновлення'}

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('superuser'):
            self.can_create = True
            self.can_edit = True
            self.can_delete = True
            return True

        elif current_user.has_role('user'):
            self.can_create = True
            self.can_edit = True
            self.can_delete = True
            return True

        return False


class DepartmentsModelView(ParentModelView):
    column_labels = {'created': 'Створено', 'updated': 'Останнє оновлення', 'department': 'Відділ',
                     'fullname': 'Співробітники', 'amount_of_workers': 'кількість робітників', 'description': 'Опис'}
    column_searchable_list = ['department', 'department_code']
    column_filters = ['department', 'department_code']
    column_editable_list = ['department', 'department_code', 'description']

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('superuser'):
            self.can_create = True
            self.can_edit = True
            self.can_delete = True
            return True

        elif current_user.has_role('user'):
            self.can_edit = True
            return True

        return False

class StatusModelView(ParentModelView):
    column_labels = {'status': ' Посада', 'salary': 'Зарплатня', 'vacation': 'Відпустка', 'fine_count': 'Штрафні бали',
                     'created': 'Створено', 'updated': 'Останнє оновлення'}
    column_searchable_list = ['status', 'salary_tot', 'vacation']
    column_filters = ['status', 'salary_tot', 'vacation']
    column_editable_list = ['status', 'salary_tot', 'vacation']

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('superuser'):
            self.can_create = True
            self.can_edit = True
            self.can_delete = True
            return True

        elif current_user.has_role('user'):
            self.can_create = True
            self.can_edit = True
            self.can_delete = True
            return True

        return False


path = op.join(op.dirname(__file__), 'Reports')
admin.add_view(FileAdmin(path, '/Reports/', name='Reports', category='Admin'))

admin.add_view(RoleUsersModelView(Role, db.session, category='Admin'))
admin.add_view(User_ModelView(User, db.session, category='Admin'))
admin.add_view(Bot_ModelView(Bot_info, db.session, category='Admin'))
admin.add_view(WorkersModelView(Workers, db.session, name='Співробітники', category='Спіробітники'))
admin.add_view(StatusModelView(Status, db.session, name='Посада', category='Керування'))
admin.add_view(ReportsModelView(Reports, db.session, name='Звіти', category='Спіробітники'))
admin.add_view(FinesModelView(Fines, db.session, name='Штрафи', category='Спіробітники'))
admin.add_view(DepartmentsModelView(Departments, db.session, name='Відділення', category='Керування'))
admin.add_view(InfoModelView(FAQ, db.session, name='Питання', category='Керування'))


user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
        get_url=url_for
    )

# test for all system
from flask_security.utils import hash_password
db.drop_all()
db.create_all()
with app.app_context():
    date = d.datetime.now().date() - d.timedelta(days=5)
    user_role = Role(name='user')
    super_user_role = Role(name='superuser')
    db.session.add(user_role)
    db.session.add(super_user_role)
    department = Departments(department='ІТ', amount_of_workers=+1)
    db.session.add(department)
    s = Status(status='Адмін', salary_tot=20000)
    w = Workers(fullname='Ф І О', phone_number='yourphonenumber', created=date, status=s,
                salary=s.salary_tot, departments=department)
    b = Bot_info(chat_id=332291910, username='@RazDua', first_name='1', last_name='2', workers=w)
    db.session.add(b)
    db.session.add(w)
    db.session.add(s)

    # for i in range(20):
    #     db.session.add(Workers(fullname='Ф І О', status='Адмін', salary=20000,
    #             phone_number='+phonenumber'+str(i), chat_id=332291910+i, username='@RazDua'+str(i), first_name='1'+str(i), last_name='2'+str(i),
    #             created=date))

    test_admin = user_datastore.create_user(
        fullname='Admin',
        email='admin',
        password=hash_password('admin'),
        roles=[super_user_role]
    )
    test_user = user_datastore.create_user(
        fullname='test',
        email='test',  # test@example.com
        password=hash_password('test'),
        roles=[user_role]
    )
    db.session.commit()





