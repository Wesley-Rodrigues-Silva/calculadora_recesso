import streamlit as st
from datetime import datetime, timedelta, date


# ============================================================
# CONFIGURAÇÕES
# ============================================================

ANO = 2026

INICIO_COMPENSACAO = date(2026, 10, 15)
FIM_COMPENSACAO = date(2026, 12, 23)


# Feriados dentro do período da compensação
FERIADOS = {
    date(2026, 11, 2),   # Finados
    date(2026, 11, 20),  # Consciência Negra
}


# ============================================================
# FUNÇÕES
# ============================================================

def is_business_day(data):
    """
    Retorna True se a data for um dia útil.
    Segunda a sexta e não pode ser feriado.
    """

    return (
        data.weekday() < 5
        and data not in FERIADOS
    )


def count_business_days(inicio, fim):
    """
    Conta os dias úteis entre duas datas, incluindo
    a data inicial e a final.
    """

    total = 0
    atual = inicio

    while atual <= fim:

        if is_business_day(atual):
            total += 1

        atual += timedelta(days=1)

    return total


def get_business_days(inicio, fim):
    """
    Retorna uma lista contendo todos os dias úteis
    entre as duas datas.
    """

    dias = []
    atual = inicio

    while atual <= fim:

        if is_business_day(atual):
            dias.append(atual)

        atual += timedelta(days=1)

    return dias


def calculate_compensation_end(start, number_of_days):
    """
    Calcula a data em que a compensação termina,
    contando os dias úteis a partir da data inicial.
    """

    if number_of_days <= 0:
        return start

    dias_contados = 0
    atual = start

    while atual <= FIM_COMPENSACAO:

        if is_business_day(atual):
            dias_contados += 1

            if dias_contados == number_of_days:
                return atual

        atual += timedelta(days=1)

    return None


# ============================================================
# CONFIGURAÇÃO DO STREAMLIT
# ============================================================

st.set_page_config(
    page_title="Calculadora de Compensação",
    page_icon="🗓️"
)


# ============================================================
# TÍTULO
# ============================================================

st.title("📅 Calculadora de Compensação")


# ============================================================
# DATAS DAS FÉRIAS
# ============================================================

inicio_ferias = st.date_input(
    "Início das férias",
    value=None,
    format="DD/MM/YYYY"
)

fim_ferias = st.date_input(
    "Fim das férias",
    value=None,
    format="DD/MM/YYYY"
)


# ============================================================
# BOTÃO
# ============================================================

if st.button("Calcular"):

    # --------------------------------------------------------
    # VALIDAÇÃO
    # --------------------------------------------------------

    if inicio_ferias is None or fim_ferias is None:

        st.warning(
            "⚠️ Selecione a data de início e a data de fim das férias."
        )

    elif fim_ferias < inicio_ferias:

        st.error(
            "❌ A data final das férias não pode ser anterior "
            "à data inicial."
        )

    elif (
        inicio_ferias.year != ANO
        or fim_ferias.year != ANO
    ):

        st.error(
            "⚠️ As férias devem estar dentro do ano de 2026."
        )

    else:

        # ----------------------------------------------------
        # DETERMINA O PERÍODO QUE SERÁ CONTADO
        # ----------------------------------------------------

        # A contagem dos dias perdidos só começa em 15/10.
        inicio_contagem = max(
            inicio_ferias,
            INICIO_COMPENSACAO
        )


        # ----------------------------------------------------
        # DIAS ÚTEIS PERDIDOS
        # ----------------------------------------------------

        if inicio_contagem > fim_ferias:

            dias_perdidos = 0
            dias_perdidos_lista = []

        else:

            dias_perdidos_lista = get_business_days(
                inicio_contagem,
                fim_ferias
            )

            dias_perdidos = len(
                dias_perdidos_lista
            )


        # ----------------------------------------------------
        # DIAS DISPONÍVEIS PARA COMPENSAÇÃO
        # ----------------------------------------------------

        dias_disponiveis = count_business_days(
            INICIO_COMPENSACAO,
            FIM_COMPENSACAO
        )


        # ----------------------------------------------------
        # RESULTADO
        # ----------------------------------------------------

        st.divider()

        if dias_perdidos == 0:

            st.success(
                "🎉 Nenhum dia útil será perdido "
                "durante o período considerado."
            )

        else:

            st.success(
                f"📌 Dias úteis a compensar: "
                f"**{dias_perdidos} dias**"
            )


            # ------------------------------------------------
            # VERIFICA SE CABE NO PERÍODO
            # ------------------------------------------------

            if dias_perdidos > dias_disponiveis:

                st.error(
                    f"❌ Não é possível compensar todos os "
                    f"{dias_perdidos} dias úteis dentro do período "
                    f"de 15/10/2026 a 23/12/2026."
                )

                st.write(
                    f"Existem apenas **{dias_disponiveis} dias úteis** "
                    f"disponíveis nesse período."
                )

            else:

                data_final_compensacao = (
                    calculate_compensation_end(
                        INICIO_COMPENSACAO,
                        dias_perdidos
                    )
                )


                st.success(
                    f"🕒 A compensação começa em "
                    f"**15/10/2026**."
                )

                st.success(
                    f"🏁 Para compensar {dias_perdidos} dias úteis, "
                    f"a compensação termina em "
                    f"**{data_final_compensacao.strftime('%d/%m/%Y')}**."
                )


        # ====================================================
        # INFORMAÇÕES
        # ====================================================

        st.divider()

        st.subheader("📊 Resumo")

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Dias perdidos",
                dias_perdidos
            )

        with col2:

            st.metric(
                "Dias disponíveis",
                dias_disponiveis
            )

        with col3:

            saldo = dias_disponiveis - dias_perdidos

            st.metric(
                "Saldo",
                saldo
            )


        # ====================================================
        # FERIADOS
        # ====================================================

        with st.expander("📅 Feriados considerados"):

            st.write(
                "02/11/2026 — Finados"
            )

            st.write(
                "20/11/2026 — Consciência Negra"
            )


        # ====================================================
        # DIAS PERDIDOS
        # ====================================================

        if dias_perdidos_lista:

            with st.expander(
                "📋 Ver dias úteis perdidos"
            ):

                for dia in dias_perdidos_lista:

                    st.write(
                        dia.strftime("%d/%m/%Y")
                    )
