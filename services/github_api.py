"""
github_api.py — Integração com a GitHub API via PyGithub.

Funções disponíveis:
    get_repo_summary(full_name)        → str com resumo do repo
    list_open_issues(full_name)        → list[dict]
    create_issue_comment(full_name, issue_number, body) → str URL do comentário
    get_file_content(full_name, path)  → str conteúdo do arquivo
"""

import os
from github import Github, GithubException
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Inicializa cliente GitHub — funciona sem token (rate limit menor)
_gh = Github(GITHUB_TOKEN) if GITHUB_TOKEN else Github()


def get_repo_summary(full_name: str) -> str:
    """
    Retorna um resumo textual do repositório.

    Args:
        full_name: ex. "JoaoRG-lab/gemibot"

    Returns:
        String formatada com nome, descrição, stars, forks, issues abertas
        e os 5 commits mais recentes.
    """
    try:
        repo = _gh.get_repo(full_name)
        commits = list(repo.get_commits()[:5])

        lines = [
            f"# {repo.full_name}",
            f"Descrição : {repo.description or '(sem descrição)'}",
            f"Stars      : {repo.stargazers_count}",
            f"Forks      : {repo.forks_count}",
            f"Issues     : {repo.open_issues_count} abertas",
            f"Branch     : {repo.default_branch}",
            "",
            "## Commits recentes",
        ]
        for c in commits:
            sha = c.sha[:7]
            msg = c.commit.message.split("\n")[0][:80]
            date = c.commit.author.date.strftime("%Y-%m-%d")
            lines.append(f"  {sha}  {date}  {msg}")

        return "\n".join(lines)

    except GithubException as e:
        return f"[GitHub API erro {e.status}] {e.data.get('message', str(e))}"


def list_open_issues(full_name: str) -> list:
    """
    Lista issues abertas do repositório.

    Returns:
        Lista de dicts com id, number, title, labels, url.
    """
    try:
        repo = _gh.get_repo(full_name)
        issues = []
        for issue in repo.get_issues(state="open"):
            issues.append({
                "number": issue.number,
                "title": issue.title,
                "labels": [lb.name for lb in issue.labels],
                "url": issue.html_url,
                "created_at": issue.created_at.isoformat(),
            })
        return issues

    except GithubException as e:
        return [{"error": f"{e.status} — {e.data.get('message', str(e))}"}]


def create_issue_comment(full_name: str, issue_number: int, body: str) -> str:
    """
    Posta um comentário em uma issue do GitHub.

    Args:
        full_name    : ex. "JoaoRG-lab/rhema-care-flow"
        issue_number : número da issue
        body         : texto do comentário (Markdown aceito)

    Returns:
        URL do comentário criado.
    """
    try:
        repo = _gh.get_repo(full_name)
        issue = repo.get_issue(issue_number)
        comment = issue.create_comment(body)
        return comment.html_url

    except GithubException as e:
        raise RuntimeError(f"Erro ao comentar na issue #{issue_number}: {e.data.get('message', str(e))}")


def get_file_content(full_name: str, path: str, ref: str = None) -> str:
    """
    Retorna o conteúdo decodificado de um arquivo do repositório.

    Args:
        full_name : ex. "JoaoRG-lab/gemibot"
        path      : ex. "services/gemini_api.py"
        ref       : branch, tag ou commit SHA (padrão: branch default)

    Returns:
        Conteúdo do arquivo como string UTF-8.
    """
    try:
        repo = _gh.get_repo(full_name)
        kwargs = {"path": path}
        if ref:
            kwargs["ref"] = ref
        file_obj = repo.get_contents(**kwargs)
        return file_obj.decoded_content.decode("utf-8")

    except GithubException as e:
        raise FileNotFoundError(f"{path} não encontrado em {full_name}: {e.data.get('message', str(e))}")
