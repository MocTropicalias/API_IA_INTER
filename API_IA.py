from flask import Flask, request, jsonify
import pickle
import pandas as pd
import os
from flask_cors import CORS
import psycopg as pg

banco = "postgres://avnadmin:AVNS_69W0O2_65jEqbsCuztW@pg-11d01e0e-testepgsql.e.aivencloud.com:24931/dbBaseIA?sslmode=require"
app = Flask(__name__)
CORS(app)

@app.route('/api/process', methods=['POST'])
def process_json():
    # Receber o JSON enviado na requisição
    data = request.get_json()

    # Validar se o JSON está no formato esperado
    required_keys = [
        "Qual é seu genero?",
        "Qual é a sua idade?",
        "Qual é a média da sua renda familiar mensal?",
        "Qual estado você mora?",
        "Você usa muitos eletrônicos durante o dia? (6h ou mais)",
        "Qual grau de educação você tem?",
        "Você pratica esportes? (pelo menos 3 vezes na semana)",
        "Você frequenta muito espaços públicos? (parques, museus e etc)"
    ]
    for key in required_keys:
        if key not in data:
            return jsonify({"error": f"Campo obrigatório ausente: {key}"}), 400
        
    query = "insert into tb_base(var_genero, int_idade, var_renda, var_estado, var_eletronicos, var_educacao, var_esportes, var_locais_publicos, var_result) values('"+data["Qual é seu genero?"]+"',"+str(data["Qual é a sua idade?"])+",'"+data["Qual é a média da sua renda familiar mensal?"]+"','"+data["Qual estado você mora?"]+"','"+data["Você usa muitos eletrônicos durante o dia? (6h ou mais)"]+"','"+data["Qual grau de educação você tem?"]+"','"+data["Você pratica esportes? (pelo menos 3 vezes na semana)"]+"','"+data["Você frequenta muito espaços públicos? (parques, museus e etc)"]+"','"

    caminho_arq_tratamento = os.path.dirname(__file__)+"/pkls/tratamento_dados.pkl"

    caminho_arq_modelo = os.path.dirname(__file__)+"/pkls/modelo.pkl"

    with open(caminho_arq_tratamento, 'rb') as f:
        tratamento_dados = pickle.load(f)

    with open(caminho_arq_modelo, 'rb') as f:
        modelo = pickle.load(f)
    
    dados = [data.copy()]
    
    dados = pd.DataFrame(dados,columns=required_keys)

    x = pd.DataFrame(tratamento_dados.transform(dados),columns=tratamento_dados.get_feature_names_out())

    previsao = modelo.predict(x)
    query = query + str(previsao)+"')"
    try:
        conn = pg.connect(banco)
        cur = conn.cursor()
        cur.execute(query)
        conn.commit()
    except (pg.Error) as error:
        print("Erro banco: ", error)
    except (Exception) as error:
        print("Erro código python")
    finally:
        if conn:
            cur.close()
            conn.close()
        print("Conexões encerradas\n\n")
        if previsao == 1:
            return jsonify({"result": True})
        else:
            return jsonify({"result": False})

def run_python_code(data):
    return True

if __name__ == '__main__':
    app.run(debug=True, port=5000, host="0.0.0.0")
