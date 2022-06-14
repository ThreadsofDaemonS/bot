#!/usr/bin/python
# _*_ coding: utf-8 _*_


from flask import url_for, redirect
import datetime as d
from models import Workers, Bot_info, Reports, Fines, FAQ, Status
from config import ProductionConfig
import telebot
from telebot import types
from app import app, db, request
from keyboard import Keyboard
import logging
from flask_security.decorators import login_required

logging.basicConfig(filename="logs/bot.log", level=logging.DEBUG)

bot = telebot.TeleBot(ProductionConfig.TOKEN)
keyboard = Keyboard(bot)
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)


T = d.time(18, 0, 0)
contactus = """
Ласкаво просимо!
Привіт, вас вітає компанія "Організація"!
Яка займається, щоб ви подумали - правильно - організацією!

Ось наші контакти:
Call-center: 383-383-383
Наш сайт: www.OOO_Organizaciya.com
"""

@bot.message_handler(commands=["start"])
def start(msg):
    bot.send_message(msg.chat.id, 'Роботу з ботом розпочато! Для більш детальної інформації про бота оберіть /about')
    bot.send_message(msg.chat.id, 'Оберіть /verification для авторизації')

@bot.message_handler(commands=["about"])
def about(msg):
    bot.send_message(msg.chat.id, contactus)

@bot.message_handler(commands=["verification"])
def acitvate(msg):
    butn = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    butn.add(types.KeyboardButton(text="Авторизуватися", request_contact=True))
    bot.send_message(msg.chat.id, 'Відправте номер телефону', reply_markup=butn)

@bot.message_handler(content_types=['contact'])
def verification(msg):
    fu = msg.from_user
    logging.info("Someone try to authorize: %s" % msg)
    with app.app_context():
        bot_in = Bot_info.query.filter_by(chat_id=fu.id).first()
        user = Workers.query.filter_by(id=bot_in.workers.id).first()
        id = bot_in.chat_id
        pn = user.phone_number
        fn = user.fullname
        if msg.contact.user_id == fu.id and id == fu.id and (pn == msg.contact.phone_number or msg.contact.phone_number == '+%s' % pn):
            bot.send_message(msg.chat.id, 'Авторизацію пройдено \nЛаскаво просимо, %s ' % fn,
                             reply_markup=types.ReplyKeyboardRemove(True))
            bot.send_message(msg.chat.id, "Оберіть пункт:", reply_markup=keyboard.menu())
            bot_in.authorized_in_bot = True
            db.session.add(bot_in)
            db.session.commit()
        elif pn != msg.contact.phone_number or msg.contact.phone_number == '+%s' % pn:
            logging.info("Someone failed authorize: %s" % msg)
            bot_in.authorized_in_bot = False
            db.session.add(bot_in)
            db.session.commit()

@bot.callback_query_handler(func=lambda call: call.message.from_user.id == ProductionConfig.BOT_CHAT_ID and \
                                              Bot_info.query.filter_by(chat_id=call.message.chat.id).first().authorized_in_bot) # id бота
def callback_menu(call):
    with app.app_context():
        bot_in = Bot_info.query.filter_by(chat_id=call.message.chat.id).first()
        user = Workers.query.filter_by(id=bot_in.workers.id).first()
        reprt = Reports.query.filter(Reports.user_id == user.id).order_by(Reports.created).all() # detalized select (до какого-то и числа и т.д.)
        fines = Fines.query.filter(Fines.user_id == user.id).order_by(Fines.created).all() # detalized select
        stat = Status.query.filter_by(id=user.status.id).first()   # here
        faq = FAQ.query.all()
        if call.message:
            if call.data == 'report_menu':
                bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              reply_markup=keyboard.report_menu())
            elif call.data == 'report':
                # учесть дни недели + система оповещения + ориентация по департаменту - создать кортеж или из базы что-то + клава + Excel или вообще под всех сразу
                DATE = [(user.created + d.timedelta(day)).date() for day in
                        range(((d.datetime.now() - user.created).days))]
                R = [r.created.date() for r in reprt]
                for date in DATE:
                    if date not in R:
                        score = 24
                        fine = 'Штраф: %d балли - запізнення зі звітом за %s' % (
                        score, date.strftime("%d.%m.%Y"))
                        f = Fines(fine=fine, created=date)
                        user.fine_count += score    # here
                        user.salary -= user.fine_count
                        user.fine.append(f)
                        db.session.add(user)
                        db.session.commit()
                        to_report = 'Спочатку наберіть звіт за %s:' % date.strftime("%d.%m.%Y")
                        bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
                        bot.send_message(call.message.chat.id, text=to_report)
                        bot.register_next_step_handler(call.message, report)
                        break
                else:
                    if reprt[-1].created.date() != d.datetime.now().date():
                        if d.datetime.now().time() > T:
                            score = d.datetime.now().hour - T.hour
                            fine = 'Штраф: %d баллів - запізнення зі звітом на %d год.' % (score, score)
                            f = Fines(fine=fine)
                            user.fine_count += score # here
                            user.salary -= user.fine_count
                            user.fine.append(f)
                            db.session.add(user)
                            db.session.commit()
                        bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
                        bot.send_message(call.message.chat.id, 'Наберіть ваш звіт:')
                        bot.register_next_step_handler(call.message, report)
                    else:
                        bot.send_message(call.message.chat.id, 'Ви вже за сьогодні відправили звіт')
                        bot.send_message(call.message.chat.id, "Меню", reply_markup=keyboard.menu())

            elif call.data == 'edit_report':
                if user.report:
                    if reprt[-1].created.date() == d.datetime.now().date():
                        bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
                        bot.send_message(call.message.chat.id, 'Ось що ви відправили:\n%s\n\nНапишіть тут що має бути:' \
                                         % reprt[-1].report)
                        bot.register_next_step_handler(call.message, edit_report)
                    else:
                        bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
                        bot.send_message(call.message.chat.id, 'Редагувати можна тільки звіт за сьогодні')
                        bot.send_message(call.message.chat.id, "Оберіть пункт:", reply_markup=keyboard.report_menu())
                else:
                    bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
                    bot.send_message(call.message.chat.id, 'У вас немає звітів.')
                    bot.send_message(call.message.chat.id, "Оберіть пункт:", reply_markup=keyboard.report_menu())

            elif call.data == 'menu':
                bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              reply_markup=keyboard.menu())

            elif call.data == 'fines':
                msg_text = ''
                for fine in fines[:-21:-1]:
                    msg_text += fine.fine + '\n'
                bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
                bot.send_message(call.message.chat.id, text=msg_text)
                bot.send_message(call.message.chat.id, "Оберіть пункт:", reply_markup=keyboard.menu())

            elif call.data == 'profile':
                vac = 0 # here
                if stat.vacation:
                    vac = (stat.vacation - d.datetime.now()).days
                text = 'Співробітник: %s\nПосада: %s\nДата початку роботи: %s\nПроробив в компанії: %s\nЗалишок відпустки: %s\nЗарплатня:%s' \
                       % (user.fullname, stat.status, user.created.date().strftime("%d.%m.%Y"), # here
                          (d.datetime.now() - user.created).days, vac, user.salary)
                bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
                bot.send_message(call.message.chat.id, text=text)
                bot.send_message(call.message.chat.id, "Оберіть пункт:", reply_markup=keyboard.menu())

            elif call.data == 'questions': # here
                markup = types.InlineKeyboardMarkup(row_width=1)
                for q in faq:
                    markup.add(types.InlineKeyboardButton(text=q.question, callback_data=q.question))
                Back = types.InlineKeyboardButton(text="Назад", callback_data="menu")
                markup.add(Back)
                bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              reply_markup=markup)

            elif call.data in [e.question for e in faq]:  # here
                for a in faq:
                    if call.data == a.question:
                        bot.send_message(call.message.chat.id, text=a.answer)
                        bot.send_message(call.message.chat.id, "Оберіть пункт:", reply_markup=keyboard.menu())


def report(msg):
    with app.app_context():
        if msg.content_type == 'text': # как записывать отчеты в бд
            # here  # Departments
            # user = Workers.query.filter_by(chat_id=msg.chat.id).first()
            bot_in = Bot_info.query.filter_by(chat_id=msg.chat.id).first()
            user = Workers.query.filter_by(id=bot_in.workers.id).first()
            DATE = d.datetime.now()
            try:
                temp_date = [(user.created.date() + d.timedelta(day)) for day in range(((d.datetime.now() - user.created).days))]
                R = [r.created.date() for r in user.report]
                for date in temp_date:
                    if date not in R:
                        DATE = date
                        break
            except Exception as e:
                logging.exception("Trouble with: %s" % e)
            r = Reports(report=msg.text, created=DATE) # в залежності від відділу написати клавіатуру
            user.report.append(r)
            db.session.add(user)
            db.session.commit()
            bot.send_message(msg.chat.id, "Оберіть пункт:", reply_markup=keyboard.report_menu())
        else:
            bot.send_message(msg.chat.id, "Введіть будь-ласка текст!")
            bot.register_next_step_handler(msg, report)

def edit_report(msg):
    with app.app_context():
        if msg.content_type == 'text':
            # user = Workers.query.filter_by(chat_id=msg.chat.id).first()
            bot_in = Bot_info.query.filter_by(chat_id=msg.chat.id).first()
            user = Workers.query.filter_by(id=bot_in.workers.id).first()
            reprt = Reports.query.filter(Reports.user_id == user.id).order_by(Reports.created).all()
            reprt[-1].report = msg.text
            db.session.add(user)
            db.session.commit()
            bot.send_message(msg.chat.id, "Меню", reply_markup=keyboard.report_menu())
        else:
            bot.send_message(msg.chat.id, "Введіть будь-ласка текст!")
            bot.register_next_step_handler(msg, edit_report())


@bot.message_handler(commands=["menu"])
@bot.message_handler(func=lambda msg: Bot_info.query.filter_by(chat_id=msg.chat.id).first().authorized_in_bot)
def menu_r(msg):
    bot.send_message(msg.chat.id, "Оберіть пункт:", reply_markup=keyboard.menu())



@app.route("/{}".format(ProductionConfig.TOKEN), methods=['POST'])
def getMessage():
    new_updates = [types.Update.de_json(request.data.decode("utf-8"))]
    bot.process_new_updates(new_updates)
    return "ok", 200

@app.route("/")
@login_required
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url="{}/{}".format(ProductionConfig.URL, ProductionConfig.TOKEN))
    return redirect(url_for('admin.index'))

