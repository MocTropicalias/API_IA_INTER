from flask import Flask, request, jsonify
import pickle
import pandas as pd
import os

app = Flask(__name__)

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


    caminho_arq_tratamento = os.path.dirname(__file__)+"\\pkls\\tratamento_dados.pkl"

    caminho_arq_modelo = os.path.dirname(__file__)+"\\pkls\\modelo.pkl"

    with open(caminho_arq_tratamento, 'rb') as f:
        tratamento_dados = pickle.load(f)

    with open(caminho_arq_modelo, 'rb') as f:
        modelo = pickle.load(f)
    
    dados = [data.copy()]
    
    dados = pd.DataFrame(dados,columns=required_keys)

    x = pd.DataFrame(tratamento_dados.transform(dados),columns=tratamento_dados.get_feature_names_out())

    previsao = modelo.predict(x)

    if previsao == 1:
        return jsonify({"result": True})
    else:
        return jsonify({"result": False})

def run_python_code(data):
    return True

if __name__ == '__main__':
    app.run(debug=True, port=5000, host="0.0.0.0")
