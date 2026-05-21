minirepo-gemini-bot/
├── .env                # Suas senhas (NUNCA será enviado ao GitHub)
├── .gitignore          # Diz ao Git para ignorar o .env
├── requirements.txt    # Lista de dependências
├── main.py             # Ponto de entrada do app
└── services/           # Pasta com as lógicas separadas
    ├── __init__.py     # Arquivo vazio (diz ao Python que é um pacote)
    ├── gemini_api.py   # Lógica exclusiva da IA
    └── github_api.py   # Lógica exclusiva do GitHub# gemibot
