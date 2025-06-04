import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="⏱️ Calculadora de Tempos por Componente", layout="wide")

st.title("⏱️ Calculadora de Tempos por Componente")

# 🎯 Configuração dos tipos e pesos padrão
componentes = [
    "Origem", "Grupo de Controle", "Canal", "Decisão", "Espera",
    "Multiplas Rotas Paralelas", "Contagem Dinâmica", "Exportação de Público",
    "Espera por uma data", "Random Split", "Join", "Término"
]

pesos_padrao = {
    "Origem": "00:30",
    "Grupo de Controle": "01:00",
    "Canal": "01:00",
    "Decisão": "00:30",
    "Espera": "00:15",
    "Multiplas Rotas Paralelas": "01:30",
    "Contagem Dinâmica": "01:00",
    "Exportação de Público": "00:30",
    "Espera por uma data": "00:15",
    "Random Split": "01:00",
    "Join": "01:00",
    "Término": "00:15"
}

# 🔧 Funções auxiliares
def hhmm_para_minutos(hhmm):
    try:
        horas, minutos = map(int, hhmm.strip().split(":"))
        return horas * 60 + minutos
    except:
        return 0

def minutos_para_hhmm(minutos):
    horas = minutos // 60
    minutos_restantes = minutos % 60
    return f"{horas:02d}:{minutos_restantes:02d}"

def limpar_texto(texto):
    texto_sem_parenteses = re.sub(r'\(.*?\)', '', texto)
    return texto_sem_parenteses.lower()

# 📝 Entrada de texto
st.subheader("📝 Cole abaixo o texto com os componentes")

texto = st.text_area(
    "Cole aqui os dados copiados da sua tabela ou sistema",
    height=250,
    placeholder="Exemplo:\nID\tComponente\tStatus\tInício\tTempo de execução\t...\n..."
)

# 🚦 Processamento
if texto.strip() != "":
    texto_processado = limpar_texto(texto)

    dados = []

    total_minutos_geral = 0
    total_quantidade_geral = 0

    for componente in componentes:
        nome_proc = componente.lower()

        # Contagem de ocorrências no texto
        ocorrencias = len(re.findall(rf'\b{re.escape(nome_proc)}\b', texto_processado))

        peso_hhmm = pesos_padrao.get(componente, "00:00")
        peso_min = hhmm_para_minutos(peso_hhmm)

        total_min = peso_min * ocorrencias

        dados.append({
            "Componente": componente,
            "Peso (HH:MM)": peso_hhmm,
            "Quantidade": ocorrencias,
            "Total de Horas (HH:MM)": minutos_para_hhmm(total_min)
        })

        total_minutos_geral += total_min
        total_quantidade_geral += ocorrencias

    # Linha de TOTAL
    dados.append({
        "Componente": "TOTAL",
        "Peso (HH:MM)": "",
        "Quantidade": total_quantidade_geral,
        "Total de Horas (HH:MM)": minutos_para_hhmm(total_minutos_geral)
    })

    df_resultado = pd.DataFrame(dados)

    # 📊 Exibição do resultado
    st.subheader("📊 Resultado Final")
    st.dataframe(
        df_resultado,
        use_container_width=True,
        height=(len(df_resultado) + 1) * 35
    )

    # 📥 Download do resultado em Excel
    def gerar_excel(df):
        from io import BytesIO
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Resultado")
        return output.getvalue()

    st.download_button(
        label="📥 Baixar Resultado em Excel",
        data=gerar_excel(df_resultado),
        file_name="resultado_tempos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.info("Cole o texto acima para gerar o resultado.")
