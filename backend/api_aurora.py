import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq

app = Flask(__name__)
# Certifique-se de que este é o URL correto do seu front-end
frontend_url = "https://aurora-front.onrender.com"
CORS(app, resources={r"/analise_texto": {"origins": frontend_url}})

# --- LÊ A CHAVE DE API DO AMBIENTE DO RENDER ---
try:
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    groq_api_key_found = True
except Exception as e:
    groq_api_key_found = False

print("="*50)
print(f"API AURORA INICIADA. Permitindo pedidos de: {frontend_url}")
if not groq_api_key_found:
    print("AVISO: A variável de ambiente GROQ_API_KEY não foi encontrada ou é inválida.")
print("="*50)

def extrair_dados_estruturados_com_groq(texto_usuario: str) -> dict:
    """Envia o texto para a API da Groq para análise com Llama3."""
    
    if not groq_api_key_found:
        return {"erro": "A chave da API da Groq não está configurada no servidor.", "resumo_narrativo": "Erro de configuração do servidor."}

    # --- PROMPT APRIMORADO E MAIS RIGOROSO ---
    prompt_sistema = """
    Your task is to act as a strict JSON formatting tool. Analyze the user's text and extract information into the provided JSON structure.

    **CRITICAL RULES:**
    1. Your entire output MUST be ONLY the JSON object.
    2. DO NOT include ```json, any explanation, or any text before or after the JSON object.
    3. You MUST fill every single field in the JSON structure.
    4. If a value is not found in the text, use an empty value like `[]` or `null`. The `resumo_narrativo` field is mandatory and must always contain a one-sentence summary.

    **JSON STRUCTURE TO POPULATE:**
    {
      "sintomas": [],
      "local_dor": [],
      "intensidade_dor": null,
      "gatilhos_potenciais": {
        "alimentacao": [],
        "ambiente": [],
        "rotina": []
      },
      "medicamentos": [],
      "sentimentos_emocoes": [],
      "resumo_narrativo": ""
    }
    """
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": prompt_sistema
                },
                {
                    "role": "user",
                    "content": f"User's text to analyze: {texto_usuario}",
                }
            ],
            model="llama3-70b-8192", 
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        
        json_string = chat_completion.choices[0].message.content
        return json.loads(json_string)

    except Exception as e:
        print(f"Erro na chamada da Groq: {e}")
        return {"erro": str(e), "resumo_narrativo": "Falha ao contactar a IA."}

@app.route("/analise_texto", methods=["POST"])
def analise_texto_endpoint():
    dados = request.get_json()
    if not dados or 'texto' not in dados:
        return jsonify({"erro": "Nenhum texto fornecido."}), 400
    
    texto_usuario = dados['texto']
    print(f"\n--- Texto Recebido para Análise ---\n{texto_usuario}\n----------------------------------\n")
    
    resultado_final = extrair_dados_estruturados_com_groq(texto_usuario)
    return jsonify(resultado_final)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
