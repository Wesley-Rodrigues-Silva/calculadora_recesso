import streamlit as st
from datetime import date, timedelta


# ============================================================
# CONFIGURAÇÕES
# ============================================================

ANO = 2026

# Regras conforme a tabela fornecida
REGRAS_JORNADA = {
    "8 horas": {
        "horas": 24,
        "inicio": date(2026, 10, 15),
    },
    "6 horas": {
        "horas": 18,
        "inicio": date(2026, 11, 3),
    },
    "5 horas": {
        "horas": 15,
        "inicio": date(2026, 11, 11),
    },
    "4 horas": {
        "horas": 12,
        "inicio": date(2026, 11, 19),
    },
}


# Último dia permitido para a compensação
FIM_COMPENSACAO = date(2026, 12, 23)


# Feriados dentro do período relevante
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

    Segunda a sexta-feira e não pode ser feriado.
    """

    return (
        data.weekday() < 5
        and data not in FERIADOS
    )


def get_business_days(inicio, fim):
    """
    Retorna uma lista contendo todos os dias úteis
    entre duas datas, incluindo início e fim.
    """

    dias = []
    atual = inicio

    while atual <= fim:

        if is_business_day(atual):
            dias.append(atual)

        atual += timedelta(days=1)

    return dias


def count_business_days(inicio, fim):
    """
    Conta a quantidade de dias úteis entre duas datas.
    """

    return len(
        get_business_days(inicio, fim)
    )


def calculate_end_date(inicio, quantidade_dias):
    """
    Calcula a data em que termina a compensação,
    contando somente dias úteis.
    """

    dias_contados = 0
    atual = inicio

    while atual <= FIM_COMPENSACAO:

        if is_business_day(atual):

            dias_contados += 1

            if dias_contados == quantidade_dias:
                return atual

        atual += timedelta(days=1)

    return None


# ============================================================
# CONFIGURAÇÃO DO STREAMLIT
# ============================================================

st.set_page_config(
    page_title="Calculadora de Compensação",
    page_icon="🗓️",
    layout="centered"
)


# ============================================================
# TÍTULO
# ============================================================

st.title("📅 Calculadora de Compensação")


# ============================================================
# JORNADA
# ============================================================

jornada = st.selectbox(
    "Jornada contratual diária",
    [
        "8 horas",
        "6 horas",
        "5 horas",
        "4 horas",
    ]
)


# Obtém as regras da jornada selecionada
regra = REGRAS_JORNADA[jornada]

horas_compensar = regra["horas"]
inicio_compensacao = regra["inicio"]


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
# BOTÃO CALCULAR
# ============================================================

if st.button("Calcular"):

    # --------------------------------------------------------
    # VALIDAÇÕES
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
            "⚠️ As datas das férias devem estar dentro de 2026."
        )

    else:

        # ====================================================
        # DIAS ÚTEIS PERDIDOS
        # ====================================================

        # A contagem dos dias perdidos só começa na data
        # definida para o início da compensação da jornada.

        inicio_contagem = max(
            inicio_ferias,
            inicio_compensacao
        )

        if inicio_contagem <= fim_ferias:

            dias_perdidos_lista = get_business_days(
                inicio_contagem,
                fim_ferias
            )

        else:

            dias_perdidos_lista = []


        dias_perdidos = len(
            dias_perdidos_lista
        )


        # ====================================================
        # DIAS ÚTEIS DISPONÍVEIS PARA COMPENSAÇÃO
        # ====================================================

        dias_disponiveis = count_business_days(
            inicio_compensacao,
            FIM_COMPENSACAO
        )


        # ====================================================
        # DATA FINAL DA COMPENSAÇÃO
        # ====================================================

        data_final_compensacao = calculate_end_date(
            inicio_compensacao,
            3
        )


        # ====================================================
        # RESULTADO
        # ====================================================

        st.divider()

        st.subheader("📋 Resultado")


        # ----------------------------------------------------
        # JORNADA E HORAS
        # ----------------------------------------------------

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "Jornada",
                jornada
            )

        with col2:

            st.metric(
                "Horas a compensar",
                f"{horas_compensar} horas"
            )


        # ----------------------------------------------------
        # INÍCIO DA COMPENSAÇÃO
        # ----------------------------------------------------

        st.success(
            f"🕒 **Início da compensação:** "
            f"{inicio_compensacao.strftime('%d/%m/%Y')}"
        )


        # ----------------------------------------------------
        # FIM DA COMPENSAÇÃO
        # ----------------------------------------------------

        if data_final_compensacao:

            st.success(
                f"🏁 **Fim da compensação:** "
                f"{data_final_compensacao.strftime('%d/%m/%Y')}"
            )

        else:

            st.error(
                "❌ A compensação não cabe no período "
                "até 23/12/2026."
            )


        # ====================================================
        # INFORMAÇÕES SOBRE AS FÉRIAS
        # ====================================================

        st.divider()

        st.subheader("📊 Informações sobre as férias")


        # ====================================================
        # SE NÃO AFETAR A COMPENSAÇÃO
        # ====================================================

        if dias_perdidos == 0:

            st.success(
                "✅ Período de férias não afeta a compensação."
            )

        # ====================================================
        # SE AFETAR A COMPENSAÇÃO
        # ====================================================

        else:

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
            # VER DIAS PERDIDOS
            # ------------------------------------------------

            with st.expander(
                "📋 Ver dias úteis perdidos"
            ):

                for dia in dias_perdidos_lista:

                    st.write(
                        dia.strftime("%d/%m/%Y")
                    )


            # ------------------------------------------------
            # VERIFICAÇÃO
            # ------------------------------------------------

            if dias_perdidos > dias_disponiveis:

                st.error(
                    f"❌ Existem {dias_perdidos} dias úteis "
                    f"a compensar, mas o período possui apenas "
                    f"{dias_disponiveis} dias úteis disponíveis."
                )


        # ====================================================
        # FERIADOS CONSIDERADOS
        # ====================================================

        with st.expander(
            "📅 Feriados considerados"
        ):

            st.write(
                "02/11/2026 — Finados"
            )

            st.write(
                "20/11/2026 — Consciência Negra"
            )
