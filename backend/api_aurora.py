import os
import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

# --- CORREÇÃO FINAL AQUI ---
# O URL foi atualizado para corresponder ao seu front-end real.
frontend_url = "https://aurora-front.onrender.com"
CORS(app, resources={r"/analise_texto": {"origins": frontend_url}})

print("="*50)
print(f"API AURORA (MODO TEXTO) INICIADA. Permitindo pedidos de: {frontend_url}")
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
        # A resposta do Ollama já é uma string JSON, então vamos processá-la
        json_content = response.json()['message']['content']
        return json.loads(json_content)
    except Exception as e:
        print(f"Erro na chamada do LLM: {e}")
        return {"erro": str(e), "resumo_narrativo": "Falha ao contactar a IA."}

# Rota simplificada que recebe apenas JSON com texto
@app.route("/analise_texto", methods=["POST"])
def analise_texto_endpoint():
    dados = request.get_json()
    if not dados or 'texto' not in dados:
        return jsonify({"erro": "Nenhum texto fornecido."}), 400

    texto_usuario = dados['texto']
    print(f"\n--- Texto Recebido para Análise ---\n{texto_usuario}\n----------------------------------\n")

    resultado_final = extrair_dados_estruturados(texto_usuario)
    return jsonify(resultado_final)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)