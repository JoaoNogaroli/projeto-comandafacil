from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import psycopg2
from flask_login import LoginManager

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']='postgresql://hwupyrkewttgtt:4c5959e5ee4bd36583edc1423678ba0e3901cd71f13bb140b0bbbb038d117067@ec2-54-164-22-242.compute-1.amazonaws.com:5432/d5in86mutije91'

app.config['SECRET_KEY'] = 'llllllkkokoko'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

login_manager = LoginManager(app)
db = SQLAlchemy(app)

