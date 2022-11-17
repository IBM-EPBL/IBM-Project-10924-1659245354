import ibm_db, ibm_db_sa, ibm_db_alembic
import os
from flask import Flask
from flask_db2 import DB2
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail, Message

app = Flask(__name__)

app.config['SECRET_KEY'] = '587480e285a7584cd755f6d6247ceb77'
app.config['SQLALCHEMY_DATABASE_URI'] = 'ibm_db_sa://pnh87629:XgilJxEPyFW9XgAk@824dfd4d-99de-440d-9991-629c01b3832d.bs2io90l08kqb1od8lcg.databases.appdomain.cloud:30119/BLUDB;security=SSL;'

app.config['MAIL_SERVER'] = 'smtp.sendgrid.net'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'apikey'
app.config['MAIL_PASSWORD'] = ''
app.config['MAIL_DEFAULT_SENDER'] = ''

mail = Mail(app)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


from crr import routes