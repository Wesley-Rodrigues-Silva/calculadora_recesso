import streamlit as st
from datetime import datetime, timedelta
import re

# 📅 Verifica se é dia útil (segunda a sexta)
def is_weekday(date):
    return date.weekday() < 5

# 🎯 Retorna recessos por tipo e ano
def get_recess_days(tipo, year):
    if tipo == 'PUC':
        return [datetime(year, 11, 20), datetime(year, 11, 21)]
    elif tipo == 'FUNDASP':
        return [datetime(year, 11, 20)]
    return []

# 🔁 Recessos entre anos (caso férias cruzem ano)
def get_all_recess_days(tipo, start_year, end_year):
    days = []
    for year in range(start_year, end_year + 1):
        days.extend(get_recess_days(tipo, year))
    return days

# 📉 Conta dias úteis perdidos nas férias
def count_lost_workdays(ferias_inicio, ferias_fim, tipo):
    comp_start = datetime(ferias_inicio.year, 10, 15) if tipo == 'PUC' else datetime(ferias_inicio.year, 10, 16)

    # Se as férias terminam antes do início da compensação, não há dias perdidos
    if ferias_fim < comp_start:
        return 0

    recess_days = get_all_recess_days(tipo, ferias_inicio.year, ferias_fim.year)
    lost_days = 0
    current = ferias_inicio
    while current <= ferias_fim:
        if is_weekday(current) and current not in recess_days:
            lost_days += 1
        current += timedelta(days=1)
    return lost_days

# 🔍 Encontra data de início da compensação
def find_start_date(lost_days, tipo):
    today_year = datetime.today().year
    comp_start = datetime(today_year, 10, 15) if tipo == 'PUC' else datetime(today_year, 10, 16)
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

# 🧠 Função para validar e corrigir datas digitadas
def formatar_data(data_str):
    data_str = re.sub(r"[^\d]", "", data_str)  # Remove tudo que não for número
    if len(data_str) == 8:
        return f"{data_str[:2]}/{data_str[2:4]}/{data_str[4:]}"
    return data_str

if st.button("Calcular"):
    inicio_str = formatar_data(inicio_str)
    fim_str = formatar_data(fim_str)

    try:
        ferias_inicio = datetime.strptime(inicio_str, "%d/%m/%Y")
        ferias_fim = datetime.strptime(fim_str, "%d/%m/%Y")

        if ferias_fim < ferias_inicio:
            st.error("❌ A data final não pode ser anterior à data inicial.")
        else:
            dias_perdidos = count_lost_workdays(ferias_inicio, ferias_fim, tipo)

            if dias_perdidos == 0:
                st.info("🎉 As férias não coincidem com o período de compensação. Nenhum dia útil será perdido.")
            else:
                data_inicio = find_start_date(dias_perdidos, tipo)
                st.success(f"""
                ✅ O funcionário perderá **{dias_perdidos} dias úteis** durante as férias.

                🕒 Deverá iniciar a compensação em: **{data_inicio.strftime('%d/%m/%Y')}**
                """)
    except Exception as e:
        st.error("⚠️ Verifique se as datas estão completas e no formato correto (dd/mm/aaaa).")
