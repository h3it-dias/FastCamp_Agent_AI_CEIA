import streamlit as st
import requests

st.set_page_config(page_title="Planejador de estudos")
st.title("Carderninho")
assunto = st.text_input("Qual o assunto que desejas estudar?", placeholder="Ex.: Agentes inteligentes")
dias = st.number_input("Quantos dias você quer para apreender esse assunto?")
horas_dia = st.number_input("Quantas horas por dia você tem para esse estudo?")

if st.button("Planejar estudos"):
    if not all([assunto, dias, horas_dia]):
        st.warning("Você não preencheu todas as informações")

    else:
        informacoes = {
            "assunto": assunto,
            "dias": dias,
            "horas_dia": horas_dia
        }
        resposta = requests.post("http://localhost:8000/run", json=informacoes)

        if resposta.ok:
            dados = resposta.json()
            st.subheader("TOPICOS")
            st.markdown(dados["topicos"])
            st.subheader("CRONOGRAMA")
            st.markdown(dados["cronograma"])
            st.subheader("EXERCICIOS")
            st.markdown(dados["exercicios"])
        else:
            st.error("Falha no planejamento dos estudo, tente novamente")