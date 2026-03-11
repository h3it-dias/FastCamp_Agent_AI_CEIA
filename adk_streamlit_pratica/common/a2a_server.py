from fastapi import FastAPI
import uvicorn

def criar_servidor(agent):
    app = FastAPI()
    @app.post("/run")
    async def run(informacoes: dict):
        return await agent.execute(informacoes)
    return app