from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from mistralai import Mistral
from dotenv import load_dotenv
import os

load_dotenv()

NOME_COLECAO = "abstracts"
BATCH_SIZE = 50

cliente = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
    timeout=300,
    port=443,
    https=True
)

model_mistral = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

def gerar_embedding(texto: str) -> list:
    return model_mistral.embeddings.create(model="mistral-embed", inputs=[texto]).data[0].embedding

def get_cliente():
    return QdrantClient(
        url=os.getenv("QDRANT_URL"),
        api_key=os.getenv("QDRANT_API_KEY"),
        timeout=300,
        check_compatibility=False
    )

if __name__ == "__main__":
    if not cliente.collection_exists(NOME_COLECAO):
        cliente.create_collection(
            collection_name=NOME_COLECAO,
            vectors_config=VectorParams(size=1024, distance=Distance.COSINE)
        )

    chunks = [
        " ".join(open("train.txt", encoding="utf-8").read().split()[i:i+200])
        for i in range(0, len(open("train.txt", encoding="utf-8").read().split()), 200)
    ]
    print(f"Chunks criados: {len(chunks)}")

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

    if points:
        cliente.upsert(collection_name=NOME_COLECAO, points=points)

    print("Indexação concluída!")