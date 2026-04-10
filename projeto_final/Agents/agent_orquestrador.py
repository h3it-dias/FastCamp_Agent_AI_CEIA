import asyncio
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from google.adk.models.lite_llm import LiteLlm
from .agent_visao_computacional import agent_visao_computacional
from .agent_busca import agent_busca
from .agent_diagnostico import agent_diagnostico


orquestrador_agent = Agent(
    name="orquestrador_agent",
    model=LiteLlm("mistral/mistral-medium-latest"),
    description=(
        "Agente mestre responsável por coordenar a triagem médica. "
        "Ele identifica se a entrada contém imagens ou texto e direciona para os especialistas."
    ),
    instruction=(
        "Você é o Orquestrador do sistema TIVS. Sua função é coordenar os sub-agentes nesta ordem: "
        "1. Se a entrada contiver 'image_base64', chame IMEDIATAMENTE o 'agent_visao_computacional' para transcrever a imagem em texto clínico. "
        "2. Com o texto clínico (ou sintomas digitais), chame o 'agent_busca' para obter contexto científico no banco de dados. "
        "3. Por fim, passe os sintomas e o contexto médico para o 'agent_diagnostico' gerar a triagem final. "
        "NUNCA tente diagnosticar sozinho. Sempre utilize os sub-agentes."
    ),
    sub_agents=[agent_busca, agent_diagnostico, agent_visao_computacional]
)