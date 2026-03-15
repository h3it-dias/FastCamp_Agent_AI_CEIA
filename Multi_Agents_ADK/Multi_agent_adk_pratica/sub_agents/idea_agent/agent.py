from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext

def pegar_ideias_computacao(topic: str) -> str:

    ideias = {
        "algoritmos": ["ordenação", "busca binária", "grafos", "programação dinâmica"],
        "estruturas de dados": ["listas", "árvores", "filas", "pilhas", "hash maps"],
        "redes": ["TCP/IP", "HTTP", "DNS", "firewalls", "VPNs"],
        "banco de dados": ["SQL", "NoSQL", "indexação", "transações", "normalização"],
    }

    topic_lower = topic.lower()

    for key in ideias:
        if key in topic_lower:
            lista = ideias[key]
            return f"Ideias sobre {key}: {', '.join(lista)}"

    return f"Não encontrei ideias específicas para {topic}, mas você pode falar sobre conceitos básicos, aplicações práticas e erros comuns."
    

idea_agent = Agent(
    name="idea_agent",
    model="gemini-2.0-flash",
    description="Um agente que é responsável por achar ideais de computação.",
    instruction="""
        Você gera ideias criativas de vídeos sobre computação.

        Sempre use a ferramenta `pegar_ideias_computacao`
        para obter ideias base sobre o tópico.

        Depois transforme essas ideias em sugestões de vídeos.

        Formato da resposta:

        Ideia de vídeo sobre <TEMA>

        Título:
        ...

        Hook inicial:
        ...

        Conceito do vídeo:
        ...
    """,
    tools=[pegar_ideias_computacao],
)
