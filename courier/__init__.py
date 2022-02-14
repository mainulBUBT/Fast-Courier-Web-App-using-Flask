from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)



###########################################
############## DATABASE SETUP #############
###########################################

app.config['SECRET_KEY'] = 'Helloguys'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/test2'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['UPLOAD_FOLDER'] = 'static/profile_pics/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

db = SQLAlchemy(app)
Migrate(app,db)

###########################################


###########################################
############## LOGIN CONFIGS #############
###########################################

login_manager = LoginManager()

login_manager.init_app(app)
login_manager.login_view = 'merchant.merchant_login'

###########################################

from courier.core.views import core
from courier.merchants.views import merchant
from courier.admin.views import admin

app.register_blueprint(merchant)
app.register_blueprint(core)
app.register_blueprint(admin)