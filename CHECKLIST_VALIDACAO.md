# Checklist de Validação — Integração Gemini · Gemibot / Rhema Care Flow

**Versão:** 2.0 | **Data:** 2026-05-23 | **Repositório:** [JoaoRG-lab/gemibot](https://github.com/JoaoRG-lab/gemibot)

> Preencher **✓** (aprovado), **✗** (reprovado) ou **N/A**. Nunca registrar valores reais de chaves em "Evidência" — usar apenas "OK confirmado" ou similar.

---

## 1. Pré-requisitos

### 1.1 Chave de API Gemini

| # | Verificação | Critério de aprovação | ✓/✗ | Evidência |
|---|---|---|---|---|
| 1.1.1 | Chave gerada no Google AI Studio | [aistudio.google.com](https://aistudio.google.com/app/apikey) — valor começa com `AIza` | | |
| 1.1.2 | `.env` local criado a partir de `.env.example` | Arquivo `.env` existe na raiz e **não** aparece em `git status` | | |
| 1.1.3 | `.env` coberto pelo `.gitignore` | `grep '\.env' .gitignore` retorna resultado | | |
| 1.1.4 | Variável carregável no Python | `python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(bool(os.getenv('GEMINI_API_KEY')))"` → `True` | | |

### 1.2 Dependências instaladas

| # | Pacote | Comando de verificação | Versão mínima | ✓/✗ |
|---|---|---|---|---|
| 1.2.1 | `google-generativeai` | `pip show google-generativeai` | ≥ 0.7.0 | |
| 1.2.2 | `python-dotenv` | `pip show python-dotenv` | ≥ 1.0.0 | |
| 1.2.3 | `Pillow` | `pip show Pillow` | ≥ 10.0.0 | |
| 1.2.4 | `PyGithub` | `pip show PyGithub` | ≥ 2.0.0 | |

### 1.3 Estrutura de arquivos

| # | Arquivo | Esperado | ✓/✗ |
|---|---|---|---|
| 1.3.1 | `services/gemini_api.py` | Existe e não está vazio | |
| 1.3.2 | `main.py` | Existe e importa `ask_gemini` ou `gemini_api` | |
| 1.3.3 | `AGENTS.md` | Existe com instruções de configuração | |
| 1.3.4 | `.env.example` | Contém `GEMINI_API_KEY=` (sem valor real) | |
| 1.3.5 | `requirements.txt` | Lista os 4 pacotes com versão mínima | |

---

## 2. Validação Local — `gemibot`

### 2.1 Importação e módulo `gemini_api`

| # | Verificação | Critério | ✓/✗ | Evidência |
|---|---|---|---|---|
| 2.1.1 | Importação sem traceback | `python -c "from services.gemini_api import ask_gemini"` → sem erro | | |
| 2.1.2 | `analyze_medical_image` exportada | `python -c "from services.gemini_api import analyze_medical_image"` → sem erro | | |
| 2.1.3 | Fallback gracioso sem chave | Renomear `.env` temporariamente → `ask_gemini("teste")` → retorna `str` com mensagem de erro, **sem** `KeyError` ou `AttributeError` | | |

### 2.2 Teste de resposta básica

```bash
python - <<'PY'
from dotenv import load_dotenv
load_dotenv()
from services.gemini_api import ask_gemini

resp = ask_gemini("Olá, você está funcionando? Responda em uma frase.")
print(type(resp), "—", resp[:150])
assert isinstance(resp, str) and len(resp) > 10, "FALHOU"
print("OK")
PY
```

| Critério | Esperado | ✓/✗ |
|---|---|---|
| `type(resp)` é `str` | `True` | |
| `len(resp) > 10` | `True` | |
| Sem exceção | Nenhum traceback | |

### 2.3 Teste com histórico de chat

```bash
python - <<'PY'
from dotenv import load_dotenv
load_dotenv()
from services.gemini_api import ask_gemini

historico = [
    {"role": "user", "parts": ["Meu nome é João Otávio e sou reumatologista."]},
    {"role": "model", "parts": ["Entendido, Dr. João Otávio!"]}
]
resp = ask_gemini("Qual é meu nome e especialidade?", history=historico)
print(resp[:200])
assert "João" in resp or "joao" in resp.lower(), "Contexto não preservado"
print("OK")
PY
```

| Critério | Esperado | ✓/✗ |
|---|---|---|
| Resposta menciona "João" | `True` | |
| Contexto de especialidade preservado | `True` | |

### 2.4 Teste de análise de imagem médica (Vision)

```bash
python - <<'PY'
from dotenv import load_dotenv
load_dotenv()
from services.gemini_api import analyze_medical_image
from PIL import Image
import io

img = Image.new("RGB", (200, 200), color=(180, 180, 180))
buf = io.BytesIO()
img.save(buf, format="JPEG")
buf.seek(0)

resp = analyze_medical_image(buf.read(), prompt="Descreva o que vê nesta imagem de teste.")
print(type(resp), "—", resp[:200])
assert isinstance(resp, str), "FALHOU"
print("OK")
PY
```

| Critério | Esperado | ✓/✗ |
|---|---|---|
| `type(resp)` é `str` | `True` | |
| Sem exceção de tipo | Nenhum traceback | |

### 2.5 Teste clínico reumatológico (qualidade da resposta)

```bash
python - <<'PY'
from dotenv import load_dotenv
load_dotenv()
from services.gemini_api import ask_gemini

pergunta = (
    "Paciente 52 anos, FR positivo 1:320, anti-CCP positivo, "
    "erosões em RX de mãos bilaterais, sinovite há 8 semanas. "
    "Qual a classificação ACR/EULAR 2010 e a pontuação?"
)
resp = ask_gemini(pergunta)
print(resp[:500])
PY
```

| Critério | Esperado | ✓/✗ |
|---|---|---|
| Resposta menciona escore ≥ 6 pontos | `True` | |
| Cita critérios (sorologia, imagem, duração) | `True` | |
| Tom técnico/clínico mantido | `True` | |
| Não alucina medicamentos sem solicitar | `True` | |

### 2.6 Integração com `main.py`

| # | Verificação | Critério | ✓/✗ |
|---|---|---|---|
| 2.6.1 | `python main.py` inicia sem traceback | Exit code 0 ou aguarda input (sem crash imediato) | |
| 2.6.2 | `main.py` não expõe chave em stdout | Nenhuma linha com `AIza` na saída | |

---

## 3. Validação no Supabase

### 3.1 Secret configurado

| # | Verificação | Critério | ✓/✗ | Evidência |
|---|---|---|---|---|
| 3.1.1 | Secret `GEMINI_API_KEY` criado | Supabase Dashboard → Project Settings → Edge Functions → Secrets → `GEMINI_API_KEY` aparece na lista | | |
| 3.1.2 | Valor correto (confirmado no momento da criação) | Supabase não exibe após salvo — anotar "criado em DD/MM/AAAA" | | |

### 3.2 Edge Function — requisição autenticada

```bash
# Substitua <PROJECT_REF> e <ANON_KEY>
curl -s -o response.json -w "%{http_code}" \
  -X POST "https://<PROJECT_REF>.supabase.co/functions/v1/gemini-chat" \
  -H "Authorization: Bearer <ANON_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"message": "Responda com exatamente uma palavra: funcionando."}'

cat response.json
```

| Critério | Esperado | ✓/✗ |
|---|---|---|
| HTTP status | `200` | |
| Body contém chave `"response"` | `true` | |
| Sem `"error": "missing GEMINI_API_KEY"` | `true` | |

### 3.3 Edge Function — sem autenticação (fallback de segurança)

```bash
curl -s -w "\nHTTP: %{http_code}" \
  -X POST "https://<PROJECT_REF>.supabase.co/functions/v1/gemini-chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "teste"}'
```

| Critério | Esperado | ✓/✗ |
|---|---|---|
| HTTP status | `401` ou `403` (não `500`) | |
| Body contém mensagem legível | `true` | |
| Nenhuma chave exposta no body | `true` | |

### 3.4 Logs da Edge Function

| # | Verificação | Critério | ✓/✗ |
|---|---|---|---|
| 3.4.1 | Sem erros nas últimas 10 invocações | Supabase Dashboard → Functions → Logs → 0 entradas com `status: error` | |
| 3.4.2 | Tempo de resposta aceitável | Média < 10 s por invocação | |

---

## 4. Protocolo TMR — Segurança de Dados Clínicos

> ⚠️ **Regra absoluta:** O `gemibot` NUNCA deve ler ou escrever dados de pacientes no `rhema-care-flow`.

| # | Verificação | Critério | ✓/✗ |
|---|---|---|---|
| 4.1 | `gemibot` sem `SUPABASE_URL` do projeto clínico | `grep -r "rhema" .env .env.example` → sem resultado | |
| 4.2 | Sem endpoints de escrita de dados clínicos | Nenhum route `POST/PUT/DELETE` em `main.py` ou `services/` altera registros de pacientes | |
| 4.3 | Sem importação direta do banco clínico | `grep -r "rhema-care-flow\|pacientes\|consultas" services/` → sem resultado relevante | |
| 4.4 | Logs do gemibot isolados | Nenhum arquivo de log mescla IDs de pacientes reais com histórico de chat | |
| 4.5 | Revisão manual do `services/gemini_api.py` | Nenhuma chamada a API externa além de `generativeai` | |

---

## 5. Validação no Rhema Care Flow (`/ai-panel`)

### 5.1 Painel carrega

| # | Verificação | Critério | ✓/✗ | Evidência |
|---|---|---|---|---|
| 5.1.1 | Rota `/ai-panel` acessível | Sem 404 | | |
| 5.1.2 | Console do browser sem erros críticos | DevTools → Console → 0 erros vermelhos | | |
| 5.1.3 | Campo de mensagem visível e funcional | Input/textarea presente e editável | | |
| 5.1.4 | Botão enviar não está desabilitado | `disabled` ausente no estado inicial | | |

### 5.2 Fluxo de envio

| # | Passo | Critério | ✓/✗ |
|---|---|---|---|
| 5.2.1 | Digitar mensagem e enviar | Loading indicator ≤ 500 ms | |
| 5.2.2 | Aguardar resposta | Texto do Gemini aparece ≤ 15 s | |
| 5.2.3 | Resposta é texto legível | Sem `[object Object]` ou JSON bruto | |
| 5.2.4 | Histórico da sessão preservado | 2ª pergunta acessa contexto da 1ª | |
| 5.2.5 | Estado de erro exibido corretamente | Desconectar rede → mensagem de erro amigável (não traceback) | |

---

## 6. Logs e Monitoramento

| # | Verificação | Critério | ✓/✗ | Evidência |
|---|---|---|---|---|
| 6.1 | Log de inicialização Gemini | `[GEMINI] API inicializada` nos logs de startup | | |
| 6.2 | Log de erro quando chave inválida | `[GEMINI] ERRO: chave inválida` em vez de traceback | | |
| 6.3 | Tempo de resposta logado | Cada chamada registra `[GEMINI] tempo: Xs` | | |
| 6.4 | Nenhuma chave nos logs | `grep -r "AIza" logs/` → sem resultado | | |

---

## 7. GitHub Actions (CI/CD)

| # | Verificação | Critério | ✓/✗ | Evidência |
|---|---|---|---|---|
| 7.1 | Secret `GEMINI_API_KEY` no repositório | Settings → Secrets → Actions → `GEMINI_API_KEY` listado | | |
| 7.2 | Chave não exposta em logs | Logs do pipeline não contêm `AIza` | | |
| 7.3 | Smoke test no pipeline passa | Job de teste → exit code `0` | | |
| 7.4 | Deploy não quebra sem a chave | Pipeline com secret ausente retorna erro claro, não crash silencioso | | |

---

## 8. Resumo Executivo

| Seção | Total de itens | Aprovados | Reprovados | N/A | Status |
|---|---|---|---|---|---|
| 1. Pré-requisitos | 13 | | | | |
| 2. Testes locais | 13 | | | | |
| 3. Supabase | 7 | | | | |
| 4. Protocolo TMR | 5 | | | | |
| 5. Rhema Care Flow | 9 | | | | |
| 6. Logs | 4 | | | | |
| 7. GitHub Actions | 4 | | | | |
| **TOTAL** | **55** | | | | |

**Responsável pela validação:** ___________________________

**Data de execução:** _____ / _____ / 2026

**SHA do commit validado:** ________________________________

**Versão do `google-generativeai` em uso:** ________________

---

> **Referências internas:** [`AGENTS.md`](./AGENTS.md) · [`services/gemini_api.py`](./services/gemini_api.py) · [`requirements.txt`](./requirements.txt)
