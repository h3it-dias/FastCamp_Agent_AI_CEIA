# TIVS — Triagem Inteligente e Visual de Saúde

> Sistema multiagente de triagem médica com análise de sintomas e imagens de lesões, integrando LLMs, busca semântica vetorial e interface conversacional via WhatsApp e web.

---

## O Problema

Em regiões com acesso limitado a serviços de saúde, pacientes frequentemente não sabem avaliar a gravidade de sintomas como picadas de insetos, manchas na pele ou reações alérgicas. A falta de uma triagem inicial rápida pode levar à demora no atendimento adequado ou ao uso desnecessário de pronto-socorros.

O TIVS resolve isso oferecendo uma **triagem automatizada de primeiro nível**, disponível 24h, que:

- Recebe a descrição textual dos sintomas do paciente.
- Aceita imagens de lesões ou picadas para análise visual.
- Consulta uma base de conhecimento médica indexada vetorialmente.
- Retorna uma avaliação preliminar com nível de urgência e recomendação de conduta.
- Está acessível via interface web (Streamlit) ou WhatsApp (WAHA + n8n).

> O TIVS **não substitui** consulta médica. Seu objetivo é orientar o paciente sobre a urgência do caso e o encaminhamento mais adequado.

---

## Arquitetura

```
Usuário (Streamlit ou WhatsApp)
        │
        ▼
   API FastAPI (api.py)
        │
        ▼
 Agente Orquestrador  ←──────────────────────────────┐
        │                                             │
        ├──► Agente de Visão Computacional            │
        │    (Pixtral 12B via Mistral API)            │
        │    Analisa imagem → descrição técnica       │
        │                                             │
        ├──► Agente de Busca                          │
        │    (Mistral Small + Qdrant)                 │
        │    Busca semântica em base médica           │
        │                                             │
        └──► Agente de Diagnóstico                    │
             (Mistral Small)                          │
             Retorna condição + urgência + conduta ───┘
```

---

## Tecnologias Utilizadas

| Camada | Tecnologia |
|---|---|
| Orquestração de agentes | [Google ADK](https://google.github.io/adk-docs/) |
| LLM principal | [Mistral Medium](https://mistral.ai/) via LiteLLM |
| Análise de imagem | [Pixtral 12B](https://mistral.ai/news/pixtral-12b/) via Mistral API |
| Embeddings | `mistral-embed` (1024 dimensões) |
| Banco vetorial | [Qdrant](https://qdrant.tech/) (cloud) |
| API backend | [FastAPI](https://fastapi.tiangolo.com/) + Uvicorn |
| Interface web | [Streamlit](https://streamlit.io/) |
| Integração WhatsApp | [WAHA](https://waha.devlike.pro/) + [n8n](https://n8n.io/) |
| Gerenciamento de env | [python-dotenv](https://pypi.org/project/python-dotenv/) |

---

## Pré-requisitos

- Python 3.10+
- Conta na [Mistral AI](https://console.mistral.ai/) com acesso à API
- Cluster no [Qdrant Cloud](https://cloud.qdrant.io/) (plano gratuito disponível)
- (Opcional) WAHA + n8n para integração WhatsApp

---

## Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/tivs.git
cd tivs
```

### 2. Crie e ative um ambiente virtual

```bash
python -m venv .venv
source .venv/bin/activate      # Linux/macOS
.venv\Scripts\activate         # Windows
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

<details>
<summary>Dependências principais (requirements.txt)</summary>

```
google-adk
litellm
mistralai
qdrant-client
fastapi
uvicorn
streamlit
python-dotenv
pydantic
requests
```

</details>

### 4. Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
# Mistral AI
MISTRAL_API_KEY=sua_chave_aqui

# Qdrant
QDRANT_URL=https://seu-cluster.qdrant.io
QDRANT_API_KEY=sua_chave_aqui
```

### 5. Indexe a base de conhecimento médica

Coloque seu arquivo de texto médico como `train.txt` na raiz do projeto e execute:

```bash
python embedding.py
```

Isso criará a coleção `abstracts` no Qdrant e indexará o conteúdo em chunks de 200 palavras.

---

## Como Executar

### Interface Web (Streamlit)

Abra dois terminais:

**Terminal 1 — API:**
```bash
uvicorn api:app --reload
```

**Terminal 2 — Interface:**
```bash
streamlit run interface.py
```

Acesse `http://localhost:8501` no navegador.

### Somente a API (modo headless / integração n8n)

```bash
uvicorn api:app --host 0.0.0.0 --port 8000
```

A documentação interativa estará disponível em `http://localhost:8000/docs`.

---

## Endpoints da API

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/health` | Verifica se a API está online |
| `POST` | `/triage/symptoms` | Triagem por sintomas textuais |
| `POST` | `/triage/image` | Triagem por imagem de lesão |
| `POST` | `/webhook` | Webhook para integração com n8n/WAHA |

### Exemplo — triagem por sintomas

```bash
curl -X POST http://localhost:8000/triage/symptoms \
  -H "Content-Type: application/json" \
  -d '{
    "symptoms": "Febre alta há 2 dias, manchas vermelhas no braço que coçam bastante",
    "patient_age": 34,
    "patient_gender": "masculino"
  }'
```

```json
{
  "resultado": "Condição compatível com reação alérgica ou picada de inseto. Nível de urgência: Amarelo. Recomenda-se consulta médica em até 24h. Monitore evolução das manchas e temperatura."
}
```

---

## Estrutura do Projeto

```
tivs/
├── Agents/
│   ├── __init__.py
│   ├── agent_orquestrador.py     # Agente raiz — coordena os demais
│   ├── agent_visao_computacional.py  # Analisa imagens médicas (Pixtral)
│   ├── agent_busca.py            # Busca semântica no Qdrant
│   └── agent_diagnostico.py     # Gera diagnóstico preliminar
├── api.py                        # API FastAPI — endpoints de triagem
├── embedding.py                  # Geração de embeddings e indexação Qdrant
├── interface.py                  # Interface Streamlit
├── train.txt                     # Base de conhecimento médica (não versionada)
├── .env                          # Variáveis de ambiente (não versionado)
├── .env.example                  # Template do .env
├── requirements.txt
└── README.md
```

---

## Fluxo de Triagem

```
1. Usuário descreve sintomas (+ imagem opcional)
        │
        ▼
2. [Se imagem] Agente de Visão analisa e gera descrição técnica
        │
        ▼
3. Agente de Busca consulta base vetorial (Qdrant)
   → retorna os 5 trechos mais relevantes
        │
        ▼
4. Agente de Diagnóstico analisa contexto e sintomas
   → retorna: condição provável | nível de urgência | recomendação
        │
        ▼
5. Resposta entregue ao usuário via Streamlit ou WhatsApp
```

## Integração WhatsApp (opcional)

O fluxo usa WAHA como gateway WhatsApp e n8n como orquestrador de eventos:

```
WhatsApp → WAHA → n8n → POST /webhook → TIVS API → resposta → WAHA → WhatsApp
```

Configure o webhook do n8n para apontar para `http://seu-servidor:8000/webhook`.

---

## Limitações Conhecidas

- O agente de visão computacional (`Pixtral`) requer que a imagem seja enviada como `Part` multimodal — a integração completa com o pipeline ADK está em desenvolvimento.
- A sessão de usuário na API usa `user_id` fixo para requisições Streamlit; em produção, use um UUID por sessão.
- O sistema não armazena histórico de triagens entre sessões (memória in-memory).

---

## Aviso Legal

> Este sistema é um MVP experimental para fins educacionais e de pesquisa. **Não deve ser utilizado como substituto de diagnóstico médico profissional.** Em caso de emergência, acione o SAMU (192) ou dirija-se ao pronto-socorro mais próximo.

---
