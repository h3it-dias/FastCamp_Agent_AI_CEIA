from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import json

exercicios_agent = Agent(
    name="exercicios_agent",
    model=LiteLlm("mistral/mistral-small-latest"),
    description="Gera exercícios práticos para reforçar o aprendizado de um tópico.",
    instruction=(
        "Dado um tópico de estudo, gere 3-4 exercícios práticos para ajudar o aluno a treinar o conteúdo. "
        "Cada exercício deve conter uma breve descrição do problema ou tarefa proposta. "
        "Se apropriado, inclua um pequeno exemplo ou dica. "
        "Responda em português. Seja claro e mantenha os exercícios curtos e objetivos."
    )
)

memoria_sessao = InMemorySessionService()

runner = Runner(
    agent=exercicios_agent,
    app_name="exercicios_app",
    session_service=memoria_sessao
)
USER_ID = "user_exercicios"
SESSAO_ID = "sessao_exercicios"

async def execute(request):
    await memoria_sessao.create_session(
        app_name="exercicios_app",
        user_id=USER_ID,
        session_id=SESSAO_ID
    )

    prompt_estruturado = (
        f"Os tópicos que o estudante está aprendendo são:\n"
        f"{request['topicos']}\n\n"
        f"Para cada tópico, gere 1 ou 2 exercícios práticos "
        f"para ajudar na fixação do conteúdo.\n\n"
        f"Responda em JSON usando a chave 'exercicios' "
        f"com uma lista de objetos contendo 'topico' e 'exercicio'."
    )

    message = types.Content(role="user", parts=[types.Part(text=prompt_estruturado)])
    async for event in runner.run_async(user_id=USER_ID, session_id=SESSAO_ID, new_message=message):
        if event.is_final_response():
            texto_resposta = event.content.parts[0].text
            try:
                parsed = json.loads(texto_resposta)
                if "exercicios" in parsed and isinstance(parsed["exercicios"], list):
                    return {"exercicios": parsed["exercicios"]}
                else:
                    return {"exercicios": texto_resposta}

            except json.JSONDecodeError as e:
                return {"exercicios": texto_resposta}