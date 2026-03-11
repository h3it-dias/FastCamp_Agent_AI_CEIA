from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import json

cronograma_agent = Agent(
    name="cronograma_agent",
    model=LiteLlm("mistral/mistral-small-latest"),
    description="Cria um cronograma de estudos baseado nos tópicos e no tempo disponível.",
    instruction=(
        "Dada uma lista de tópicos de estudo, o prazo total em dias e o tempo diário disponível, "
        "crie um cronograma simples distribuindo os tópicos ao longo dos dias ou semanas. "
        "Para cada período, indique qual tópico deve ser estudado e o tempo aproximado dedicado a ele. "
        "Responda em português. Mantenha o cronograma claro, conciso e bem organizado."
    )
)

memoria_sessao = InMemorySessionService()

runner = Runner(
    agent=cronograma_agent,
    app_name="cronograma_app",
    session_service=memoria_sessao
)
USER_ID = "user_cronograma"
SESSAO_ID = "sessao_cronograma"

async def execute(request):
    await memoria_sessao.create_session(
        app_name="cronograma_app",
        user_id=USER_ID,
        session_id=SESSAO_ID
    )

    prompt_estruturado = (
        f"O usuário possui {request['dias']} dias para estudar "
        f"e {request['horas_dia']} horas disponíveis por dia.\n\n"
        f"Os tópicos que precisam ser estudados são:\n"
        f"{request['topicos']}\n\n"
        f"Crie um cronograma distribuindo esses tópicos ao longo dos dias "
        f"de forma equilibrada.\n\n"
        f"Responda em JSON usando a chave 'cronograma' com uma lista de objetos contendo "
        f"'dia', 'topico' e 'horas'."
    )

    message = types.Content(role="user", parts=[types.Part(text=prompt_estruturado)])
    async for event in runner.run_async(user_id=USER_ID, session_id=SESSAO_ID, new_message=message):
        if event.is_final_response():
            texto_resposta = event.content.parts[0].text
            try:
                parsed = json.loads(texto_resposta)
                if "cronograma" in parsed and isinstance(parsed["cronograma"], list):
                    return {"cronograma": parsed["cronograma"]}
                else:
                    return {"cronograma": texto_resposta}

            except json.JSONDecodeError as e:
                return {"cronograma": texto_resposta}