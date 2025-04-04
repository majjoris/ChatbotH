from flask import Flask, request, jsonify,render_template
from flask_cors import CORS
import google.generativeai as genai
import markdown
import unicodedata

# Configuração da API do Google
GOOGLE_GEMINI_API_KEY = '...'  # Substitua pela sua chave real
genai.configure(api_key=GOOGLE_GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash-latest")

# Função para remover acentos
def remover_acentos(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

# Função para verificar se a pergunta é sobre harry potter
def verifica_pergunta(pergunta, palavras_chave):
    pergunta_normalizada = remover_acentos(pergunta.lower())  # Normaliza a pergunta
    return any(remover_acentos(palavra).lower() in pergunta_normalizada for palavra in palavras_chave)

# Função para ler palavras de um arquivo .txt
def ler_palavras(arquivo):
    try:
        with open(arquivo, 'r', encoding='utf-8') as arquivo:
            conteudo = arquivo.read()
            palavras_chave = [palavra.strip() for palavra in conteudo.split(',')]
        return palavras_chave
    except FileNotFoundError:
        print(f"Arquivo não encontrado: {arquivo}")
        return []

# Carregar palavras para pesquisa
pesquisa_palavras = ler_palavras("pesquisa_palavras.txt")

# Inicialização do Flask
app = Flask(__name__)
CORS(app)

# Lista para armazenar o histórico da conversa
historico_conversa = []

# Funçao flask para a pagina inicial 
@app.route('/')
def index():
    return render_template('index.html') 

@app.route('/pergunta', methods=['POST'])
def pergunta():
    # Obtém a pergunta do corpo da requisição JSON
    data = request.json
    pergunta_usuario = data.get('pergunta', '').strip()

    # Verifica se a pergunta está relacionada a harry potter
    if verifica_pergunta(pergunta_usuario, pesquisa_palavras):
        # Adiciona a pergunta do usuário ao histórico
        historico_conversa.append(f"Usuário: {pergunta_usuario}")
        
        # Cria o contexto da conversa
        contexto_conversa = '\n'.join(historico_conversa)
        
        # Gera a resposta usando o modelo, passando o contexto da conversa
        resposta = model.generate_content(contexto_conversa)

        # Adiciona a resposta ao histórico
        historico_conversa.append(f"Chatbot: {resposta.text}")

        # Converte o markdown para HTML
        resposta_formatada = markdown.markdown(resposta.text)
        return jsonify({'resposta': resposta_formatada})
    else:
        return jsonify({'resposta': "Desculpe, eu só posso responder perguntas relacionadas ao universo de Harry Potter."})

# Executa o servidor Flask
if __name__ == '__main__':
    app.run(debug=True)
