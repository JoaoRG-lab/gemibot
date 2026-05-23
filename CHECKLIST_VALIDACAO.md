# Checklist de Validação — Integração Gemini no Gemibot / Rhema Care Flow

**Versão:** 1.0 | **Data:** 2026-05-23 | **Repositório:** [JoaoRG-lab/gemibot](https://github.com/JoaoRG-lab/gemibot)

---

## 1. Pré-requisitos

### 1.1 Chave de API Gemini

| # | Verificação | Critério de aprovação | ✓/✗ | Evidência |
|---|---|---|---|---|
| 1.1.1 | Chave gerada no Google AI Studio | URL: https://aistudio.google.com/app/apikey — chave começa com `AIza` | | |
| 1.1.2 | `.env` local criado a partir de `.env.example` | Arquivo `.env` existe na raiz e **não** aparece no `git status` | | |
| 1.1.3 | `.env` listado no `.gitignore` | `grep GEMINI .gitignore` retorna linha ou `.env` está coberto | | |
| 1.1.4 | Variável carrega corretamente no Python | `python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(bool(os.getenv('GEMINI_API_KEY')))"` → `True` | | |

### 1.2 Dependências instaladas

| # | Verificação | Critério de aprovação | ✓/✗ | Evidência |
|---|---|---|---|---|
| 1.2.1 | `google-generativeai >= 0.7.0` instalada | `pip show google-generativeai` mostra versão ≥ 0.7 | | |
| 1.2.2 | `python-dotenv >= 1.0.0` instalada | `pip show python-dotenv` mostra versão ≥ 1.0 | | |
| 1.2.3 | `Pillow >= 10.0.0` instalada | `pip show Pillow` mostra versão ≥ 10 | | |
| 1.2.4 | `PyGithub >= 2.0.0` instalada | `pip show PyGithub` mostra versão ≥ 2.0 | | |

---

## 2. Validação Local — `gemibot`

### 2.1 Módulo `services/gemini_api.py`

| # | Verificação | Comando / Critério | ✓/✗ | Evidência |
|---|---|---|---|---|
| 2.1.1 | Arquivo existe no repo | `ls services/gemini_api.py` → sem erro | | |
| 2.1.2 | Importação sem erros | `python -c "from services.gemini_api import ask_gemini"` → sem traceback | | |
| 2.1.3 | `ask_gemini()` retorna string | Ver item 2.2 abaixo | | |
| 2.1.4 | Fallback gracioso sem chave | Renomear `.env` temporariamente → importar → deve retornar mensagem de erro legível, **não** `KeyError` nem `AttributeError` | | |

### 2.2 Teste de resposta básica

```bash
# Execute no diretório raiz do gemibot
python - <<'PY'
from dotenv import load_dotenv
load_dotenv()
from services.gemini_api import ask_gemini

resp = ask_gemini("Olá, você está funcionando?")
print(type(resp), "—", resp[:120])
PY
```

| Critério | Esperado |
|---|---|
| `type(resp)` | `<class 'str'>` |
| Comprimento | > 10 caracteres |
| Sem exceção | Nenhum traceback |

### 2.3 Teste com histórico de chat

```bash
python - <<'PY'
from dotenv import load_dotenv
load_dotenv()
from services.gemini_api import ask_gemini

historico = [
    {"role": "user", "parts": ["Meu nome é João Otávio"]},
    {"role": "model", "parts": ["Entendido, João Otávio!"]}
]
resp = ask_gemini("Qual é meu nome?", history=historico)
print(resp[:200])
PY
```

| Critério | Esperado |
|---|---|
| Resposta menciona "João" | `True` |
| Sem exceção | Nenhum traceback |

### 2.4 Teste de análise de imagem médica (Vision)

```bash
python - <<'PY'
from dotenv import load_dotenv
load_dotenv()
from services.gemini_api import analyze_medical_image
from PIL import Image
import io

# Cria imagem de teste mínima
img = Image.new("RGB", (100, 100), color=(200, 200, 200))
buf = io.BytesIO()
img.save(buf, format="JPEG")
buf.seek(0)

resp = analyze_medical_image(buf.read(), prompt="Descreva o que vê nesta imagem de teste.")
print(type(resp), "—", resp[:200])
PY
```

| Critério | Esperado |
|---|---|
| `type(resp)` | `<class 'str'>` |
| Sem exceção de tipo | Nenhum traceback |

---

## 3. Validação no Supabase

### 3.1 Secret configurado

| # | Verificação | Critério | ✓/✗ | Evidência |
|---|---|---|---|---|
| 3.1.1 | Secret `GEMINI_API_KEY` criado | Supabase Dashboard → Project Settings → Edge Functions → Secrets → nome `GEMINI_API_KEY` aparece na lista | | |
| 3.1.2 | Valor começa com `AIza` | Confirmado no momento da criação (Supabase não exibe valor depois de salvo) | | |

### 3.2 Edge Function com acesso à chave

```bash
# Substitua PROJECT_REF e ANON_KEY
curl -X POST "https://<PROJECT_REF>.supabase.co/functions/v1/gemini-chat" \
  -H "Authorization: Bearer <ANON_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"message": "Olá, Gemini! Responda com uma palavra."}'
```

| Critério | Esperado |
|---|---|
| HTTP status | `200` |
| Body contém `"response"` | `true` |
| Sem `"error": "missing GEMINI_API_KEY"` | `true` |

### 3.3 Fallback quando chave ausente

```bash
curl -X POST "https://<PROJECT_REF>.supabase.co/functions/v1/gemini-chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "teste"}'
```

| Critério | Esperado |
|---|---|
| HTTP status | `401` ou `403` (não `500`) |
| Body contém mensagem legível | `true` |

---

## 4. Validação no Rhema Care Flow (`/ai-panel`)

### 4.1 Painel carrega sem erros

| # | Verificação | Critério | ✓/✗ | Evidência |
|---|---|---|---|---|
| 4.1.1 | Rota `/ai-panel` acessível | Navegação sem 404 | | |
| 4.1.2 | Console do browser sem erros vermelhos | DevTools → Console → 0 erros críticos | | |
| 4.1.3 | Campo de mensagem visível | Input/textarea presente no DOM | | |
| 4.1.4 | Botão de envio habilitado | Não está `disabled` na carga inicial | | |

### 4.2 Fluxo de envio de mensagem

| # | Passo | Critério de aprovação | ✓/✗ |
|---|---|---|---|
| 4.2.1 | Digitar mensagem e clicar "Enviar" | Indicador de loading aparece ≤ 500 ms | |
| 4.2.2 | Aguardar resposta | Resposta do Gemini aparece ≤ 15 s | |
| 4.2.3 | Resposta é texto legível | Sem `[object Object]` ou JSON cru | |
| 4.2.4 | Histórico persiste durante a sessão | 2ª mensagem referencia contexto da 1ª | |

### 4.3 Teste clínico reumatológico

Enviar a seguinte mensagem no painel:

> "Paciente 52 anos, FR positivo 1:320, anti-CCP positivo, erosões em RX de mãos bilaterais. Qual a classificação ACR/EULAR 2010?"

| Critério | Esperado |
|---|---|
| Resposta menciona escore ≥ 6 pontos | `true` |
| Cita critérios (sorológico, imagem, duração) | `true` |
| Não inventa medicamentos sem solicitar | `true` |
| Tom técnico/clínico mantido | `true` |

### 4.4 Protocolo TMR — verificações de segurança

> ⚠️ **NUNCA modificar dados do `rhema-care-flow` através do `gemibot`**

| # | Verificação | Critério | ✓/✗ |
|---|---|---|---|
| 4.4.1 | `gemibot` não tem acesso à API do Supabase do `rhema-care-flow` | Nenhuma `SUPABASE_URL` do projeto clínico no `.env` do `gemibot` | |
| 4.4.2 | Sem rotas de escrita expostas pelo gemibot | Nenhum endpoint `POST/PUT/DELETE` que altera dados de pacientes | |
| 4.4.3 | Logs de conversa isolados | Logs do gemibot não mesclam com registros clínicos | |

---

## 5. Validação de Logs e Monitoramento

| # | Verificação | Critério | ✓/✗ | Evidência |
|---|---|---|---|---|
| 5.1 | Log de inicialização Gemini | Linha `[GEMINI] API inicializada com sucesso` nos logs | | |
| 5.2 | Log de erros quando chave inválida | Linha `[GEMINI] ERRO: chave inválida` em vez de traceback | | |
| 5.3 | Tempo de resposta logado | Cada chamada loga `[GEMINI] tempo: Xs` | | |
| 5.4 | Supabase Edge Function Logs | Dashboard → Functions → Logs → últimas 10 invocações sem `status: error` | | |

---

## 6. GitHub Actions (CI/CD)

| # | Verificação | Critério | ✓/✗ | Evidência |
|---|---|---|---|---|
| 6.1 | Secret `GEMINI_API_KEY` configurado no repo | Settings → Secrets → Actions → `GEMINI_API_KEY` listado | | |
| 6.2 | Workflow passa sem expor a chave em logs | Logs do GitHub Actions não contêm `AIza...` | | |
| 6.3 | Teste de smoke no pipeline | Job de teste retorna exit code 0 | | |

---

## 7. Resumo Executivo

| Categoria | Total | Aprovados | Reprovados | Status |
|---|---|---|---|---|
| 1. Pré-requisitos | 8 | | | |
| 2. Testes locais | 9 | | | |
| 3. Supabase | 5 | | | |
| 4. Rhema Care Flow | 11 | | | |
| 5. Logs | 4 | | | |
| 6. GitHub Actions | 3 | | | |
| **TOTAL** | **40** | | | |

**Responsável pela validação:** ___________________________

**Data de execução:** _____ / _____ / 2026

**SHA do commit validado:** ________________________________

---

> **Nota de segurança:** Este arquivo pode ser commitado. Nunca preencher o campo Evidência com valores reais de chaves de API — usar apenas "OK confirmado" ou similar.
