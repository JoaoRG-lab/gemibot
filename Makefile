.PHONY: install test chat imagem-demo repo-demo lint

# Instala todas as dependências
install:
	pip install -r requirements.txt

# Testa conexão com Gemini
test:
	@echo "--- Verificando GEMINI_API_KEY ---"
	@python -c "import os; from dotenv import load_dotenv; load_dotenv(); \
key = os.getenv('GEMINI_API_KEY'); \
print('OK — chave configurada' if key else 'ERRO — GEMINI_API_KEY não encontrada')"
	@echo "--- Testando chamada à API ---"
	@python -c "\
from services.gemini_api import ask_gemini; \
resp = ask_gemini('Responda em uma palavra: o modelo está funcionando?'); \
print('Gemini respondeu:', resp[:100])"

# Inicia chat interativo
chat:
	python main.py chat

# Demo: analisa imagem médica
imagem-demo:
	@echo "Uso: make imagem-demo FILE=caminho/imagem.jpg"
	@test -n "$(FILE)" && python main.py imagem $(FILE) || echo "Defina FILE=<caminho>"

# Demo: resumo do repo gemibot
repo-demo:
	python main.py repo JoaoRG-lab/gemibot

# Linting básico
lint:
	python -m py_compile main.py services/gemini_api.py services/github_api.py services/__init__.py
	@echo "Sintaxe OK"
