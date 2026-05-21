import os
from dotenv import load_dotenv
from services.gemini_api import gerar_texto_issue
from services.github_api import criar_issue

# Carrega as chaves de segurança do arquivo .env
load_dotenv()

def executar_app():
    print("🤖 --- Assistente Gemini + GitHub --- 🐙\n")
    
    # 1. Pede as informações diretamente no terminal
    repo_alvo = input("📌 Repositório alvo (ex: JoaoRGLab/rhema-care-flow): ")
    titulo_issue = input("🏷️  Título da Issue: ")
    comando_ia = input("🧠 O que a IA deve escrever? (Descreva o contexto): ")
    
    print("\n⏳ Processando... Deixe a IA pensar e o GitHub agir.")
    
    # 2. Gera o texto com o Gemini
    texto_gerado = gerar_texto_issue(comando_ia)
    
    # 3. Cria a issue no GitHub
    link_resultado = criar_issue(repo_alvo, titulo_issue, texto_gerado)
    
    print("\n✅ Processo Finalizado com Sucesso!")
    print(f"🔗 Confira o resultado em: {link_resultado}\n")

if __name__ == "__main__":
    executar_app()
