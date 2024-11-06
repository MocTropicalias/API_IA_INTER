from flask import Flask, request, jsonify
import pickle
import pandas as pd
import os
from flask_cors import CORS, cross_origin
import psycopg as pg
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente
load_dotenv()
banco = os.getenv("banco")

# Configurar Flask e CORS
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

@app.route('/api/process', methods=['POST', 'OPTIONS'])
@cross_origin()  # Permitir requisições de qualquer origem
def process_json():
    # Receber o JSON enviado na requisição
    data = request.get_json()

    # Validar se o JSON está no formato esperado
    required_keys = [
        "genero",
        "idade",
        "renda",
        "estado",
        "eletronicos",
        "educacao",
        "esportes",
        "locais_publicos"
    ]
    for key in required_keys:
        if key not in data:
            return jsonify({"error": f"Campo obrigatório ausente: {key}"}), 400

    # Construir a consulta SQL
    query = (
        "INSERT INTO tb_base(var_genero, int_idade, var_renda, var_estado, "
        "var_eletronicos, var_educacao, var_esportes, var_locais_publicos, var_result) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    )

    # Carregar os modelos
    caminho_arq_tratamento = os.path.join(os.path.dirname(__file__), "pkls/tratamento_dados.pkl")
    caminho_arq_modelo = os.path.join(os.path.dirname(__file__), "pkls/modelo.pkl")
    
    with open(caminho_arq_tratamento, 'rb') as f:
        tratamento_dados = pickle.load(f)

    with open(caminho_arq_modelo, 'rb') as f:
        modelo = pickle.load(f)
    
    #declarando colunas
    cols = [
        "Qual é seu genero?",
        "Qual é a sua idade?",
        "Qual é a média da sua renda familiar mensal?",
        "Qual estado você mora?",
        "Você usa muitos eletrônicos durante o dia? (6h ou mais)",
        "Qual grau de educação você tem?",
        "Você pratica esportes? (pelo menos 3 vezes na semana)",
        "Você frequenta muito espaços públicos? (parques, museus e etc)"
    ]
    # Preparar os dados para o modelo
    lista = []
    for i in required_keys:
        lista.append(data[i]) 
    dados = pd.DataFrame([lista], columns=cols)
    x = pd.DataFrame(tratamento_dados.transform(dados), columns=tratamento_dados.get_feature_names_out())
    previsao = modelo.predict(x)[0]
    
    # Adicionar a previsão à consulta SQL
    valores = (
        data["genero"],
        int(data["idade"]),
        data["renda"],
        data["estado"],
        data["eletronicos"],
        data["educacao"],
        data["esportes"],
        data["locais_publicos"],
        previsao
    )

    # Inserir os dados no banco de dados
    try:
        conn = pg.connect(banco)
        cur = conn.cursor()
        cur.execute(query, valores)
        conn.commit()
    except (pg.Error) as error:
        print("Erro no banco:", error)
        return jsonify({"error": "Erro ao salvar os dados no banco de dados"}), 500
    finally:
        if conn:
            cur.close()
            conn.close()
            print("Conexões encerradas\n\n")
    
    # Retornar o resultado
    return jsonify({"result": bool(previsao)})

# Função de inicialização
if __name__ == '__main__':
    app.run(debug=True, port=5000, host="0.0.0.0")
