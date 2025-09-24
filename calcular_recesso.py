import streamlit as st
from datetime import datetime, timedelta

# 📅 Verifica se é dia útil (segunda a sexta)
def is_weekday(date: datetime) -> bool:
    return date.weekday() < 5

# 🎯 Retorna recessos por tipo e ano
def get_recess_days(tipo: str, year: int):
    if tipo == 'PUC':
        return [datetime(year, 11, 20), datetime(year, 11, 21)]
    elif tipo == 'FUNDASP':
        return [datetime(year, 10, 10), datetime(year, 11, 20)]
    return []

# 🔁 Recessos entre anos
def get_all_recess_days(tipo: str, start_year: int, end_year: int):
    days = []
    for year in range(start_year, end_year + 1):
        days.extend(get_recess_days(tipo, year))
    return days

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

# 🔍 Busca a data fixa de início da compensação por vínculo + jornada
def get_fixed_start_date(tipo: str, jornada: str, year: int) -> datetime:
    data_str = datas_inicio[tipo][jornada] + f"/{year}"
    return datetime.strptime(data_str, "%d/%m/%Y")

# 📉 Conta dias úteis perdidos nas férias
def count_lost_workdays(ferias_inicio: datetime, ferias_fim: datetime, tipo: str, jornada: str) -> int:
    comp_start = get_fixed_start_date(tipo, jornada, ferias_inicio.year)
    
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

# 🔍 Calcula a data real de início da compensação voltando os dias úteis perdidos
def find_start_date(ferias_fim: datetime, lost_days: int, tipo: str) -> datetime:
    """
    Volta 'lost_days' dias úteis a partir do fim das férias,
    considerando finais de semana e recessos.
    """
    recess_days = set(get_all_recess_days(tipo, ferias_fim.year, ferias_fim.year))
    current = ferias_fim
    dias_para_voltar = lost_days

    while dias_para_voltar > 0:
        current -= timedelta(days=1)
        if is_weekday(current) and current not in recess_days:
            dias_para_voltar -= 1

    return current

# 🧱 Interface Streamlit
st.set_page_config(page_title="Calculadora de Compensação", page_icon="🗓️")
st.title("📅 Calculadora de Início de Compensação")

tipo = st.selectbox("Tipo de vínculo", ["PUC", "FUNDASP"])
jornada = st.selectbox("Jornada diária", ["08h", "06h", "05h", "04h"])

inicio_str = st.text_input("Início das férias (dd/mm/aaaa)")
fim_str = st.text_input("Fim das férias (dd/mm/aaaa)")

if st.button("Calcular"):
    try:
        ferias_inicio = datetime.strptime(inicio_str, "%d/%m/%Y")
        ferias_fim = datetime.strptime(fim_str, "%d/%m/%Y")

        if ferias_fim < ferias_inicio:
            st.error("❌ A data final não pode ser anterior à data inicial.")
        else:
            dias_perdidos = count_lost_workdays(ferias_inicio, ferias_fim, tipo, jornada)

            if dias_perdidos == 0:
                st.info("🎉 As férias não coincidem com o período de compensação. Nenhum dia útil será perdido.")
            else:
                data_inicio = find_start_date(ferias_fim, dias_perdidos, tipo)
                st.success(
                    f"✅ O funcionário perderá **{dias_perdidos} dias úteis** durante as férias.\n\n"
                    f"🕒 Deverá iniciar a compensação em: **{data_inicio.strftime('%d/%m/%Y')}**"
                )
    except ValueError:
        st.error("⚠️ Digite as datas corretamente no formato dd/mm/aaaa.")
