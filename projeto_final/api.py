import os
import ast
import base64
from typing import Any, Dict, Tuple, Optional
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from pydantic import BaseModel, Field, field_validator

from Agents.agent_orquestrador import orquestrador_agent

load_dotenv()


def _normalizar_url(valor: str) -> str:
    if not valor:
        return ""
    bruto = valor.strip()
    try:
        parsed = ast.literal_eval(bruto)
        if isinstance(parsed, (list, tuple)) and len(parsed) == 1 and isinstance(parsed[0], str):
            return parsed[0].strip().rstrip("/")
    except Exception:
        pass
    return bruto.strip().strip('"').strip("'").rstrip("/")

WAHA_URL     = _normalizar_url(os.getenv("WAHA_URL", "http://docker.host.internal:3000"))
WAHA_API_KEY = os.getenv("WAHA_API_KEY", "")
WAHA_SESSION = os.getenv("WAHA_SESSION", "default")


app = FastAPI(title="TIVS — Triagem Inteligente e Visual de Saúde")

session_service = InMemorySessionService()
runner = Runner(
    agent=orquestrador_agent,
    app_name="tivs_app",
    session_service=session_service,
)


class SymptomsInput(BaseModel):
    """Entrada de triagem por sintomas textuais."""
    symptoms: str = Field(..., min_length=10, max_length=2000)
    patient_age: Optional[int] = Field(None, ge=0, le=120)
    patient_gender: Optional[str] = Field(None, pattern=r"^(masculino|feminino|outro)$")

    @field_validator("symptoms")
    @classmethod
    def symptoms_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Sintomas não podem ser vazios.")
        return v.strip()


class ImageInput(BaseModel):
    """Entrada de triagem por imagem de lesão ou picada."""
    image_base64: str = Field(..., description="Imagem codificada em Base64.")
    image_type: str = Field(default="image/jpeg", pattern=r"^image/(jpeg|png|webp)$")
    body_part: Optional[str] = Field(None, max_length=100)
    symptoms: Optional[str] = Field(None, max_length=1000)

    @field_validator("image_base64")
    @classmethod
    def validate_base64(cls, v: str) -> str:
        try:
            decoded = base64.b64decode(v, validate=True)
            if len(decoded) > 10 * 1024 * 1024:
                raise ValueError("Imagem excede o limite de 10 MB.")
        except Exception as exc:
            raise ValueError(f"Imagem Base64 inválida: {exc}") from exc
        return v

def _extrair_mensagem(dados: Dict[str, Any]) -> Tuple[str, str, bool]:
    payload  = dados.get("payload", dados)
    texto    = payload.get("body") or payload.get("text") or payload.get("message") or ""
    chat_id  = payload.get("chatId") or payload.get("from") or payload.get("chat_id") or ""
    from_me  = payload.get("fromMe") or payload.get("from_me") or False
    if isinstance(from_me, str):
        from_me = from_me.lower() == "true"
    return texto, chat_id, bool(from_me)


def _enviar_whatsapp(chat_id: str, texto: str) -> None:
    if not WAHA_URL:
        raise RuntimeError("WAHA_URL não configurado.")
    url      = f"{WAHA_URL}/api/sendText"
    payload  = {"session": WAHA_SESSION, "chatId": chat_id, "text": texto}
    headers  = {"X-Api-Key": WAHA_API_KEY} if WAHA_API_KEY else {}
    resposta = requests.post(url, json=payload, headers=headers, timeout=30)
    resposta.raise_for_status()


async def _chamar_orquestrador(mensagem: str, user_id: str) -> str:
    """Cria/reutiliza sessão ADK e executa o orquestrador."""
    session_id = f"sessao_{user_id}"

    try:
        await session_service.create_session(
            app_name="tivs_app",
            user_id=user_id,
            session_id=session_id,
        )
    except Exception:
        pass  # Sessão já existente — reutiliza

    message = types.Content(role="user", parts=[types.Part(text=mensagem)])

    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=message,
    ):
        if event.is_final_response():
            content = getattr(event, "content", None)
            if content and getattr(content, "parts", None):
                for part in content.parts:
                    texto = getattr(part, "text", None)
                    if texto:
                        return texto
            return "Não foi possível obter resposta do agente."

    return "Não foi possível obter resposta do agente."

@app.get("/health")
async def health():
    return {"status": "ok", "service": "TIVS API"}


@app.post("/triage/symptoms")
async def triage_symptoms(body: SymptomsInput):
    """Triagem via sintomas textuais — consumido pelo Streamlit."""
    contexto = f"Sintomas: {body.symptoms}"
    if body.patient_age:
        contexto += f"\nIdade: {body.patient_age} anos"
    if body.patient_gender:
        contexto += f"\nGênero: {body.patient_gender}"

    try:
        resposta = await _chamar_orquestrador(contexto, user_id="streamlit_user")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {"resultado": resposta}


@app.post("/triage/image")
async def triage_image(body: ImageInput):
    """Triagem via imagem de lesão — consumido pelo Streamlit."""
    contexto = "tipo_entrada: image"
    if body.symptoms:
        contexto += f"\nSintomas adicionais: {body.symptoms}"
    if body.body_part:
        contexto += f"\nRegião afetada: {body.body_part}"
    contexto += f"\nimage_base64: {body.image_base64[:50]}..."  # log seguro

    try:
        resposta = await _chamar_orquestrador(contexto, user_id="streamlit_user")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {"resultado": resposta}


@app.post("/webhook")
async def webhook(request: Request):
    """Webhook consumido pelo n8n após receber mensagem do WAHA."""
    dados = await request.json()

    event = dados.get("event", "")
    if event and event != "message":
        print(f"[WEBHOOK] Ignorando evento: {event}")
        return {"status": "ok"}

    payload = dados.get("payload", dados)

    if payload.get("hasMedia") and not payload.get("body"):
        print("[WEBHOOK] Ignorando mídia sem texto.")
        return {"status": "ok"}

    texto, chat_id, from_me = _extrair_mensagem(dados)

    if not texto or not chat_id:
        raise HTTPException(status_code=400, detail="Payload inválido.")

    try:
        resposta = await _chamar_orquestrador(texto, user_id=chat_id)
        print(f"[WEBHOOK] Resposta gerada: {resposta}")
    except Exception as exc:
        print(f"[WEBHOOK] Erro ao chamar orquestrador: {exc}")
        return {"status": "error", "detail": "Erro interno ao processar a mensagem."}

    try:
        _enviar_whatsapp(chat_id, resposta)
    except Exception as exc:
        print(f"[WEBHOOK] Erro ao enviar WhatsApp: {exc}")
        return {"status": "error", "detail": "Falha no envio da resposta."}

    return {"status": "ok"}