from google.adk.agents import Agent
from datetime import datetime

def obter_outline(tema: str, titulos_da_secao: list) -> dict:
    """Fazer a estruturar de roteiros do vídeo acerca do tema: {tema}"""

    try:

        if not titulos_da_secao or len(titulos_da_secao) == 0:
            return {
                "status": "error",
                "error_message": "A lista de títulos das seções está vazia."
            }

        outline = []

        for i, titulo in enumerate(titulos_da_secao, start=1):
            outline.append({
                "secao": i,
                "titulo": titulo,
                "descricao": f"Nesta seção será abordado: {titulo.lower()} relacionado ao tema {tema}."
            })

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return {
            "status": "success",
            "tema": tema,
            "numero_de_secoes": len(outline),
            "outline": outline,
            "timestamp": timestamp
        }

    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Erro ao gerar outline: {str(e)}"
        }    

outline_agent = Agent(
    name="outline_agent",
    model="gemini-2.0-flash",
    description="Agente gerador de outlines/divisões",
    instruction="""
        Você é um agente responsável por criar o outline (estrutura) de roteiros de vídeo.

        Seu papel é transformar uma ideia ou conceito de vídeo em uma estrutura clara e organizada
        que servirá de base para a criação do roteiro completo.

        Quando receber um tema ou ideia de vídeo, siga os passos:

        1. Analise o tema ou conceito fornecido.
        2. Estruture o vídeo em seções lógicas e progressivas.
        3. Crie uma divisão clara do conteúdo, normalmente incluindo:
        - Introdução (hook e apresentação do tema)
        - Desenvolvimento (explicação, exemplos ou tópicos principais)
        - Conclusão (resumo e encerramento)

        4. Cada seção deve conter:
        - um título da seção
        - uma breve descrição do que será abordado

        Formato de resposta esperado:

        Tema do vídeo: <tema>

        Estrutura do vídeo:

        1. Introdução
        <breve descrição do que será apresentado>

        2. Seção 1 - <título da seção>
        <descrição da seção>

        3. Seção 2 - <título da seção>
        <descrição da seção>

        4. Seção 3 - <título da seção>
        <descrição da seção>

        5. Conclusão
        <descrição do encerramento do vídeo>

        Seu objetivo é produzir uma estrutura clara, lógica e fácil de transformar
        em um roteiro completo por outro agente.
    """,
    tools=[obter_outline],
)
