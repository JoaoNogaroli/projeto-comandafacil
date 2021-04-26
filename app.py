from inicializacao import app, db
from flask import Flask, request, render_template, url_for, session, json,jsonify

import os
from classe_modelo import Users, Restaurante, Produto
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
    #print(valor_a_resgatar)
    valor_a_resgatar_alterado = valor_a_resgatar.split(',')
    valores_finais = []
    for i in range(1, len(valor_a_resgatar_alterado)):
       valores_finais.append(valor_a_resgatar_alterado[i])

    #print(valores_finais)
    lista_pegar = ['Cliente','Quantidade','Preço/Un','Produto']
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
    #print(new.shape[0])
    session['new'] = new.to_json()

    return render_template('comanda.html', results=results, items=items, linhas=linhas, len=len)

@app.route("/teste", methods=['POST'])
def teste():
    new = session['new']
    #print(new)
    novo_df = pd.read_json(new)
    #print(novo_df.dtypes)
    #print(novo_df)
    #print(novo_df.shape)
    

    #print('-------')
    #print(novo_df)
    novo_df['Quantidade'] = novo_df['Quantidade'].astype(float)
    novo_df['Preço/Un'] = novo_df['Preço/Un'].astype(float)
    novo_df['SomaValores'] = novo_df['Quantidade'] * novo_df['Preço/Un']

    contatotal = novo_df['SomaValores'].sum()
    

    contatotal_mais_dez = (contatotal*1.1)
    contatotal_mais_dez = ("{:.2f}".format(contatotal_mais_dez))
    #print(novo_df)
    contatotal = ("{:.2f}".format(contatotal))

    
    #print('-------')
    #print(novo_df.dtypes)
    #print('-------')
    #print('R$: ',contatotal)
    #print('-------')
    #print('Como os 10% '+'R$: '+ str(contatotal_mais_dez))

    #-------- Parte dos valores totais terminada
    valores_de_cada_um = novo_df.groupby(by=["Cliente"])['SomaValores'].sum()

    #print(valores_de_cada_um)
    #print('-------')
    #print(valores_de_cada_um.to_json(orient='split'))
    valores_de_cada_um = valores_de_cada_um.to_json(orient='split')
    #print(valores_de_cada_um)
    #print('2 -------')
    resp = json.loads(valores_de_cada_um)
    lista_clientes= resp['index']
    #print(lista_clientes)
    #print('3 -------')
    lista_clientes_conta= resp['data']

    exatos_dez_por_cliente = []
    for item in lista_clientes_conta:
        exatos_dez_por_cliente.append("{:.2f}".format(item*1.1))
    #print(lista_clientes_conta)
    lista_final = list(zip(lista_clientes,lista_clientes_conta,exatos_dez_por_cliente))
    #print(lista_final)

    #--------- Parte dos valores de cada um termianda
    dez_por_cento =  float(contatotal_mais_dez)-float(contatotal)
    dez_por_cento_sem_format = dez_por_cento
    dez_por_cento = ("{:.2f}".format(dez_por_cento))

    #print(dez_por_cento)
    #--------- Parte do valor dos 10% termianda

    quantidade_de_clientes = float(len(lista_clientes))
    valor_dez_por_cliente = dez_por_cento_sem_format/quantidade_de_clientes
    valor_dez_por_cliente = ("{:.2f}".format(valor_dez_por_cliente))


    #print(valor_dez_por_cliente)
    #--------- Parte dos 10% de cada cliente terminada

    #--------- Error DEscoberto- --- Cada cliente paga seus 10%
    

   
    # ---- TENTANDO JUNTAR 2 listas
    

    return {'contatotal':contatotal, 'contatotal_mais_dez':contatotal_mais_dez, 'lista_final':lista_final,'dez_por_cento':dez_por_cento, 'valor_dez_por_cliente':valor_dez_por_cliente,'exatos_dez_por_cliente':exatos_dez_por_cliente}

@app.route('/cadastrar_produto', methods=['POST'])
def cadastrar_produto():
    nome_restaurante = request.form['nomeres']

    session['nome_restaurante'] = nome_restaurante

    nome_produto = request.form['produto']
    valor_produto = request.form['valor']
    
    if nome_restaurante and valor_produto and valor_produto:
        try:
            item_final = Produto(nome_restaurante, nome_produto, valor_produto)
            db.session.add(item_final)
            db.session.commit()
            return 'Cadastrado com sucesso'
        except Exception as e:
            print(e)
            return 'Error ao cadastrar, produto já cadastrado.'

@app.route('/pegar_produtos', methods=['POST']) 
def pegar_produtos():
    nome_restaurante = request.form['nome_restaurante']
    print(nome_restaurante)
    
    tabela_produtos = db.Table('produtos', db.metadata)
    produtos = []
    produtos = [r[2] for r in db.session.query(tabela_produtos).filter_by(nome_restaurante=nome_restaurante).all()]

    print(type(produtos))
    print('-------')
   
    print(produtos)

    return {'produtos':produtos}

@app.route('/pegar_preco', methods=['POST'])
def pegar_preco():
    nome_restaurante = request.form['nome_restaurante']

    tabela_produtos = db.Table('produtos', db.metadata)

    produtos = []
    produtos = [r[2] for r in db.session.query(tabela_produtos).filter_by(nome_restaurante=nome_restaurante).all()]

    precos = []
    precos = [r[3] for r in db.session.query(tabela_produtos).filter_by(nome_restaurante=nome_restaurante).all()]
    
    print(produtos)
    print(precos)

    preco_produto = dict(zip(produtos,precos))

    print(preco_produto)


    return preco_produto

if __name__  == '__main__':
    app.run(debug=True, port=port)