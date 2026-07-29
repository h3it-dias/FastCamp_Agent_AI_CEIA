import asyncio
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from google.adk.models.lite_llm import LiteLlm

from embedding import *

# IDs fixos: sessão única compartilhada por todos os usuários da interface
USER_ID = "user_orquestrador"
SESSION_ID = "session_orquestrador"

# Evita chamadas concorrentes ao Qdrant/Mistral quando várias mensagens chegam ao mesmo tempo
lock = asyncio.Lock()

# Tool usada pelo agent_busca: transforma a pergunta em embedding e busca os 5 trechos mais próximos no Qdrant
async def buscar_informacoes(pergunta: str) -> dict:
    async with lock:
        loop = asyncio.get_event_loop()

        cliente = get_cliente()
        vetor = gerar_embedding(pergunta)

        # query_points é síncrono; roda em thread separada para não travar o event loop
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

# Sub-agente 1: só busca contexto no banco vetorial, não diagnostica
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

# Sub-agente 2: recebe o contexto do agent_busca e gera a triagem final
diagnostico_agent = Agent(
    name="diagnostico_agent",
    model=LiteLlm("mistral/mistral-small-latest"),
    instruction=(
        "Analise os textos médicos e retorne possíveis condições, "
        "nível de urgência e recomendação."
    )
)

# Agente raiz: apenas orquestra a ordem busca -> diagnóstico
orquestrador_agent = Agent(
    name="orquestrador_agent",
    model=LiteLlm("mistral/mistral-medium-latest"),
    instruction=(
        "Chame o agente de busca e depois o de diagnóstico."
    ),
    sub_agents=[busca_agent, diagnostico_agent]
)

# Runner "global" (não usado pela interface, que cria o seu próprio via criar_runner)
memoria_sessao = InMemorySessionService()
runner = Runner(
    agent=orquestrador_agent,
    app_name="orquestrador_app",
    session_service=memoria_sessao
)

# Cada sessão do Streamlit tem seu próprio runner/histórico em memória
def criar_runner():
    memoria_sessao = InMemorySessionService()
    return Runner(
        agent=orquestrador_agent,
        app_name="orquestrador_app",
        session_service=memoria_sessao
    )

# Envia os sintomas ao orquestrador e devolve a resposta final do agente de diagnóstico
async def execute(request, runner):

    # cria a sessão se ainda não existir (idempotente na prática, pois USER_ID/SESSION_ID são fixos)
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

    # percorre os eventos do agente até a resposta final (ignora eventos intermediários dos sub-agentes)
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=message
    ):
        if event.is_final_response():
            return {
                "resposta_medica": event.content.parts[0].text
            }

