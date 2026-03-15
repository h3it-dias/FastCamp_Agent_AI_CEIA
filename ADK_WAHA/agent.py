from fastapi import FastAPI
from pydantic import BaseModel
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.models import LiteLlm
from google.genai import types
import requests
import asyncio
from datetime import datetime

app = FastAPI()

def enviar_lembrete(nome_contato: str, data_hora: str, descricao: str) -> str:
    """Envia um lembrete para um compromisso individual"""
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")
    return f"Lembrete ({agora}): {nome_contato}, você tem um compromisso '{descricao}' agendado para {data_hora}."

def registrar_compromisso(nome_contato: str, data_hora: str, descricao: str) -> str:
    """Registra um compromisso individual e retorna mensagem de confirmação"""

    return f"Compromisso registrado: '{descricao}' com {nome_contato} em {data_hora}."

def objetivo_conversa() -> dict:
    """Retorna as opções/objetivos de intereção"""

    opcoes = {
        "descrição1": "Marcar uma reunião sobre assuntos da faculdade",
        "descrição2": "Marcar uma reunião sobre assuntos do projeto do CEIA",
        "descrição3": "Conversa casual entre colegas",
        "descrição4": "Conversa familiar"
    }

    return opcoes

lembrete_agent = Agent(
    name="lembrete_agent",
    model="mistral/mistral-small-latest",
    description="Agente responsável por enviar lembretes de compromisso",
    instruction=
        "Você é um agente de lembretes, responsável por enviar lembretes individuais de compromissos via WhatsApp. "
        "Sempre verifique os compromissos agendados e envie lembretes no horário adequado usando a ferramenta 'enviar_lembrete'. "
        "Nunca interaja com grupos, apenas mensagens diretas de pessoas.",
    tools=[enviar_lembrete]
)

agendamento_agent = Agent(
    name="agendamento_agent",
    model="mistral/mistral-small-latest",
    description="Agente responsável por marcar compromissos e reuniões na conversa",
    instruction=
        "Você é um agente de agendamento, responsável por marcar compromissos individuais no WhatsApp. "
        "Sempre confirme com o contato a data e hora antes de agendar. "
        "Se necessário, sugira horários disponíveis e registre o compromisso usando a ferramenta 'registrar_compromisso'. "
        "Nunca interaja com grupos, apenas mensagens diretas de pessoas.",
    tools=[registrar_compromisso]
)

gerente_agent = Agent(
    name="gerente_agent",
    model=LiteLlm("mistral/mistral-small-latest"),
    description="Agente responsável por gerenciar a conversa de whatsapp de um restaurante",
    instruction=
        "Você é o agente gerente de um sistema de WhatsApp pessoal. "
        "Só deve interagir com mensagens de pessoas, nunca grupos. "
        "Assim que receber uma mensagem, use 'objetivo_conversa' para mostrar as opções de interação"
        "Você tem sub-agents: 'agendamento_agent' para marcar compromissos, "
        "'lembrete_agent' para enviar lembretes",
    sub_agents=[agendamento_agent, lembrete_agent, ],
    tools=[objetivo_conversa]
)

session_service = InMemorySessionService()
runner = Runner(
    agent=gerente_agent,
    app_name="gerente_app",
    session_service=session_service
)

class Valid_Entrada(BaseModel):
    mensagem: str
    chat_id: str

@app.post("/run")
async def run(entrada: Valid_Entrada):
    if "@g.us" in entrada.chat_id:
        return {"resposta": "Mensagens de grupo são ignoradas."}

    id_sessao = entrada.chat_id.replace("@", "_").replace(".", "_")
    message = types.Content(role="user", parts=[types.Part(text=entrada.mensagem)])
    
    resposta_final = "Desculpe, não consegui processar sua solicitação."

    try:
        await session_service.create_session(app_name="gerente_app", user_id=id_sessao, session_id=id_sessao)

        async for event in runner.run_async(user_id=id_sessao, session_id=id_sessao, new_message=message):
            if event.is_final_response():
                if event.content and event.content.parts:
                    resposta_final = event.content.parts[0].text
        
        return {
            "chatId": entrada.chat_id,
            "text": resposta_final,
            "session": "default" 
        }
    
    except Exception as e:
        return {
            "chatId": entrada.chat_id,
            "text": "Ocorreu um erro interno.",
            "session": "default",
            "error_log": str(e)
        }

