# _*_ coding: utf-8 _*_



# проверка отчетов + уведомления в телегу о сдаче отчета + уведомление о штрафе

# штрафы в оригинал боте - не забудь

# check and notification


from bot_copy import notification, create_report
import schedule
import time

schedule.every().day.at("11:14").do(create_report)
schedule.every().day.at("11:15").do(notification)

while True:
    schedule.run_pending()
    time.sleep(1)





# def notification():
#     users = Workers.query.all()
#     for user in users:
#         if None in [r.report for r in user.report]:
#             bot.send_message(user.chat_id, 'Здайте будь-ласка звіт!')
#
# def create_report():
#     users = Workers.query.all()
#     for user in users:
#         DATE = [(user.created + d.timedelta(day)).date() for day in range(((d.datetime.now() - user.created).days + 1))]
#         for date in DATE:
#             if date not in [r.created.date() for r in user.report]:
#                 r = Reports(report=None, created=date)
#                 user.report.append(r)
#                 db.session.add(user)
#                 db.session.commit()
#         else:
#             reprt = Reports.query.filter(Reports.user_id == user.id).order_by(Reports.created).all()
#             if reprt[-1].created.date() != d.datetime.now().date():
#                 r = Reports(report=None)
#                 user.report.append(r)
#                 db.session.add(user)
#                 db.session.commit()



