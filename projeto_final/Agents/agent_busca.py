import asyncio
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from google.adk.models.lite_llm import LiteLlm
from embedding import *


lock = asyncio.Lock()

async def buscar_informacoes(query: str) -> dict():
    async with lock:
        loop = asyncio.get_event_loop()

        cliente = get_cliente()
        vetor = gerar_embedding(query)

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


agent_busca = Agent(
    name="agent_busca",
    model="gemini/gemini-1.5-pro",
    description="Busca informações médicas no banco vetorial.",
    instruction=(
        "Você DEVE usar a ferramenta buscar_informacoes. "
        "Retorne apenas os textos mais relevantes."
    ),
    tools=[buscar_informacoes]
)