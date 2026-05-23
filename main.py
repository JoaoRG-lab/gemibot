#!/usr/bin/env python3
"""
gemibot — Ponto de entrada principal.
Executa no modo CLI interativo ou processa um único prompt via argumento.
"""

import sys
import argparse
from services.gemini_api import ask_gemini, analyze_medical_image
from services.github_api import get_repo_summary, create_issue_comment


def cli_chat():
    """Modo chat interativo no terminal."""
    print("gemibot — Analista Clínico Multimodal (Rhema Care Flow)")
    print("Gemini 1.5 Pro · Digite 'sair' para encerrar\n")

    history = []

    while True:
        try:
            user_input = input("Você: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nEncerrando.")
            break

        if not user_input:
            continue
        if user_input.lower() in ("sair", "exit", "quit"):
            print("Encerrando.")
            break

        try:
            response = ask_gemini(user_input, history=history)
            print(f"\nGemini: {response}\n")

            # Atualiza histórico no formato esperado pela SDK
            history.append({"role": "user", "parts": [user_input]})
            history.append({"role": "model", "parts": [response]})

        except Exception as e:
            print(f"[ERRO] {e}\n")


def cli_image(image_path: str, question: str = None):
    """Analisa uma imagem médica via Gemini Vision."""
    print(f"Analisando imagem: {image_path}")
    result = analyze_medical_image(image_path, question)
    print(f"\nGemini:\n{result}")


def cli_github_summary(repo: str):
    """Mostra resumo de um repositório GitHub."""
    print(f"Buscando informações: {repo}")
    summary = get_repo_summary(repo)
    print(summary)


def main():
    parser = argparse.ArgumentParser(
        prog="gemibot",
        description="Bot Gemini para análise clínica e integração com GitHub",
    )
    subparsers = parser.add_subparsers(dest="command")

    # Subcomando: chat (padrão)
    subparsers.add_parser("chat", help="Chat interativo com o Gemini")

    # Subcomando: imagem
    img_parser = subparsers.add_parser("imagem", help="Analisa imagem médica")
    img_parser.add_argument("arquivo", help="Caminho da imagem (JPG/PNG)")
    img_parser.add_argument("--pergunta", help="Pergunta específica sobre a imagem")

    # Subcomando: repo
    repo_parser = subparsers.add_parser("repo", help="Resumo de repositório GitHub")
    repo_parser.add_argument("nome", help="owner/repo ex: JoaoRG-lab/gemibot")

    args = parser.parse_args()

    if args.command == "imagem":
        cli_image(args.arquivo, args.pergunta)
    elif args.command == "repo":
        cli_github_summary(args.nome)
    else:
        # Padrão: modo chat
        cli_chat()


if __name__ == "__main__":
    main()
