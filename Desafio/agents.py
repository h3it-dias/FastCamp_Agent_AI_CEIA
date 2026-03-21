import asyncio
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from google.adk.models.lite_llm import LiteLlm

from embedding import *

USER_ID = "user_orquestrador"
SESSION_ID = "session_orquestrador"

lock = asyncio.Lock()

async def buscar_informacoes(pergunta: str) -> dict:
    async with lock:
        loop = asyncio.get_event_loop()

        cliente = get_cliente()
        vetor = gerar_embedding(pergunta)

        resultados = await loop.run_in_executor(
            None,
            lambda: cliente.query_points(
                collection_name=NOME_COLECAO,
                query=vetor,
                limit=5
            ).points
        )

        await asyncio.sleep(0.3)

        contexto = [
            {
                "texto": i.payload.get("texto", ""),
                "score": i.score
            }
            for i in resultados
        ]

        return {"contexto": contexto}

busca_agent = Agent(
    name="agent_busca",
    model=LiteLlm("mistral/mistral-small-latest"),
    description="Busca informações médicas no banco vetorial.",
    instruction=(
        "Você DEVE usar a ferramenta buscar_informacoes. "
        "Retorne apenas os textos mais relevantes."
    ),
    tools=[buscar_informacoes]
)

diagnostico_agent = Agent(
    name="diagnostico_agent",
    model=LiteLlm("mistral/mistral-small-latest"),
    instruction=(
        "Analise os textos médicos e retorne possíveis condições, "
        "nível de urgência e recomendação."
    )
)

orquestrador_agent = Agent(
    name="orquestrador_agent",
    model=LiteLlm("mistral/mistral-medium-latest"),
    instruction=(
        "Chame o agente de busca e depois o de diagnóstico."
    ),
    sub_agents=[busca_agent, diagnostico_agent]
)

memoria_sessao = InMemorySessionService()
runner = Runner(
    agent=orquestrador_agent,
    app_name="orquestrador_app",
    session_service=memoria_sessao
)

def criar_runner():
    memoria_sessao = InMemorySessionService()
    return Runner(
        agent=orquestrador_agent,
        app_name="orquestrador_app",
        session_service=memoria_sessao
    )

async def execute(request, runner):

    await runner.session_service.create_session(
        app_name="orquestrador_app",
        user_id=USER_ID,
        session_id=SESSION_ID
    )

    prompt = f"Paciente relata: {request['sintomas']}"

    message = types.Content(
        role="user",
        parts=[types.Part(text=prompt)]
    )

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=message
    ):
        if event.is_final_response():
            return {
                "resposta_medica": event.content.parts[0].text
            }

