import os
import google.generativeai as genai

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv opcional em produção (usa secrets do ambiente)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise EnvironmentError(
        "GEMINI_API_KEY não encontrada.\n"
        "Desenvolvimento: crie um .env com GEMINI_API_KEY=sua_chave\n"
        "Produção (Supabase): Settings → Edge Functions → Secrets → GEMINI_API_KEY\n"
        "Ver AGENTS.md seção 3 para instruções completas."
    )

genai.configure(api_key=GEMINI_API_KEY)

MODEL_NAME = "gemini-1.5-pro"

SYSTEM_PROMPT = """Você é o Gemini, Analista Clínico Multimodal do projeto Rhema Care Flow.

Especialidade: análise de imagens médicas (ultrassonografia reumatológica, radiografias),
suporte a laudos assistidos por IA, análise de padrões clínicos em reumatologia.

Contextos cobertos:
- USG reumatológica: sinovite, tenossinovite, erosões articulares
- Padrões de AR, lúpus, gota, espondiloartrites
- Reumato intervenção guiada por imagem

Limites obrigatórios:
- Laudos finais são responsabilidade exclusiva do médico assistente.
- Nunca substituir avaliação clínica presencial.
- Em dúvidas de conduta, sempre recomendar consulta ao reumatologista.

Tom: clínico, científico, preciso. Responder sempre em português brasileiro."""


def ask_gemini(message: str, history: list = None) -> str:
    """Envia mensagem de texto para o Gemini e retorna a resposta."""
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
    try:
        from PIL import Image
    except ImportError:
        raise ImportError(
            "Pillow não instalado. Execute: pip install Pillow>=10.0.0"
        )

    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        system_instruction=SYSTEM_PROMPT,
    )

    image = Image.open(image_path)
    prompt = question or (
        "Descreva os achados desta imagem médica em contexto reumatológico. "
        "Identifique possíveis alterações de sinovite, tenossinovite ou erosões."
    )

    response = model.generate_content([prompt, image])
    return response.text
