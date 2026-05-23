# AGENTS.md — Gemibot: Instruções para o Gemini como Agente Autônomo

> **Para agentes de IA que lêem este arquivo:** Este repositório é o `gemibot`, um bot Python que integra a Google Gemini API com a GitHub API. Você, como agente, é o **Analista Clínico Multimodal** do ecossistema `rhema-care-flow`. Leia este arquivo completamente antes de qualquer ação.

---

## 1. Identidade e Papel

Você é o **Gemini**, operando como `analista_clinico` no ecossistema multi-agente do projeto **Rhema Care Flow**.

| Campo | Valor |
|-------|-------|
| **Agente** | `gemini` |
| **Contexto API** | `analista_clinico` |
| **Repositório principal** | `JoaoRG-lab/rhema-care-flow` |
| **Repositório do bot** | `JoaoRG-lab/gemibot` |
| **Modelo** | `gemini-1.5-pro` |
| **Especialidade** | USG reumatológica, análise multimodal de imagens médicas, laudos assistidos por IA |

---

## 2. Arquitetura do Projeto

```
gemibot/
├── AGENTS.md           ← Você está aqui
├── .env                ← Secrets locais (NUNCA commitar)
├── .gitignore          ← .env está ignorado
├── requirements.txt    ← Dependências Python
├── main.py             ← Ponto de entrada
└── services/
    ├── __init__.py     ← Pacote Python
    ├── gemini_api.py   ← Lógica da Gemini API
    └── github_api.py   ← Lógica da GitHub API
```

### Como o bot funciona

```
main.py
  └─→ services/gemini_api.py
          └─→ POST generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent
                  Authorization: key=GEMINI_API_KEY
  └─→ services/github_api.py
          └─→ GET/POST api.github.com
                  Authorization: Bearer GITHUB_TOKEN
```

---

## 3. Configuração de Secrets — Passo a Passo

### 3.1 Variáveis de ambiente locais (desenvolvimento)

Crie um arquivo `.env` na raiz do repositório (ele está no `.gitignore` e NUNCA será commitado):

```env
# .env — NUNCA commitar este arquivo
GEMINI_API_KEY=sua_chave_aqui
GITHUB_TOKEN=seu_token_aqui
```

### 3.2 GEMINI_API_KEY — Como obter

1. Acesse **[Google AI Studio](https://aistudio.google.com/app/apikey)**
2. Clique em **"Create API Key"**
3. Selecione o projeto Google Cloud associado
4. Copie a chave gerada (formato: `AIzaSy...`)
5. Cole no `.env` local: `GEMINI_API_KEY=AIzaSy...`

> ⚠️ **Segurança:** Nunca cole a chave em chats, issues, commits ou qualquer campo de texto não criptografado. Se uma chave for exposta, revogue imediatamente no Google AI Studio e gere uma nova.

### 3.3 Configurar GEMINI_API_KEY no Supabase (produção)

Esta é a configuração que ativa o Gemini no painel multi-IA do `rhema-care-flow`:

```
1. Acesse: https://app.supabase.com
2. Selecione o projeto: rhema-care-flow
3. Navegue: Settings → Edge Functions → Secrets
4. Clique em: + New Secret
   Name:  GEMINI_API_KEY
   Value: <cole a nova chave do Google AI Studio>
5. Clique: Save
```

Após salvar, a Edge Function `ai-assistant` (v3.0) roteará automaticamente:
- Requisições com `agent: "gemini"` ou `context: "analista_clinico"` → **Gemini 1.5 Pro**
- Demais agentes → **Perplexity sonar-pro**

Não é necessário redeploy — o secret é lido na próxima invocação.

### 3.4 Configurar no GitHub Actions (CI/CD)

Se o bot rodar via GitHub Actions:

```
1. Acesse: https://github.com/JoaoRG-lab/gemibot/settings/secrets/actions
2. Clique: New repository secret
   Name:  GEMINI_API_KEY
   Value: <chave do Google AI Studio>
3. Clique: Add secret

4. Para o GITHUB_TOKEN: já é injetado automaticamente pelo Actions.
   Nunca crie um secret manual chamado GITHUB_TOKEN.
```

---

## 4. Dependências

```txt
# requirements.txt atual
google-generativeai
PyGithub
```

Instalar localmente:
```bash
pip install -r requirements.txt
```

### Versões recomendadas

| Pacote | Versão mínima | Notas |
|--------|--------------|-------|
| `google-generativeai` | `0.7.0+` | Suporte a `gemini-1.5-pro` e `system_instruction` |
| `PyGithub` | `2.0.0+` | API v3, suporte a GraphQL via requests |
| `python-dotenv` | `1.0.0+` | Para carregar `.env` localmente |
| `Pillow` | `10.0.0+` | Para análise de imagens médicas |

Adicionar ao `requirements.txt` quando usar análise de imagens:
```
python-dotenv>=1.0.0
Pillow>=10.0.0
```

---

## 5. Configuração do `gemini_api.py`

Estrutura esperada do `services/gemini_api.py`:

```python
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()  # Carrega .env local

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise EnvironmentError("GEMINI_API_KEY não configurada. Ver AGENTS.md seção 3.")

genai.configure(api_key=GEMINI_API_KEY)

MODEL_NAME = "gemini-1.5-pro"

SYSTEM_PROMPT = """Você é o Gemini, Analista Clínico Multimodal do projeto Rhema Care Flow.

Especialidade: análise de imagens médicas (ultrassonografia reumatológica, radiografias),
suporte a laudos assistidos por IA, análise de padrões clínicos em reumatologia.

Contextos cobertos:
- USG reumatológica: sinovite, tenossinovite, erosões
- Padrões de AR, lúpus, gota, espondiloartrites
- Reumato intervenção guiada por imagem

Limites: laudos finais são responsabilidade do médico. Nunca substituir avaliação clínica.
Tom: clínico, científico, preciso. Responder em português brasileiro."""


def ask_gemini(message: str, history: list = None) -> str:
    """Envia mensagem para o Gemini e retorna a resposta."""
    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        system_instruction=SYSTEM_PROMPT,
    )
    
    if history:
        chat = model.start_chat(history=history)
        response = chat.send_message(message)
    else:
        response = model.generate_content(message)
    
    return response.text


def analyze_medical_image(image_path: str, question: str = None) -> str:
    """Analisa imagem médica (USG, RX) com o Gemini Vision."""
    from PIL import Image
    
    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        system_instruction=SYSTEM_PROMPT,
    )
    
    image = Image.open(image_path)
    prompt = question or "Descreva os achados desta imagem médica em contexto reumatológico."
    
    response = model.generate_content([prompt, image])
    return response.text
```

---

## 6. Conexão com o Ecossistema Rhema Care Flow

### Como a Edge Function roteou para você

Quando o painel `/ai-panel` do `rhema-care-flow` envia uma mensagem para o agente Gemini:

```json
POST /functions/v1/ai-assistant
{
  "message": "Analise este padrão de sinovite na USG",
  "agent": "gemini",
  "context": "analista_clinico"
}
```

A Edge Function `ai-assistant` v3.0 detecta `agent === "gemini"` e chama:
```
GET https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key=GEMINI_API_KEY
```

Se `GEMINI_API_KEY` não estiver configurada no Supabase, **o sistema faz fallback gracioso para Perplexity** com o mesmo system prompt clínico — sem erro para o usuário.

### Protocolo TMR (não violar)

```
❌ NÃO reativar deploy.yml ou ci.yml no rhema-care-flow
❌ NÃO criar workflow paralelo ao TMR
❌ NÃO alterar src/lib/medical*.ts, clinicalScores.ts, healthCycleEngine.ts
✅ Commits atômicos: feat(scope): descrição ou fix(scope): descrição
✅ Comentar no Issue de coordenação ao concluir cada fase
✅ Verificar que o TMR passou antes de reportar sucesso
```

---

## 7. Comandos Rápidos

```bash
# Instalar dependências
pip install -r requirements.txt

# Testar conexão com Gemini
python -c "from services.gemini_api import ask_gemini; print(ask_gemini('Teste de conexão'))"

# Verificar secret configurado
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('OK' if os.getenv('GEMINI_API_KEY') else 'GEMINI_API_KEY não encontrada')"

# Rodar o bot
python main.py
```

---

## 8. Segurança — Checklist Obrigatório

- [ ] `.env` está no `.gitignore` e **nunca foi commitado**
- [ ] `GEMINI_API_KEY` configurada no Supabase via dashboard (não via código)
- [ ] Nenhuma chave de API aparece em issues, PRs, commits ou logs
- [ ] Se uma chave foi exposta: **revogar imediatamente** em [Google AI Studio](https://aistudio.google.com/app/apikey)
- [ ] GitHub Actions usa secrets do repositório, não variáveis hardcoded

---

## 9. Stack de Referência

```
Bot repo:      JoaoRG-lab/gemibot
Principal:     JoaoRG-lab/rhema-care-flow
Domínio:       https://www.reumatismos.com
Edge Function: supabase/functions/ai-assistant (v3.0)
Painel IA:     /ai-panel → src/components/ai/AIIntegrationPanel.tsx
Gemini model:  gemini-1.5-pro
Python:        3.11+
```

---

*Atualizado em 2026-05-23 · Rhema Care Flow v3.0 · Gemini como `analista_clinico`*
