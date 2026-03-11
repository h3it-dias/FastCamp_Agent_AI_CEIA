from common.a2a_client import chamar_agent
EXERCICIOS_URL = "http://localhost:8001/run"
CRONOGRAMA_URL = "http://localhost:8002/run"
TOPICOS_URL = "http://localhost:8003/run"

async def run(informacoes):
    print("Informações:", informacoes)

    topicos = await chamar_agent(TOPICOS_URL, informacoes)

    cronograma = await chamar_agent(CRONOGRAMA_URL, {
        "topicos": topicos.get("topicos"),
        "dias": informacoes["dias"],
        "horas_dia": informacoes["horas_dia"]
    })

    exercicios = await chamar_agent(EXERCICIOS_URL, {
        "topicos": topicos.get("topicos")
    })

    print("topicos:", topicos)
    print("cronograma:", cronograma)
    print("exercicios:", exercicios)

    topicos = topicos if isinstance(topicos, dict) else {}
    cronograma = cronograma if isinstance(cronograma, dict) else {}
    exercicios = exercicios if isinstance(exercicios, dict) else {}

    return {
        "topicos": topicos.get("topicos", "Nenhum tópico retornado."),
        "cronograma": cronograma.get("cronograma", "Nenhum cronograma retornado."),
        "exercicios": exercicios.get("exercicios", "Nenhum exercício retornado.")
    }