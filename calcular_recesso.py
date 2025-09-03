import streamlit as st
from datetime import datetime, timedelta

# 📅 Verifica se é dia útil (segunda a sexta)
def is_weekday(date: datetime) -> bool:
    return date.weekday() < 5

# 🎯 Retorna recessos por tipo e ano
def get_recess_days(tipo: str, year: int):
    if tipo == 'PUC':
        # Exemplo: 20 e 21/11 (ajuste se necessário)
        return [datetime(year, 11, 20), datetime(year, 11, 21)]
    elif tipo == 'FUNDASP':
        return [datetime(year, 11, 20)]
    return []

# 🔁 Recessos entre anos (caso férias cruzem ano)
def get_all_recess_days(tipo: str, start_year: int, end_year: int):
    days = []
    for year in range(start_year, end_year + 1):
        days.extend(get_recess_days(tipo, year))
    return days

# 📉 Conta dias úteis perdidos nas férias (somente dentro do período de compensação)
def count_lost_workdays(ferias_inicio: datetime, ferias_fim: datetime, tipo: str) -> int:
    # Início da compensação: PUC=16/10, FUNDASP=15/10 (do ano de referência das férias)
    comp_start = datetime(ferias_inicio.year, 10, 16) if tipo == 'PUC' else datetime(ferias_inicio.year, 10, 15)

    # Se as férias terminam antes do início da compensação, não há dias perdidos
    if ferias_fim < comp_start:
        return 0

    # Só contamos os dias que caem dentro da janela de compensação (a partir do comp_start)
    contagem_inicio = max(ferias_inicio, comp_start)

    recess_days = set(get_all_recess_days(tipo, contagem_inicio.year, ferias_fim.year))
    lost_days = 0
    current = contagem_inicio
    while current <= ferias_fim:
        if is_weekday(current) and current not in recess_days:
            lost_days += 1
        current += timedelta(days=1)
    return lost_days

# 🔍 Encontra data de início da compensação retrocedendo dias úteis perdidos
def find_start_date(lost_days: int, tipo: str, year: int) -> datetime:
    # Início da compensação no ano de referência
    comp_start = datetime(year, 10, 16) if tipo == 'PUC' else datetime(year, 10, 15)

    # Se perdeu 0 dias, não precisa compensar; se perdeu 1 dia, começa no próprio comp_start
    if lost_days <= 1:
        return comp_start

    recess_days = set(get_recess_days(tipo, comp_start.year))
    current = comp_start
    steps_to_go_back = lost_days - 1  # inclui o dia de comp_start na contagem

    while steps_to_go_back > 0:
        current -= timedelta(days=1)
        if is_weekday(current) and current not in recess_days:
            steps_to_go_back -= 1
    return current

# 🧱 Interface Web com Streamlit
st.set_page_config(page_title="Calculadora de Compensação", page_icon="🗓️")
st.title("📅 Calculadora de Início de Compensação")

tipo = st.selectbox("Tipo de vínculo", ["PUC", "FUNDASP"])
inicio = st.date_input("Início das férias")
fim = st.date_input("Fim das férias")

if st.button("Calcular"):
    ferias_inicio = datetime.combine(inicio, datetime.min.time())
    ferias_fim = datetime.combine(fim, datetime.min.time())

    if ferias_fim < ferias_inicio:
        st.error("❌ A data final não pode ser anterior à data inicial.")
    else:
        dias_perdidos = count_lost_workdays(ferias_inicio, ferias_fim, tipo)

        if dias_perdidos == 0:
            st.info("🎉 As férias não coincidem com o período de compensação. Nenhum dia útil será perdido.")
        else:
            data_inicio = find_start_date(dias_perdidos, tipo, ferias_inicio.year)
            st.success(
                f"✅ O funcionário perderá **{dias_perdidos} dias úteis** durante as férias.\n\n"
                f"🕒 Deverá iniciar a compensação em: **{data_inicio.strftime('%d/%m/%Y')}**"
            )

