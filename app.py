'''
from flask import Flask

app = Flask(__name__)

@app.route("/ola")
def hello():
    from flask import request, jsonify, render_template
    return "Hello from FastCGI via IIS - Lucas!"
if __name__ == "__main__":
 app.run()

'''



import flask
from flask import Flask
from flask import request, jsonify, render_template,json
import sqlite3
#from flask_sslify import SSLify
import datetime
from datetime import datetime
from datetime import timedelta
import time
import html
import logging
import numpy as np
from sklearn.linear_model import LinearRegression
import pandas as pd


#from flask_cors import CORS
app = flask.Flask(__name__)
#dbpath='/home/nayara/Documentos/api-dados-extraidos-sesdf/'
dbpath='C:/Users/lucas/Desktop/UNB/Mestrado/Projetos/App-Covid-19/api-dados-extraidos-sesdf/'
dbname='dados-extraidos-covid19-sesdf.db'
global db
db=dbpath+dbname
#CORS(app)
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d




@app.route("/apiv2")
def hello():
    return "<h1>Distant Reading Archive</h1><p>A prototype API for distant reading of science fiction novels.</p>"
    #return "<h1>404</h1><p>The resource could not be found.</p>", 404

@app.route('/apiv2/regiao/all', methods=['GET'])
def api_all():
    print("!!!!!!!!")
    conn = sqlite3.connect(db)
    conn.row_factory = dict_factory
    cur = conn.cursor()
    all_data = cur.execute('SELECT * FROM \"dados-extraidos-covid19-sesdf\";').fetchall()
    return jsonify(all_data)
    #return render_template('site.html')



@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


@app.route('/apiv2/regiao/', methods=['GET'])
def api_filtro():
    query_parameters = request.args;
    #cpf = query_parameters.get('cpf')
    dataExtracao = query_parameters.get('dataExtracao')
    if(dataExtracao):
        dataExtracao=html.unescape(dataExtracao)
    print(dataExtracao)
    regiao = query_parameters.get('regiao')
    if(regiao):
        regiao=html.unescape(regiao)
    print(regiao)
    #conta1mt5 = query_parameters.get('conta1mt5')
    #conta2mt5 = query_parameters.get('conta2mt5')
    query = "SELECT * FROM \"dados-extraidos-covid19-sesdf\" WHERE"
    to_filter = []
    #if (cpf):
     #   query += ' cpf=? AND'
     #   to_filter.append(cpf)
    if (dataExtracao):
        query += ' dataExtracao=? AND'
        to_filter.append(dataExtracao)
    if (regiao):
        query += ' regiao=? AND'
        to_filter.append(regiao)
    #if idcompra:
    #    query += ' idcompra=? AND'
    #   to_filter.append(idcompra)
    #if conta1mt5 and (not conta2mt5):
    #    query += ' conta1mt5=? AND'
    #    to_filter.append(conta1mt5)
    #if conta2mt5 and (not conta1mt5):
    #    query += ' conta2mt5=? AND'
    #    to_filter.append(conta2mt5)
    #if not (cpf or email or idcompra or conta1mt5 or conta2mt5):
    #    return page_not_found(404)
    if not (regiao or dataExtracao):
        return page_not_found(404)
    query = query[:-4] + ';'
    conn = sqlite3.connect(db)
    conn.row_factory = dict_factory
    cur = conn.cursor()
    results = cur.execute(query, to_filter).fetchall()
    results=flask.jsonify(results)
    #results.headers.add('Access-Control-Allow-Origin', '*')
    return results




@app.route('/apiv2/regiao/list', methods=['GET'])
def api_list():
    print("!!!!!!!!2")
    conn = sqlite3.connect(db)
    conn.row_factory = dict_factory
    cur = conn.cursor()
    all_data = cur.execute('SELECT regiao,COUNT(DISTINCT regiao) FROM \"dados-extraidos-covid19-sesdf\" GROUP BY regiao;').fetchall()
    return jsonify(all_data)
    #return render_template('site.html')

@app.route('/apiv2/regiao/maxincid', methods=['GET'])
def api_maxinc():
    conn = sqlite3.connect(db)
    conn.row_factory = dict_factory
    cur = conn.cursor()
    max_data = cur.execute('SELECT MAX(incidencia) FROM \"dados-extraidos-covid19-sesdf\";').fetchone()
    max_obit = cur.execute('SELECT MAX(obitos) FROM \"dados-extraidos-covid19-sesdf\";').fetchone()
    maximum = max_data['MAX(incidencia)']
    interval = int(max_data['MAX(incidencia)']/5)
    maxObitos = max_obit['MAX(obitos)']
    intervalObitos = int(max_obit['MAX(obitos)']/5)
    newDic= {
        "num":[interval, 2*interval, 3*interval, 4*interval],
        "obitos":[intervalObitos, 2*intervalObitos, 3*intervalObitos, 4*intervalObitos]}
    return jsonify(newDic)




@app.route('/apiv2/predicao/', methods=['GET'])
def api_predicao():
    query_parameters = request.args;
    regiao = query_parameters.get('regiao')
    if(regiao):
        regiao=html.unescape(regiao)
    print(regiao)
    daysPredict = query_parameters.get('diasPredicao')
    if(daysPredict):
        daysPredict=int(html.unescape(daysPredict))
    print(daysPredict)
    query = "SELECT * FROM \"dados-extraidos-covid19-sesdf\" WHERE"
    to_filter = []
    if (regiao):
        query += ' regiao=? AND'
        to_filter.append(regiao)
    if not (regiao):
        return page_not_found(404)
    query = query[:-4] + ';'
    conn = sqlite3.connect(db)
    conn.row_factory = dict_factory
    cur = conn.cursor()
    results = cur.execute(query, to_filter).fetchall()

    casos=[]
    ln_casos=[]
    datas=[]
    datas_ordinal=[]
    for result,index in zip(results,range(len(results))):
        casos.append(int(result['num']))
        ln_casos.append(np.log(int(result['num'])))
        datas.append(datetime.strptime(str(result['dataExtracao']), '%Y-%m-%d').date())
        datas_ordinal.append(datetime.strptime(str(result['dataExtracao']), '%Y-%m-%d').toordinal())
    #print(*casos,sep="\n")
    #print(*ln_casos,sep="\n")
    #print(*datas,sep="\n")
    datas=sorted(datas)
    datas_ordinal=sorted(datas_ordinal)
    datas_predict_ordinal = []
    datas_predict = []   
    for i in range(daysPredict):
        datas_predict.append((datas[-1]+timedelta(days=i)))
        datas_predict_ordinal.append((datas[-1]+timedelta(days=i)).toordinal())

    
    casos = np.array(casos)
    ln_casos = np.array(ln_casos)
    #datas = np.array(datas)
    datas_ordinal = np.array(datas_ordinal)
    #datas_predict = np.array(datas_predict)
    datas_predict_ordinal = np.array(datas_predict_ordinal)
    
    casos= casos.reshape(-1, 1)
    ln_casos= ln_casos.reshape(-1, 1)
    #datas= datas.reshape(-1, 1)
    datas_ordinal= datas_ordinal.reshape(-1, 1)
    #datas_predict= datas_predict.reshape(-1, 1)
    datas_predict_ordinal= datas_predict_ordinal.reshape(-1, 1)

    
    model = LinearRegression()
    model.fit(datas_ordinal, ln_casos)
    

    ln_casos_predict = model.predict(datas_predict_ordinal)
    #print(*ln_casos_predict,sep="\n")


    casos_predito=[]
    for value in ln_casos_predict:
        casos_predito.append(int(np.exp(value)))

    #print(*casos,sep="\n")
    #print("\n")
    #print(*casos_predito,sep="\n")
    

    array_dict_predict = []
    for i in range(daysPredict-1):
        array_dict_predict.append({})
        array_dict_predict[i]["dataExtracao"]=str(str(datas_predict[i]))
        array_dict_predict[i]["num"]=str(casos_predito[i])

    #response_json
    return flask.jsonify(array_dict_predict)




def add_headers_to_fontawesome_static_files(response):
    """
    Fix for font-awesome files: after Flask static send_file() does its
    thing, but before the response is sent, add an
    Access-Control-Allow-Origin: *
    HTTP header to the response (otherwise browsers complain).
    """
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response





#SSL PRECISA DO pyOpenSSL instalado
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    app.run(host='0.0.0.0', port=5003)
    app.after_request(add_headers_to_fontawesome_static_files)
    #app.run(ssl_context='adhoc')


