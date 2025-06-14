# --- Importações e configuração inicial (sem alterações) ---
import os
import json
import requests
import torch
import librosa
from PIL import Image
from transformers import pipeline, AutoProcessor, AutoModelForCausalLM
from flask import Flask, request, jsonify
from flask_cors import CORS
import werkzeug.utils

app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

print("="*50)
print("INICIANDO SERVIDOR DE IA DO AURORA...")
print("="*50)

DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"
TORCH_DTYPE = torch.float16 if torch.cuda.is_available() else torch.float32
print(f"Usando dispositivo: {DEVICE}")

print("Carregando modelo de áudio (Whisper)...")
pipe_audio = pipeline("automatic-speech-recognition", model="openai/whisper-small", torch_dtype=TORCH_DTYPE, device=DEVICE)

print("Carregando modelo de visão (Moondream)...")
model_id_vision = "vikhyatk/moondream2"
processor_vision = AutoProcessor.from_pretrained(model_id_vision, trust_remote_code=True)
model_vision = AutoModelForCausalLM.from_pretrained(model_id_vision, torch_dtype=TORCH_DTYPE, trust_remote_code=True).to(DEVICE)

print("-" * 50)
print("Modelos carregados. Servidor pronto para receber pedidos.")
print("-" * 50)

def processar_audio(caminho_arquivo_audio: str) -> str:
    try:
        audio_input, _ = librosa.load(caminho_arquivo_audio, sr=16000)
        resultado = pipe_audio(audio_input)
        return resultado["text"].strip()
    except Exception as e:
        print(f"Erro ao processar áudio: {e}")
        return ""

def processar_imagem(caminho_arquivo_imagem: str) -> str:
    try:
        imagem = Image.open(caminho_arquivo_imagem)
        enc_image = model_vision.encode_image(imagem)
        descricao = model_vision.answer_question(enc_image, "<describe_image>", tokenizer=processor_vision)
        return descricao
    except Exception as e:
        print(f"Erro ao processar imagem: {e}")
        return ""

# --- FUNÇÃO ATUALIZADA COM PROMPT APRIMORADO ---
def extrair_dados_estruturados(texto_combinado: str) -> dict:
    """Envia o texto combinado para o Llama 3 com um prompt mais robusto."""
    
    # O novo prompt é mais direto, dá regras e um exemplo claro.
    prompt_sistema = """
    Você é um assistente de IA altamente preciso para o app "Aurora". Sua única função é analisar o texto do diário de um usuário e preencher **TODOS** os campos de uma estrutura JSON. Não omita nenhum campo.

    **REGRAS ESTRITAS:**
    1. Sua saída DEVE ser um único objeto JSON válido. Não inclua texto antes ou depois do JSON.
    2. Preencha **TODOS** os campos. Se nenhuma informação for encontrada, use um valor vazio ( `[]` para listas, `""` ou `null` para texto/números).
    3. O campo `resumo_narrativo` é **obrigatório**. Crie sempre um resumo de uma frase, mesmo que seja simples.

    **EXEMPLO DE USO:**
    - **Texto do Usuário:** "dor de cabeça terrível hoje. o dia no trabalho foi de muito estresse e acho que o café que tomei piorou a situação."
    - **JSON de Saída Esperado:**
      {
        "sintomas": ["dor de cabeça terrível"],
        "local_dor": [],
        "intensidade_dor": null,
        "gatilhos_potenciais": { "alimentacao": ["café"], "ambiente": [], "rotina": ["estresse no trabalho"] },
        "medicamentos": [],
        "sentimentos_emocoes": ["estressado"],
        "resumo_narrativo": "O usuário relatou uma dor de cabeça terrível, possivelmente associada a estresse no trabalho e consumo de café."
      }

    **ESTRUTURA JSON FINAL OBRIGATÓRIA:**
    {
      "sintomas": [], "local_dor": [], "intensidade_dor": null,
      "gatilhos_potenciais": { "alimentacao": [], "ambiente": [], "rotina": [] },
      "medicamentos": [], "sentimentos_emocoes": [], "resumo_narrativo": ""
    }
    """

    url_ollama = "http://localhost:11434/api/chat"
    payload = {"model": "llama3", "format": "json", "stream": False, "messages": [{"role": "system", "content": prompt_sistema}, {"role": "user", "content": texto_combinado}]}
    try:
        response = requests.post(url_ollama, json=payload, timeout=180) # Timeout aumentado para segurança
        response.raise_for_status()
        response_data = response.json()
        json_content = response_data['message']['content']
        return json.loads(json_content)
    except Exception as e:
        print(f"Erro na chamada do LLM: {e}")
        return {"erro": str(e)}

# --- Rota da API (sem alterações) ---
@app.route("/analise_multimodal", methods=["POST"])
def analise_multimodal_endpoint():
    if 'texto_usuario' not in request.form:
        return jsonify({"erro": "O campo 'texto_usuario' é obrigatório."}), 400

    texto_usuario = request.form['texto_usuario']
    caminho_audio = None
    caminho_imagem = None

    if 'arquivo_audio' in request.files:
        arquivo_audio = request.files['arquivo_audio']
        if arquivo_audio.filename != '':
            nome_seguro_audio = werkzeug.utils.secure_filename(arquivo_audio.filename)
            caminho_audio = os.path.join(app.config['UPLOAD_FOLDER'], nome_seguro_audio)
            arquivo_audio.save(caminho_audio)

    if 'arquivo_imagem' in request.files:
        arquivo_imagem = request.files['arquivo_imagem']
        if arquivo_imagem.filename != '':
            nome_seguro_imagem = werkzeug.utils.secure_filename(arquivo_imagem.filename)
            caminho_imagem = os.path.join(app.config['UPLOAD_FOLDER'], nome_seguro_imagem)
            arquivo_imagem.save(caminho_imagem)

    partes_texto = []
    if texto_usuario: partes_texto.append(f"Nota do usuário: {texto_usuario}")
    if caminho_audio: partes_texto.append(f"Transcrição de áudio: {processar_audio(caminho_audio)}")
    if caminho_imagem: partes_texto.append(f"Descrição da imagem: {processar_imagem(caminho_imagem)}")

    if not partes_texto: return jsonify({"erro": "Nenhum conteúdo válido para análise."}), 400

    texto_combinado = "\n\n".join(filter(None, partes_texto))
    print("\n--- Texto Combinado Recebido para Análise ---\n" + texto_combinado + "\n" + "-"*50 + "\n")
    
    resultado_final = extrair_dados_estruturados(texto_combinado)

    if caminho_audio and os.path.exists(caminho_audio): os.remove(caminho_audio)
    if caminho_imagem and os.path.exists(caminho_imagem): os.remove(caminho_imagem)

    return jsonify(resultado_final)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
