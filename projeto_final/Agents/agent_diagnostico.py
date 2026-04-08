import asyncio
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from google.adk.models.lite_llm import LiteLlm

agent_diagnostico = Agent(
    name="agent_diagnostico",
    model="gemini/gemini-1.5-pro",
    instruction=(
        "Analise os textos médicos e retorne possíveis condições, "
        "nível de urgência e recomendação."
    )
)