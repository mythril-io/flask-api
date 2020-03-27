from flask import Flask
from extensions import db, migrate, guard, cors, mail, ma
from models import User
# from logging.config import fileConfig

# Import API
from api.v1 import blueprint as api_v1

# Initialize the flask instance and configs
app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
# fileConfig('logging.cfg')
# logging.basicConfig(filename='storage/logs/app.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

# Initialize extensions
db.init_app(app)
migrate.init_app(app, db)
guard.init_app(app, User)
cors.init_app(app)
ma.init_app(app)
if app.config.get('MAIL_SERVER'):
    mail.init_app(app)

# Register blueprints
app.register_blueprint(api_v1)