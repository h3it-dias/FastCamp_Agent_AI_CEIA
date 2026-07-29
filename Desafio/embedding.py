from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from mistralai import Mistral
from dotenv import load_dotenv
import os

load_dotenv()

NOME_COLECAO = "abstracts"
BATCH_SIZE = 50  # quantidade de chunks enviados por vez ao Qdrant

# Cliente usado apenas na indexação (execução via __main__)
cliente = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
    timeout=300,
    port=443,
    https=True
)

model_mistral = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

# Gera o vetor de embedding (1024 dimensões) de um texto via API da Mistral
def gerar_embedding(texto: str) -> list:
    return model_mistral.embeddings.create(model="mistral-embed", inputs=[texto]).data[0].embedding

# Cliente usado em tempo de consulta (chamado por agents.py a cada busca)
def get_cliente():
    return QdrantClient(
        url=os.getenv("QDRANT_URL"),
        api_key=os.getenv("QDRANT_API_KEY"),
        timeout=300,
        check_compatibility=False
    )

# Script de indexação: lê train.txt, divide em chunks e popula a coleção no Qdrant
if __name__ == "__main__":
    # cria a coleção só se ela ainda não existir
    if not cliente.collection_exists(NOME_COLECAO):
        cliente.create_collection(
            collection_name=NOME_COLECAO,
            vectors_config=VectorParams(size=1024, distance=Distance.COSINE)
        )

    # divide o texto base em blocos de 200 palavras
    chunks = [
        " ".join(open("train.txt", encoding="utf-8").read().split()[i:i+200])
        for i in range(0, len(open("train.txt", encoding="utf-8").read().split()), 200)
    ]
    print(f"Chunks criados: {len(chunks)}")

    # gera o embedding de cada chunk e envia ao Qdrant em lotes de BATCH_SIZE
    points = []
    for i, chunk in enumerate(chunks):
        try:
            points.append(PointStruct(id=i, vector=gerar_embedding(chunk), payload={"texto": chunk}))
            print(f"Chunk {i+1}/{len(chunks)} processado")

            if len(points) >= BATCH_SIZE:
                cliente.upsert(collection_name=NOME_COLECAO, points=points)
                print(f"  Batch enviado!")
                points = []
        except Exception as e:
            print(f"Erro no chunk {i}: {e}")

    # envia o restante que não completou um batch inteiro
    if points:
        cliente.upsert(collection_name=NOME_COLECAO, points=points)

    print("Indexação concluída!")