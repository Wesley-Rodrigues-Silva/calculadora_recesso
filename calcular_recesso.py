import streamlit as st
from datetime import datetime, timedelta


# ============================================================
# CONFIGURAÇÕES
# ============================================================

ANO = 2026

INICIO_COMPENSACAO = datetime(2026, 10, 15)
FIM_COMPENSACAO = datetime(2026, 12, 23)


# Feriados que realmente estão dentro do período da compensação
FERIADOS = {
    datetime(2026, 11, 2),   # Finados
    datetime(2026, 11, 20),  # Consciência Negra
}


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def is_business_day(date):
    """
    Retorna True se for um dia útil:
    - Segunda a sexta
    - Não for feriado
    """

    return (
        date.weekday() < 5
        and date not in FERIADOS
    )


def first_business_on_or_after(date):
    """
    Encontra o primeiro dia útil a partir da data informada.
    """

    current = date

    while not is_business_day(current):
        current += timedelta(days=1)

    return current


def list_lost_dates(start, end):
    """
    Retorna todos os dias úteis perdidos
    durante o período das férias.
    """

    lost = []
    current = start

    while current <= end:

        if is_business_day(current):
            lost.append(current)

        current += timedelta(days=1)

    return lost


def backdate_business_days_from(start, days):
    """
    Volta a quantidade de dias úteis informada
    a partir da data de início da compensação.
    """

    current = start
    remaining = days

    while remaining > 0:

        current -= timedelta(days=1)

        if is_business_day(current):
            remaining -= 1

    return current


def count_business_days(start, end):
    """
    Conta quantos dias úteis existem entre duas datas.
    """

    total = 0
    current = start

    while current <= end:

        if is_business_day(current):
            total += 1

        current += timedelta(days=1)

    return total


# ============================================================
# CONFIGURAÇÃO DO STREAMLIT
# ============================================================

st.set_page_config(
    page_title="Calculadora de Compensação",
    page_icon="🗓️"
)


st.title("📅 Calculadora de Início de Compensação")


st.info(
    "🕒 **Período da compensação:** "
    "15/10/2026 até 23/12/2026"
)


# ============================================================
# CAMPOS
# ============================================================

inicio_str = st.text_input(
    "Início das férias (dd/mm/aaaa)"
)

fim_str = st.text_input(
    "Fim das férias (dd/mm/aaaa)"
)


# ============================================================
# CÁLCULO
# ============================================================

if st.button("Calcular"):

    try:

        ferias_inicio = datetime.strptime(
            inicio_str,
            "%d/%m/%Y"
        )

        ferias_fim = datetime.strptime(
            fim_str,
            "%d/%m/%Y"
        )


        # ----------------------------------------------------
        # VALIDAÇÕES
        # ----------------------------------------------------

        if ferias_fim < ferias_inicio:

            st.error(
                "❌ A data final das férias não pode "
                "ser anterior à data inicial."
            )

        elif (
            ferias_inicio.year != ANO
            or ferias_fim.year != ANO
        ):

            st.error(
                "⚠️ As datas das férias devem estar "
                "dentro de 2026."
            )

        else:

            # ------------------------------------------------
            # INÍCIO REAL DA CONTAGEM
            # ------------------------------------------------

            contagem_inicio_raw = max(
                ferias_inicio,
                INICIO_COMPENSACAO
            )


            # Primeiro dia útil a partir da data encontrada
            contagem_inicio = first_business_on_or_after(
                contagem_inicio_raw
            )


            # ------------------------------------------------
            # DIAS ÚTEIS PERDIDOS
            # ------------------------------------------------

            if contagem_inicio > ferias_fim:

                dias_perdidos = 0
                lost_dates = []

            else:

                lost_dates = list_lost_dates(
                    contagem_inicio,
                    ferias_fim
                )

                dias_perdidos = len(lost_dates)


            # ------------------------------------------------
            # DIAS DISPONÍVEIS PARA COMPENSAÇÃO
            # ------------------------------------------------

            dias_disponiveis = count_business_days(
                INICIO_COMPENSACAO,
                FIM_COMPENSACAO
            )


            # ------------------------------------------------
            # RESULTADO
            # ------------------------------------------------

            if dias_perdidos == 0:

                st.info(
                    "🎉 Nenhum dia útil será perdido "
                    "durante as férias."
                )

            else:

                # Verifica se cabe no período disponível
                if dias_perdidos > dias_disponiveis:

                    st.error(
                        f"❌ São necessários **{dias_perdidos} "
                        f"dias úteis** para compensação, mas existem "
                        f"apenas **{dias_disponiveis} dias úteis** "
                        f"disponíveis entre 15/10/2026 e 23/12/2026."
                    )

                else:

                    inicio_compensacao = (
                        backdate_business_days_from(
                            INICIO_COMPENSACAO,
                            dias_perdidos
                        )
                    )

                    st.success(
                        f"✅ O funcionário perderá "
                        f"**{dias_perdidos} dias úteis** "
                        f"durante as férias."
                    )

                    st.success(
                        f"🕒 A compensação deve iniciar em: "
                        f"**{inicio_compensacao.strftime('%d/%m/%Y')}**"
                    )


            # ------------------------------------------------
            # INFORMAÇÕES DO CÁLCULO
            # ------------------------------------------------

            st.divider()

            st.subheader("📊 Informações")

            col1, col2 = st.columns(2)

            with col1:

                st.metric(
                    "Dias úteis perdidos",
                    dias_perdidos
                )

            with col2:

                st.metric(
                    "Dias úteis disponíveis",
                    dias_disponiveis
                )


            # ------------------------------------------------
            # FERIADOS CONSIDERADOS
            # ------------------------------------------------

            with st.expander("📅 Feriados considerados"):

                st.write("02/11/2026 — Finados")
                st.write("20/11/2026 — Consciência Negra")


            # ------------------------------------------------
            # DIAS PERDIDOS
            # ------------------------------------------------

            if lost_dates:

                with st.expander(
                    "📋 Ver dias úteis perdidos"
                ):

                    for date in lost_dates:

                        st.write(
                            date.strftime("%d/%m/%Y")
                        )


    except ValueError:

        st.error(
            "⚠️ Digite as datas corretamente "
            "no formato dd/mm/aaaa."
        )
