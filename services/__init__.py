"""
Pacote services — integrações com Gemini API e GitHub API.

Exporta as funções principais para uso direto:
    from services import ask_gemini, get_repo_summary
"""

from .gemini_api import ask_gemini, analyze_medical_image
from .github_api import get_repo_summary, create_issue_comment, list_open_issues

__all__ = [
    "ask_gemini",
    "analyze_medical_image",
    "get_repo_summary",
    "create_issue_comment",
    "list_open_issues",
]
