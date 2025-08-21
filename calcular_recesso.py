import streamlit as st
from datetime import datetime, timedelta

def is_weekday(date):
    return date.weekday() < 5

def precisa_compensar(ferias_inicio, ferias_fim, tipo):
    comp_start = datetime(ferias_inicio.year, 10, 15) if tipo == 'PUC' else datetime(ferias_inicio.year, 10, 16)
    comp_end = datetime(ferias_inicio.year, 12, 23)
    return ferias_fim >= comp_start and ferias_inicio <= comp_end

def dias_uteis_perdidos(ferias_inicio, ferias_fim, tipo):
    comp_start = datetime(ferias_inicio.year, 10, 15) if tipo == 'PUC' else datetime(ferias_inicio.year, 10, 16)
    comp_end = datetime(ferias_inicio.year, 12, 23)

    lost_days = 0
    current = comp_start
    while current <= comp_end:
        if ferias_inicio <= current <= ferias_fim and is_weekday(current):
            lost_days += 1
        current += timedelta(days=1)
    return lost_days

def calcular_inicio_compensacao(inicio_ferias, dias_perdidos):
    dias_contados = 0
    data = inicio_ferias - timedelta(days=1)

    while dias_contados < dias_perdidos:
        if is_weekday(data):
            dias_contados += 1
        data -= timedelta(days=1)

    return data + timedelta(days=1)

# Interface Streamlit
st.set_page_config(page_title="Cálculo do Início da Compensação", page_icon="📅")
st.title("📅 Cálculo do Início da Compensação")

tipo_vinculo = st.selectbox("Tipo de vínculo", ["PUC", "Fundação"])
inicio_str = st.text_input("Início das férias (dd/mm/aaaa)", "20/09/2025")
fim_str = st.text_input("Fim das férias (dd/mm/aaaa)", "19/10/2025")

if st.button("Calcular"):
    try:
        inicio_ferias = datetime.strptime(inicio_str, "%d/%m/%Y")
        fim_ferias = datetime.strptime(fim_str, "%d/%m/%Y")

        if precisa_compensar(inicio_ferias, fim_ferias, tipo_vinculo):
            dias_perdidos = dias_uteis_perdidos(inicio_ferias, fim_ferias, tipo_vinculo)
            compensacao_inicio = calcular_inicio_compensacao(inicio_ferias, dias_perdidos)

            st.info(f"📅 Deverá iniciar a compensação em: {compensacao_inicio.strftime('%d/%m/%Y')}")
            st.error(f"📆 Dias úteis da compensação perdidos: {dias_perdidos}")
        else:
            st.success("🎉 As férias não coincidem com o período de compensação. Nenhuma compensação é necessária.")

    except ValueError:
        st.error("❌ Datas inválidas. Use o formato dd/mm/aaaa.")

