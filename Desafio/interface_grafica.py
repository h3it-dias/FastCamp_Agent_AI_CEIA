import streamlit as st
import asyncio
import nest_asyncio
from agents import execute, criar_runner

nest_asyncio.apply()

st.set_page_config(page_title="Assistente Médico", layout="centered")
st.title("Assistente Médico Inteligente")

if "runner" not in st.session_state:
    st.session_state.runner = criar_runner()

if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

for msg in st.session_state.mensagens:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("Descreva seus sintomas..."):
    st.session_state.mensagens.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    resposta = asyncio.run(
        execute({"sintomas": prompt}, st.session_state.runner)
    )

    resposta_texto = resposta["resposta_medica"]
    st.session_state.mensagens.append({"role": "assistant", "content": resposta_texto})
    with st.chat_message("assistant"):
        st.write(resposta_texto)