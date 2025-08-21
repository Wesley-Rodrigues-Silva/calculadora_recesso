import streamlit as st
from datetime import datetime, timedelta

def is_weekday(date):
    return date.weekday() < 5  # Segunda a sexta

def get_recess_days(tipo, year):
    if tipo == 'PUC':
        return [datetime(year, 11, 20), datetime(year, 11, 21)]
    elif tipo == 'FUNDASP':
        return [datetime(year, 11, 20)]
    return []

def count_lost_workdays(ferias_inicio, ferias_fim, tipo):
    recess_days = get_recess_days(tipo, ferias_inicio.year)
    lost_days = 0
    current = ferias_inicio
    while current <= ferias_fim:
        if is_weekday(current) and current not in recess_days:
            lost_days += 1
        current += timedelta(days=1)
    return lost_days

def find_start_date(lost_days, tipo):
    # Define a data de início da compensação conforme o tipo
    if tipo == 'PUC':
        comp_start = datetime(datetime.today().year, 10, 15)
    elif tipo == 'FUNDASP':
        comp_start = datetime(datetime.today().year, 10, 16)
    else:
        comp_start = datetime(datetime.today().year, 10, 15)

    recess_days = get_recess_days(tipo, comp_start.year)
    current = comp_start
    count = 0
    while count < lost_days:
        current -= timedelta(days=1)
        if is_weekday(current) and current not in recess_days:
            count += 1
    return current

# 🧱 Interface Web com Streamlit
st.set_page_config(page_title="Calculadora de Compensação", page_icon="🗓️")
st.title("📅 Calculadora de Início de Compensação")

tipo = st.selectbox("Tipo de vínculo", ["PUC", "FUNDASP"])
inicio_str = st.text_input("Início das férias (dd/mm/aaaa)")
fim_str = st.text_input("Fim das férias (dd/mm/aaaa)")

if st.button("Calcular"):
    try:
        ferias_inicio = datetime.strptime(inicio_str, "%d/%m/%Y")
        ferias_fim = datetime.strptime(fim_str, "%d/%m/%Y")
        if ferias_fim < ferias_inicio:
            st.error("A data final não pode ser anterior à data inicial.")
        else:
            dias_perdidos = count_lost_workdays(ferias_inicio, ferias_fim, tipo)
            data_inicio = find_start_date(dias_perdidos, tipo)
            st.success(f"""
            ✅ O funcionário perderá **{dias_perdidos} dias úteis** durante as férias.

            🕒 Deverá iniciar a compensação em: **{data_inicio.strftime('%d/%m/%Y')}**
            """)
    except Exception as e:
        st.error(f"Verifique os dados inseridos. Erro: {e}")
