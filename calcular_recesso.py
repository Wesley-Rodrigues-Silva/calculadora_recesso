import streamlit as st
from datetime import datetime, timedelta

# ---------------------------
# Helpers
# ---------------------------
def is_weekday(date: datetime) -> bool:
    return date.weekday() < 5  # Mon-Fri

def get_recess_days(tipo: str, year: int):
    """Recessos por tipo/ano — atualize se precisar adicionar feriados extras."""
    if tipo == 'PUC':
        return [datetime(year, 11, 20), datetime(year, 11, 21)]
    elif tipo == 'FUNDASP':
        return [datetime(year, 10, 10), datetime(year, 11, 20)]
    return []

def get_all_recess_days(tipo: str, start_year: int, end_year: int):
    days = []
    for y in range(start_year, end_year + 1):
        days.extend(get_recess_days(tipo, y))
    return set(days)

# ---------------------------
# Datas fixas por vínculo/jornada
# ---------------------------
datas_inicio = {
    "PUC": {"08h": "15/10", "06h": "31/10", "05h": "10/11", "04h": "18/11"},
    "FUNDASP": {"08h": "16/10", "06h": "03/11", "05h": "11/11", "04h": "19/11"},
}

def get_fixed_start_date(tipo: str, jornada: str, year: int) -> datetime:
    s = datas_inicio[tipo][jornada] + f"/{year}"
    return datetime.strptime(s, "%d/%m/%Y")

def first_business_on_or_after(date: datetime, recess_days: set) -> datetime:
    cur = date
    while not (is_weekday(cur) and cur not in recess_days):
        cur += timedelta(days=1)
    return cur

def list_lost_dates(contagem_inicio: datetime, ferias_fim: datetime, recess_days: set):
    """Retorna a lista de dias úteis perdidos (datetime objects)."""
    lost = []
    cur = contagem_inicio
    while cur <= ferias_fim:
        if is_weekday(cur) and cur not in recess_days:
            lost.append(cur)
        cur += timedelta(days=1)
    return lost

def backdate_business_days(start: datetime, days: int, recess_days: set):
    """
    Volta 'days' dias úteis a partir de 'start' (start deve ser um dia útil).
    Retorna (date_result, passos) onde passos é lista de dias úteis usados no recuo (ordem cronológica reversa).
    """
    current = start
    remaining = days
    passos = []
    while remaining > 0:
        current -= timedelta(days=1)
        if is_weekday(current) and current not in recess_days:
            passos.append(current)
            remaining -= 1
    return current, passos

# ---------------------------
# Streamlit UI
# ---------------------------
st.set_page_config(page_title="Calculadora de Compensação", page_icon="🗓️")
st.title("📅 Calculadora de Início de Compensação (por jornada)")

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
            # 1) data fixa de início da compensação (por jornada)
            comp_start = get_fixed_start_date(tipo, jornada, ferias_inicio.year)

            # 2) período a ser contado: começa em max(ferias_inicio, comp_start)
            contagem_inicio_raw = max(ferias_inicio, comp_start)

            # 3) recessos para os anos envolvidos
            recess_days = get_all_recess_days(tipo, contagem_inicio_raw.year, ferias_fim.year)

            # 4) achar o primeiro dia útil que realmente entra na contagem (não contar fins de semana/recessos)
            contagem_inicio = first_business_on_or_after(contagem_inicio_raw, recess_days)

            # 5) lista de dias perdidos e total
            lost_dates = list_lost_dates(contagem_inicio, ferias_fim, recess_days)
            dias_perdidos = len(lost_dates)

            if dias_perdidos == 0:
                st.info("🎉 As férias não coincidem com o período de compensação. Nenhum dia útil será perdido.")
            else:
                # 6) volta 'dias_perdidos' dias úteis a partir do PRIMEIRO dia útil contado
                inicio_compensacao, passos_recuo = backdate_business_days(contagem_inicio, dias_perdidos, recess_days)

                st.success(
                    f"✅ O funcionário perderá **{dias_perdidos} dias úteis** durante as férias.\n\n"
                    f"🕒 Deverá iniciar a compensação em: **{inicio_compensacao.strftime('%d/%m/%Y')}**"
                )

                with st.expander("Mostrar detalhes do cálculo"):
                    st.write(f"Data fixa de início da compensação (jornada): **{comp_start.strftime('%d/%m/%Y')}**")
                    st.write(f"Contagem iniciou em (raw): **{contagem_inicio_raw.strftime('%d/%m/%Y')}**")
                    st.write(f"Primeiro dia útil contado dentro das férias: **{contagem_inicio.strftime('%d/%m/%Y')}**")
                    st.write("Dias contabilizados como perdidos (lista):")
                    st.write([d.strftime("%d/%m/%Y") for d in lost_dates])
                    st.write("Passo a passo do recuo (dias úteis que foram subtraídos):")
                    st.write([d.strftime("%d/%m/%Y") for d in passos_recuo])
    except ValueError:
        st.error("⚠️ Digite as datas corretamente no formato dd/mm/aaaa.")
