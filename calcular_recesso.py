import streamlit as st
from datetime import datetime, timedelta

# 📅 Verifica se é dia útil (segunda a sexta)
def is_weekday(date: datetime) -> bool:
    return date.weekday() < 5

# 🎯 Retorna recessos por tipo e ano
def get_recess_days(tipo: str, year: int):
    if tipo == 'PUC':
        # PUC: 20/11 e 21/11
        return [datetime(year, 11, 20), datetime(year, 11, 21)]
    elif tipo == 'FUNDASP':
        # FUNDASP: 10/10 e 20/11
        return [datetime(year, 10, 10), datetime(year, 11, 20)]
    return []

# 🔁 Recessos entre anos (caso férias cruzem ano)
def get_all_recess_days(tipo: str, start_year: int, end_year: int):
    days = []
    for year in range(start_year, end_year + 1):
        days.extend(get_recess_days(tipo, year))
    return days

# 📉 Conta dias úteis perdidos nas férias
def count_lost_workdays(ferias_inicio: datetime, ferias_fim: datetime, tipo: str) -> int:
    comp_start = datetime(ferias_inicio.year, 10, 15) if tipo == 'PUC' else datetime(ferias_inicio.year, 10, 16)

    if ferias_fim < comp_start:
        return 0

    contagem_inicio = max(ferias_inicio, comp_start)
    recess_days = set(get_all_recess_days(tipo, contagem_inicio.year, ferias_fim.year))

    lost_days = 0
    current = contagem_inicio
    while current <= ferias_fim:
        if is_weekday(current) and current not in recess_days:
            lost_days += 1
        current += timedelta(days=1)
    return lost_days

# 📌 Datas fixas de início da compensação por vínculo e jornada
datas_inicio = {
    "PUC": {
        "08h": "15/10",
        "06h": "31/10",
        "05h": "10/11",
        "04h": "18/11",
    },
    "FUNDASP": {
        "08h": "16/10",
        "06h": "03/11",
        "05h": "11/11",
        "04h": "19/11",
    }
}

# 🔍 Busca a data de início da compensação pelo vínculo + jornada
def get_start_date(tipo: str, jornada: str, year: int) -> datetime:
    data_str = datas_inicio[tipo][jornada] + f"/{year}"
    return datetime.strptime(data_str, "%d/%m/%Y")

# 🧱 Interface Web com Streamlit
st.set_page_config(page_title="Calculadora de Compensação", page_icon="🗓️")
st.title("📅 Calculadora de Início de Compensação")

# Seleção do tipo de vínculo
tipo = st.selectbox("Tipo de vínculo", ["PUC", "FUNDASP"])

# Seleção da jornada diária
jornada = st.selectbox("Jornada diária", ["08h", "06h", "05h", "04h"])

# 🔧 Datas no padrão brasileiro (texto)
inicio_str = st.text_input("Início das férias (dd/mm/aaaa)")
fim_str = st.text_input("Fim das férias (dd/mm/aaaa)")

if st.button("Calcular"):
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
                data_inicio = get_start_date(tipo, jornada, ferias_inicio.year)
                st.success(
                    f"✅ O funcionário perderá **{dias_perdidos} dias úteis** durante as férias.\n\n"
                    f"🕒 Jornada diária: **{jornada}**\n"
                    f"📅 Deverá iniciar a compensação em: **{data_inicio.strftime('%d/%m/%Y')}**"
                )
    except ValueError:
        st.error("⚠️ Digite as datas corretamente no formato dd/mm/aaaa.")
