from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

orquestrador_agent = Agent(
    name="orquestrador_agent",
    model=LiteLlm("mistral/mistral-medium-latest"),
    ddescription="Coordena o planejamento de estudos chamando agentes responsáveis por tópicos, cronograma e exercícios.",
    instruction=
        "Você é o agente orquestrador responsável por planejar os estudos do usuário. "
        "Com base no assunto, prazo em dias e horas disponíveis por dia, você deve chamar "
        "agentes especializados para gerar os tópicos de estudo, criar um cronograma e "
        "sugerir exercícios práticos. Depois de coletar as respostas desses agentes, "
        "retorne um plano de estudo final organizado."    
)

memoria_sessao = InMemorySessionService()
runner = Runner(
    agent=orquestrador_agent,
    app_name="orquestrador_app",
    session_service=memoria_sessao
)
USER_ID = "user_orquestrador"
SESSION_ID = "session_orquestrador"

async def execute(request):
    await memoria_sessao.create_session(
        app_name="orquestrador_app",
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    prompt_estruturado = (
        f"Crie um plano de estudos para {request['assunto']} ao longo de {request['dias']} dias "
        f"com {request['horas_dia']} horas disponíveis por dia. "
        f"Chame os agentes de tópicos, cronograma e exercícios para gerar os resultados."
    )
    message = types.Content(role="user", parts=[types.Part(text=prompt_estruturado)])
    async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=message):
        if event.is_final_response():
            return {"plano_estudo": event.content.parts[0].text}
