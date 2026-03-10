from google.adk.agents import Agent

from .sub_agents.idea_agent.agent import idea_agent
from .sub_agents.outline_agent.agent import outline_agent
from .sub_agents.script_agent.agent import script_agent


root_agent = Agent(
    name="manager",
    model="gemini-2.5-flash-lite",
    description="Manager agent",
    instruction="""
        Você é um agente gerente responsável por supervisionar e delegar tarefas aos seus sub-agentes registrados.
        Sempre use seu melhor julgamento para delegar a tarefa ao sub-agente apropriado.

        Sub-agentes disponíveis:
        - idea_agent: responsável por gerar ideias criativas
        - outline_agent: responsável por criar estruturas e outlines
        - script_agent: responsável por escrever roteiros completos

        Regras de delegação:
        - Se o usuário pedir ideias → delegue para idea_agent
        - Se o usuário pedir estrutura ou outline → delegue para outline_agent
        - Se o usuário pedir roteiro completo → delegue para script_agent

        Se o pedido não se enquadrar em nenhuma categoria, responda diretamente.
    """,
    sub_agents=[idea_agent, outline_agent, script_agent]
)
