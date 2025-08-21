import streamlit as st
from datetime import datetime, timedelta

# Função para verificar se é dia útil (segunda a sexta)
def is_weekday(date):
    return date.weekday() < 5  # 0 = segunda, 4 = sexta

# Função para obter os dias de recesso
def get_all_recess_days(tipo, ano_inicio, ano_fim):
    recess_days = set()
    for year in range(ano_inicio, ano_fim + 1):
        if tipo == 'PUC':
            start = datetime(year, 10, 15)
            end = datetime(year, 10, 31)
        else:
            start = datetime(year, 10, 16)
            end = datetime(year, 10, 31)
        current = start
        while current <= end:
            recess_days.add(current)
            current += timedelta(days=1)
    return recess_days

# Função principal para contar dias úteis perdidos
def count_lost_workdays(ferias_inicio, ferias_fim, tipo):
    comp_start = datetime(ferias_inicio.year, 10, 15) if tipo == 'PUC' else datetime(ferias_inicio.year, 10, 16)

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

# Interface Streamlit
st.title("🗓️ Cálculo de Dias Úteis Perdidos nas Férias")

tipo_vinculo = st.selectbox("Tipo de vínculo", ["PUC", "Outro"])

inicio_str = st.text_input("Início das férias (dd/mm/aaaa)", "20/09/2025")
fim_str = st.text_input("Fim das férias (dd/mm/aaaa)", "15/10/2025")

if st.button("Calcular"):
    try:
        inicio_ferias = datetime.strptime(inicio_str, "%d/%m/%Y")
        fim_ferias = datetime.strptime(fim_str, "%d/%m/%Y")

        dias_perdidos = count_lost_workdays(inicio_ferias, fim_ferias, tipo_vinculo)

        if dias_perdidos == 0:
            st.success("🎉 As férias não coincidem com o período de compensação. Nenhum dia útil será perdido.")
        else:
            st.warning(f"⚠️ O funcionário perderá {dias_perdidos} dias úteis durante as férias.")
            compensacao_inicio = inicio_ferias - timedelta(days=1)
            st.info(f"📅 Deverá iniciar a compensação em: {compensacao_inicio.strftime('%d/%m/%Y')}")

    except ValueError:
        st.error("❌ Datas inválidas. Use o formato dd/mm/aaaa.")

