import os
import google.generativeai as genai

def gerar_texto_issue(prompt):
    """Conecta ao Gemini e retorna o texto gerado."""
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    print("🤖 Pensando no texto da issue...")
    resposta = model.generate_content(prompt)
    return resposta.text
