import os
import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# Altere para o URL do seu front-end no Render
CORS(app, resources={r"/analise_texto": {"origins": "https://aurora-app.onrender.com"}}) 

print("="*50)
print("API AURORA (MODO TEXTO) INICIADA")
print("="*50)

def extrair_dados_estruturados(texto_usuario: str) -> dict:
    """Envia o texto para o Llama 3 para análise."""
    prompt_sistema = """
    Você é um assistente de IA especialista em analisar diários de enxaqueca para o app "Aurora".
    Sua tarefa é extrair informações estruturadas do texto fornecido.
    Sua saída DEVE ser um único objeto JSON válido. Preencha TODOS os campos.
    Se uma informação não for encontrada, use um valor vazio (`[]` ou `null`).
    O campo `resumo_narrativo` é obrigatório.

    Estrutura JSON:
    { "sintomas": [], "local_dor": [], "intensidade_dor": null, "gatilhos_potenciais": { "alimentacao": [], "ambiente": [], "rotina": [] }, "medicamentos": [], "sentimentos_emocoes": [], "resumo_narrativo": "" }
    """
    url_ollama = "http://localhost:11434/api/chat"
    payload = {"model": "llama3", "format": "json", "stream": False, "messages": [{"role": "system", "content": prompt_sistema}, {"role": "user", "content": texto_usuario}]}

    try:
        response = requests.post(url_ollama, json=payload, timeout=180)
        response.raise_for_status()
        return response.json()['message']['content']
    except Exception as e:
        print(f"Erro na chamada do LLM: {e}")
        return {"erro": str(e)}

# Rota simplificada que recebe apenas JSON com texto
@app.route("/analise_texto", methods=["POST"])
def analise_texto_endpoint():
    dados = request.get_json()
    if not dados or 'texto' not in dados:
        return jsonify({"erro": "Nenhum texto fornecido."}), 400

    texto_usuario = dados['texto']
    print(f"\n--- Texto Recebido para Análise ---\n{texto_usuario}\n----------------------------------\n")

    resultado_json = extrair_dados_estruturados(texto_usuario)
    # O Llama3 já retorna uma string JSON, então apenas a convertemos para um objeto Python
    resultado_final = json.loads(resultado_json)

    return jsonify(resultado_final)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)