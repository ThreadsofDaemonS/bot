#!/usr/bin/python3
# _*_ coding: utf-8 _*_

class Config(object):
    URL = 'https://408b7544.ngrok.io'
    TOKEN = '479461558:AAE-W_lYVMyzV1mH9lD08SlsiG6qJq-450I'       # '461457277:AAGfE6ZdQgAxtNm4CHcs2co75ENpz9j-a2c'
    BOT_CHAT_ID = 479461558    # 461457277
    TESTING = False
    DEBUG = False
    BABEL_DEFAULT_LOCALE = 'uk'
    ENV = 'Production'
    # DATABASE_FILE = 'db.sqlite'
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///%s' % DATABASE_FILE
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:V$@localhost/db"
    SECRET_KEY = 'secret_key'

    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_ECHO = False

    # Flask-Security config
    SECURITY_URL_PREFIX = "/admin"
    SECURITY_PASSWORD_HASH = "bcrypt"
    SECURITY_PASSWORD_SALT = "A"

    # Flask-Security URLs, overridden because they don't put a / at the end
    SECURITY_LOGIN_URL = "/login/"
    SECURITY_LOGOUT_URL = "/logout/"
    # SECURITY_REGISTER_URL = "/register/"

    SECURITY_POST_LOGIN_VIEW = "/admin/"
    SECURITY_POST_LOGOUT_VIEW = "/admin/"
    # SECURITY_POST_REGISTER_VIEW = "/admin/"


    # Flask-Security features
    # SECURITY_CONFIRMABLE = True # для проверки почты при регистрации
    SECURITY_TRACKABLE = True
    SECURITY_REGISTERABLE = False
    SECURITY_SEND_REGISTER_EMAIL = False

    # Flask-debug-toolbar
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    # RECAPTCHA_USE_SSL = False
    # RECAPTCHA_PUBLIC_KEY = '6LeYIbsSAAAAACRPIllxA7wvXjIE411PfdB2gt2J'
    # RECAPTCHA_PRIVATE_KEY = '6LeYIbsSAAAAAJezaIq3Ft_hSTo0YtyeFG-JgRtu'
    # RECAPTCHA_OPTIONS = {'theme': 'white'}


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    ENV = 'Production'
    # LOGFILE = 'logs/Production.log'

class DevelopConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True
    ENV ='development'
    # LOGFILE = 'logs/Development.log'

class TestingConfig(Config):
    TESTING = True


