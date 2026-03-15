from datetime import datetime

from google.adk.agents import Agent
from typing import List, Dict

def estruturar_roteiro(outline: List[Dict], estrutura_roteiro: List) -> dict:
    """Retorna um roteiro estruturado do outline contendo as informações estrutura_roteiro"""

    roteiro_final = []

    for i, val in enumerate(outline, start=1):
        bloco_secao = {
                "secao": i,
                "titulo": val.get("titulo", f"Seção {i}"),
                "conteudo": {}
            }

        for est in estrutura_roteiro:
            bloco_secao["conteudo"][est] = f"{est} relacionado à seção '{val.get('titulo', '')}'."

        roteiro_final.append(bloco_secao)

    return {
        "roteiro": roteiro_final
    }
   
script_agent = Agent(
    name="script_agent",
    model="gemini-2.0-flash",
    description="Agente responsável por escrever o roteiro completo de um vídeo a partir de um outline estruturado.",
    instruction="""
        Você é um agente roteirista especializado em criar roteiros completos para vídeos.

        Seu papel é transformar um outline de vídeo em um roteiro narrado, claro e envolvente, pronto para gravação.

        Processo que você deve seguir:

        1. Sempre que receber um outline, primeiro utilize a ferramenta `estruturar_roteiro`.

        2. Passe para a ferramenta:

        * `outline`: o outline recebido
        * `estrutura_roteiro`: ["narracao", "exemplo", "visual"]

        3. Após receber a estrutura retornada pela ferramenta, expanda cada seção e escreva o roteiro completo.

        Instruções de escrita:

        * Use linguagem clara e natural, como se estivesse narrando um vídeo.
        * Comece com uma introdução que tenha um hook para prender a atenção.
        * Desenvolva cada seção explicando o tema.
        * Finalize com uma conclusão resumindo o conteúdo.

        Formato da resposta:

        Tema do vídeo: <tema>

        Roteiro:

        [INTRODUÇÃO]
        <texto da introdução>

        [SEÇÃO - título]
        <roteiro da seção>

        [CONCLUSÃO]
        <encerramento do vídeo>

        Observação:

        O roteiro deve ser objetivo.

        Limites:
        - máximo de 500 palavras
        - máximo de 2 parágrafos por seção
        - frases curtas e claras
    """,
    tools=[estruturar_roteiro],
)
