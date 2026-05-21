import os
from github import Github

def criar_issue(repositorio, titulo, corpo):
    """Conecta ao GitHub e cria a issue no repositório especificado."""
    token = os.getenv("GITHUB_TOKEN")
    g = Github(token)
    
    print(f"🐙 Conectando ao repositório {repositorio}...")
    try:
        repo = g.get_repo(repositorio)
        issue = repo.create_issue(title=titulo, body=corpo)
        return issue.html_url
    except Exception as e:
        return f"Erro ao criar issue: {e}"
