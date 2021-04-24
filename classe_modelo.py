from sqlalchemy import String, Column, Integer, Float
from inicializacao import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def get_user(id):
    return Users.query.filter_by(id=id).first()




class Users(db.Model, UserMixin):
    __tablename__ = 'users'
    id = Column('id', Integer, primary_key=True)
    nome = Column('nome', String(255), nullable=False)
    email = Column('email', String(255), nullable=False, unique =True)
    senha = Column('senha', String(255), nullable=False)

    def __init__(self, nome, email, senha):
        self.nome = nome
        self.email = email
        self.senha = generate_password_hash(senha)

    def verify_password(self, pwd):
        return check_password_hash(self.senha, pwd)

class Restaurante(db.Model, UserMixin):
    __tablename__ = 'restaurante'
    id = Column('id', Integer, primary_key=True)
    nome_res = Column('nome', String(255), nullable=False)
    email_res = Column('email', String(255), nullable=False, unique =True)
    senha_res = Column('senha', String(255), nullable=False)

    def __init__(self, nome_res, email_res, senha_res):
        self.nome_res = nome_res
        self.email_res = email_res
        self.senha_res = generate_password_hash(senha_res)

    def verify_password(self, pwd):
        return check_password_hash(self.senha_res, pwd)
