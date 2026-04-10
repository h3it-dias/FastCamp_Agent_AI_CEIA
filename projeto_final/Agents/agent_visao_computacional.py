import asyncio
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from google.adk.models.lite_llm import LiteLlm

agent_visao_computacional = Agent(
    name="agent_visao_computacional",
    model=LiteLlm("mistral/mistral-medium-latest"),
    description="Agente especializado em interpretar imagens médicas de pele, picadas e manchas.",
    instruction="""
    Sua tarefa é analisar rigorosamente a imagem fornecida pelo usuário.
    1. Identifique padrões visuais (cor, forma, presença de edema ou necrose).
    2. Se houver suspeita de picada, descreva se há pontos de inoculação.
    3. Traduza a imagem em uma DESCRIÇÃO TEXTUAL TÉCNICA para que o Agente de Busca possa pesquisar no banco de dados.
    4. Classifique o nível de alerta visual (Verde, Amarelo, Vermelho).
    
    IMPORTANTE: Não dê um diagnóstico definitivo. Use termos como 'compatível com' ou 'sugestivo de'.
    """
)