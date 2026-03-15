import httpx

async def chamar_agent(url, informacoes):
    async with httpx.AsyncClient() as client:
        resposta = await client.post(url, json=informacoes, timeout=60.0)
        resposta.raise_for_status()
        return resposta.json()