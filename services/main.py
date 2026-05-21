import os
from dotenv import load_dotenv
from services.gemini_api import gerar_texto_issue
from services.github_api import criar_issue

# Carrega as chaves de segurança do arquivo .env
load_dotenv()

def executar_app():
    # 1. Definir o que queremos da IA
    comando_ia = """
    Escreva o corpo de uma issue para o GitHub. 
    Peça para as IAs informarem qual o caminho/endpoint que usam do 'Claudefire'.
    Seja claro e amigável.
    """
    
    # 2. Chamar o serviço do Gemini
    texto_gerado = gerar_texto_issue(comando_ia)
    
    # 3. Chamar o serviço do GitHub
    repo_alvo = "JoaoRGLab/rhema-care-flow"
    titulo_issue = "[Chamado AIs] Qual o caminho do Claudefire? 🤖"
    
    link_resultado = criar_issue(repo_alvo, titulo_issue, texto_gerado)
    
    print("\n✅ Processo Finalizado!")
    print(f"Confira a issue em: {link_resultado}")

if __name__ == "__main__":
    executar_app()
