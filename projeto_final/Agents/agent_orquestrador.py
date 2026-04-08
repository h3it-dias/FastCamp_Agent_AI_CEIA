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
    model="gemini/gemini-1.5-pro",
    instruction=(
        "Chame o agente de busca e depois o de diagnóstico."
    ),
    sub_agents=[agent_busca, agent_diagnostico, agent_visao_computacional]
)