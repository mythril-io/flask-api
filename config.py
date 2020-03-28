import os

DEBUG = False
MAX_USER_AVATAR_SIZE = 3145728
MAX_USER_BANNER_SIZE = 6291456

# Flask SQLAlchemy
SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Flask Praetorian 
SECRET_KEY = os.getenv('PRAETORIAN_SECRET_KEY')
PRAETORIAN_CONFIRMATION_SENDER = os.getenv('PRAETORIAN_CONFIRMATION_SENDER')
PRAETORIAN_CONFIRMATION_URI = os.getenv('PRAETORIAN_CONFIRMATION_URI')
PRAETORIAN_CONFIRMATION_SUBJECT = 'Mythril.io - Please confirm your e-mail'
PRAETORIAN_CONFIRMATION_TEMPLATE = 'templates/email_validation.html'

# Flask Mail
MAIL_SERVER = os.getenv('MAIL_SERVER')
MAIL_PORT = os.getenv('MAIL_PORT')
MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')