import streamlit as st
from datetime import datetime, timedelta

# Função para verificar se há interseção entre férias e período de compensação
def precisa_compensar(ferias_inicio, ferias_fim, tipo):
    comp_start = datetime(ferias_inicio.year, 10, 15) if tipo == 'PUC' else datetime(ferias_inicio.year, 10, 16)
    comp_end = datetime(ferias_inicio.year, 12, 23)
    return ferias_fim >= comp_start and ferias_inicio <= comp_end

# Interface Streamlit
st.set_page_config(page_title="Cálculo do Início da Compensação", page_icon="📅")
st.title("📅 Cálculo do Início da Compensação")

# Entrada de dados
tipo_vinculo = st.selectbox("Tipo de vínculo", ["PUC", "Fundação"])
inicio_str = st.text_input("Início das férias (dd/mm/aaaa)", "20/09/2025")
fim_str = st.text_input("Fim das férias (dd/mm/aaaa)", "15/10/2025")

# Botão de cálculo
if st.button("Calcular"):
    try:
        # Conversão de datas
        inicio_ferias = datetime.strptime(inicio_str, "%d/%m/%Y")
        fim_ferias = datetime.strptime(fim_str, "%d/%m/%Y")

        # Verifica se há necessidade de compensação
        if precisa_compensar(inicio_ferias, fim_ferias, tipo_vinculo):
            compensacao_inicio = inicio_ferias - timedelta(days=1)
            st.warning("⚠️ As férias coincidem com o período de compensação.")
            st.info(f"📅 Deverá iniciar a compensação em: {compensacao_inicio.strftime('%d/%m/%Y')}")
        else:
            st.success("🎉 As férias não coincidem com o período de compensação. Nenhuma compensação é necessária.")

    except ValueError:
        st.error("❌ Datas inválidas. Use o formato dd/mm/aaaa.")

