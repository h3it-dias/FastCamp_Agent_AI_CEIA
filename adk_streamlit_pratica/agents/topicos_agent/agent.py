from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import json

topicos_agent = Agent(
    name="topicos_agent",
    model=LiteLlm("mistral/mistral-small-latest"),
    description="Define os principais tópicos de estudo para um determinado objetivo de aprendizagem.",
    instruction=(
        "Dado um assunto de estudo, número de horas de estudo por dia e prazo disponível em dias, "
        "sugira 4-6 tópicos principais que devem ser estudados para atingir esse objetivo. "
        "Para cada tópico, forneça um nome e uma breve descrição do que será aprendido. "
        "Responda em português. Seja claro, objetivo e bem organizado."
    )
)

memoria_sessao = InMemorySessionService()

runner = Runner(
    agent=topicos_agent,
    app_name="topicos_app",
    session_service=memoria_sessao
)
USER_ID = "user_topicos"
SESSAO_ID = "sessao_topicos"

async def execute(request):
    await memoria_sessao.create_session(
        app_name="topicos_app",
        user_id=USER_ID,
        session_id=SESSAO_ID
    )

    prompt_estruturado = (
        f"O usuário quer aprender {request['assunto']} em {request['dias']} dias "
        f"e possui {request['horas_dia']} disponivel para estudar por dia. "
        f"Sugira 4-6 tópicos principais de estudo para atingir esse objetivo. "
        f"Responda em JSON usando a chave 'topicos' com uma lista de objetos contendo "
        f'nome e descrição do tópico.'
    )
    message = types.Content(role="user", parts=[types.Part(text=prompt_estruturado)])
    async for event in runner.run_async(user_id=USER_ID, session_id=SESSAO_ID, new_message=message):
        if event.is_final_response():
            texto_resposta = event.content.parts[0].text
            try:
                parsed = json.loads(texto_resposta)
                if "topicos" in parsed and isinstance(parsed["topicos"], list):
                    return {"topicos": parsed["topicos"]}
                else:
                    return {"topicos": texto_resposta}

            except json.JSONDecodeError as e:
                return {"topicos": texto_resposta}