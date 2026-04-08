import streamlit as st
import requests
import base64

API_BASE_URL = "http://localhost:8000"
ENDPOINT_SYMPTOMS = f"{API_BASE_URL}/triage/symptoms"
ENDPOINT_IMAGE = f"{API_BASE_URL}/triage/image"

st.set_page_config(
    page_title="TIVS - Triagem Inteligente", 
    layout="centered"
)

st.title("TIVS - Autoatendimento")
st.markdown("Bem-vindo à Triagem Inteligente e Visual de Saúde. Descreva o que está sentindo e, se necessário, envie uma imagem da lesão.")
st.divider()

with st.form("form_triagem"):
    st.subheader("Seus Dados")
    col1, col2 = st.columns(2)
    with col1:
        idade = st.number_input("Idade (opcional)", min_value=0, max_value=120, value=None, step=1)
    with col2:
        genero = st.selectbox("Gênero (opcional)", options=["", "masculino", "feminino", "outro"])
    
    st.subheader("Relato Médico")
    texto_sintomas = st.text_area(
        "Descreva seus sintomas (Mínimo 10 caracteres):", 
        placeholder="Ex: Febre alta há 2 dias e manchas vermelhas na pele que coçam bastante...",
        height=150
    )
    
    parte_corpo = st.text_input("Região afetada (opcional, caso envie imagem):", placeholder="Ex: Braço direito, pescoço...")
    
    imagem_enviada = st.file_uploader(
        "Anexe uma foto da lesão ou picada (Opcional):", 
        type=["jpg", "jpeg", "png", "webp"]
    )
    
    botao_analisar = st.form_submit_button("Iniciar Triagem ")

if botao_analisar:
    if not texto_sintomas or len(texto_sintomas.strip()) < 10:
        st.warning("A descrição dos sintomas precisa ter pelo menos 10 caracteres.")
    else:
        genero_formatado = genero if genero != "" else None
        
        with st.spinner("Os agentes TIVS estão analisando seu caso..."):
            
            try:
                if imagem_enviada is not None:
                    st.image(imagem_enviada, caption="Imagem sob análise", width=300)

                    bytes_imagem = imagem_enviada.getvalue()
                    base64_imagem = base64.b64encode(bytes_imagem).decode("utf-8")
                    tipo_imagem = f"image/{imagem_enviada.name.split('.')[-1].lower()}"
                    if tipo_imagem == "image/jpg": 
                        tipo_imagem = "image/jpeg"

                    payload_imagem = {
                        "image_base64": base64_imagem,
                        "image_type": tipo_imagem,
                        "body_part": parte_corpo if parte_corpo else None,
                        "symptoms": texto_sintomas
                    }

                    resposta = requests.post(ENDPOINT_IMAGE, json=payload_imagem)

                else:
                    payload_sintomas = {
                        "symptoms": texto_sintomas,
                        "patient_age": idade,
                        "patient_gender": genero_formatado
                    }

                    resposta = requests.post(ENDPOINT_SYMPTOMS, json=payload_sintomas)

                if resposta.status_code == 200:
                    st.success("Triagem concluída!")
                    resultado = resposta.json().get("resultado", "Sem resposta dos agentes.")
                    
                    st.markdown("### Parecer Clínico dos Agentes")
                    st.info(resultado)
                else:
                    st.error(f"Erro na API (Status {resposta.status_code}): {resposta.text}")
                    
            except requests.exceptions.ConnectionError:
                st.error("Não foi possível conectar ao `api.py`. Verifique se o Uvicorn/FastAPI está rodando na porta 8000.")
            except Exception as e:
                st.error(f"Ocorreu um erro inesperado: {e}")