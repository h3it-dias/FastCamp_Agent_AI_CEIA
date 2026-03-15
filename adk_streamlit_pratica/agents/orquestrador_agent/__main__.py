from common.a2a_server import criar_servidor
from .task_manager import run

app = criar_servidor(agent=type("Agent", (), {"execute": run}))
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)