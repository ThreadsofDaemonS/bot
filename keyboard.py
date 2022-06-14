#!/usr/bin/python3
# _*_ coding: utf-8 _*_



from telebot import types


class Keyboard:
    def __init__(self, bot):
        self.bot = bot

    def menu(self):
        markup =  types.InlineKeyboardMarkup(row_width=2)
        Report = types.InlineKeyboardButton(text="Звіт", callback_data="report_menu")
        Fines = types.InlineKeyboardButton(text="Штрафи", callback_data="fines")
        Questions = types.InlineKeyboardButton(text="Питання", callback_data="questions")
        Data = types.InlineKeyboardButton(text="Профіль", callback_data="profile")
        markup.add(Report, Fines, Questions, Data)
        return markup

    def report_menu(self):
        markup = types.InlineKeyboardMarkup(row_width=2)
        Back = types.InlineKeyboardButton(text="Назад", callback_data="menu")
        Report = types.InlineKeyboardButton(text="Скласти звіт", callback_data="report")
        Edit_report = types.InlineKeyboardButton(text="Редагувати звіт", callback_data="edit_report")
        markup.add(Edit_report, Report, Back)
        return markup

# menu для продажников + кнопки назад и отправить, возможно взаимодействие с документом (напримере EXCEL)

    # def questions(self):  # here
    #     markup = types.InlineKeyboardMarkup(row_width=2)
    #     Back = types.InlineKeyboardButton(text="Назад", callback_data="menu")
    #     Allquestion = types.InlineKeyboardButton(text="Загальні питання", callback_data="allquestions")
    #     Salary = types.InlineKeyboardButton(text="Питання по зарплатні", callback_data="salary")
    #     markup.add(Allquestion, Salary, Back)
    #     return markup