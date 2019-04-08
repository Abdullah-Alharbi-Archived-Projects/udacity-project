from flask import Flask
from flask_login import LoginManager
from sqlalchemy import create_engine
import json
# when using * import these variables
__all__ = ['app', 'config', 'engine', 'login_manager']

# create instance of flask
app = Flask(__name__)
# create engine
engine = create_engine(
    "sqlite:///itemcatalog.db?check_same_thread=False", encoding='utf8')
# flask login setup
# about LoginManager class:
# https://flask-login.readthedocs.io/en/latest/#flask_login.LoginManager
login_manager = LoginManager(app)
# customizing the login process:
# https://flask-login.readthedocs.io/en/latest/#customizing-the-login-process
login_manager.login_view = "signIn"
login_manager.login_message_category = "info"
# read the config.json
config = json.loads(open("config.json", "r").read())
# set the secret key
app.config["SECRET_KEY"] = config["secret_key"]
