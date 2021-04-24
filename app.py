from inicializacao import app, db
from flask import Flask, request, render_template, url_for
import os
from classe_modelo import Users, Restaurante
from sqlalchemy import or_
import psycopg2
from flask_login import login_user, logout_user
import itertools
import pandas as pd

port = int(os.environ.get('PORT', 5000))

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/cadastro" ,methods=['POST'])
def cadastro():
    nome = request.form['nome']
    email = request.form['email']
    senha = request.form['senha']
    if nome and email and senha:
        try:
            user = Users(nome, email, senha)
            db.session.add(user)
            db.session.commit()
            return 'Cadastrado com sucesso'
        except Exception as e:
            print(e)
            return 'Error ao cadastrar, email já cadastrado.'

@app.route("/logar_restaurante")
@app.route("/logar")    
@app.route("/error")
def error():
    return render_template('error_page.html')


@app.route("/logar", methods=['POST'])
def logar():
    email = request.form['email']
    senha = request.form['senha']
    try:

        user = Users.query.filter_by(email=email).first()
    except Exception as e:
        return render_template('error_page.html')

    if not user or not user.verify_password(senha):
        return render_template('error_page.html')
    try:
        login_user(user)
        tabela_restaurante = db.Table('restaurante', db.metadata)
        restaurantes = []
        restaurantes = [r[1] for r in db.session.query(tabela_restaurante).all()]
        lista = ['Cliente','Produto','Quantidade','Preço/Un']
        #print(restaurantes)
        return render_template('cliente_logado.html', restaurantes=restaurantes, lista=lista)

    except Exception as e:
        return render_template('error_page.html')

@app.route("/cadastro_restaurante", methods=['POST'])
def cadastro_restaurante():
    nome_res = request.form['nome_res']
    email_res = request.form['email_res']
    senha_res = request.form['senha_res']
    if nome_res and email_res and senha_res:
        try:
            restaurante = Restaurante(nome_res, email_res, senha_res)
            db.session.add(restaurante)
            db.session.commit()
            return 'Cadastrado com sucesso'
        except Exception as e:
            print(e)
            return 'Error ao cadastrar, email já cadastrado.'
    return 'ok'

@app.route("/logar_restaurante", methods=['POST'])
def logar_restaurante():
    email_res = request.form['email_res']
    senha_res = request.form['senha_res']
    try:

        restaurante = Restaurante.query.filter_by(email_res=email_res).first()
    except Exception as e:
        return render_template('error_page.html')

    if not restaurante or not restaurante.verify_password(senha_res):
        return render_template('error_page.html')
    try:
        login_user(restaurante)
        return render_template('restaurante_logado.html')

    except Exception as e:
        return render_template('error_page.html')

def grouper(n, iterable, fillvalue=None):
    "grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return itertools.zip_longest(fillvalue=fillvalue, *args)

@app.route("/iniciar_comanda", methods=['POST'])
def iniciar_comanda():
    valor_a_resgatar = request.form['valor_a_resgatar']
    valor_a_resgatar_alterado = valor_a_resgatar.split(',')
    valores_finais = []
    for i in range(1, len(valor_a_resgatar_alterado)):
       valores_finais.append(valor_a_resgatar_alterado[i])

    #print(valores_finais)
    lista_pegar = ['Cliente','Produto','Quantidade','Preço/Un']
    tamanho_total = int(len(valores_finais))
    tamanho_dividido = int(len(valores_finais)/len(lista_pegar))
    
    #print("Tamanho total das linhas: ", tamanho_total)
    #print("Quantas linhas por colunas: ", tamanho_dividido)
 
    
    novo = list(grouper(int(tamanho_dividido), valores_finais))

    #print(novo)
    res = dict(zip(lista_pegar, novo))
    #print(res)

    #PEGAR COLUNAS
    try:
        results = []
        items= []
        for colum in res.keys():
            results.append(colum) 

        for row in res:
            items.append(res[row])


    except Exception as e:
        print(e)
    #TRANSFORMOU EM DATAFRAME FINAL
    new = pd.DataFrame.from_dict(res)
    print(new)
    linhas = new.shape[0]
    print(new.shape[0])
    return render_template('comanda.html', results=results, items=items, linhas=linhas, len=len)

if __name__  == '__main__':
    app.run(debug=True, port=port)