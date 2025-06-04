import streamlit as st
import pandas as pd
import re


st.set_page_config(page_title="Calculadora de Tempos", layout="wide")

st.title("⏱️ Calculadora de Tempos por Detecção no Texto")

st.markdown("""
Cole abaixo qualquer texto que contenha os componentes (não precisa estar formatado como tabela).  
O app irá identificar, contar e calcular os tempos de execução com base nos pesos definidos.
""")

# Lista dos tipos conhecidos
tipos = [
    "Origem", "Grupo de Controle", "Canal", "Decisão", "Espera",
    "Multiplas Rotas Paralelas", "Contagem Dinâmica", "Exportação de Público",
    "Espera por uma data", "Random Split", "Join", "Término"
]

# Pesos padrão no formato HH:MM
pesos_padrao = {
    "Origem": "00:30", "Grupo de Controle": "01:00", "Canal": "01:00",
    "Decisão": "00:30", "Espera": "00:15", "Multiplas Rotas Paralelas": "01:30",
    "Contagem Dinâmica": "01:00", "Exportação de Público": "00:30",
    "Espera por uma data": "00:15", "Random Split": "01:00", "Join": "01:00",
    "Término": "00:15"
}

# Campo de entrada de texto
texto = st.text_area(
    "📋 Cole aqui o texto (copiado de qualquer lugar, incluindo tabelas, prints do excel ou outros):",
    height=300,
    placeholder="Cole aqui..."
)

if texto.strip() != "":
    st.subheader("⚙️ Definir Pesos (HH:MM)")
    col1, col2 = st.columns(2)

    pesos_usuario = {}

    with col1:
        for tipo in tipos[:len(tipos)//2]:
            valor = st.text_input(f"{tipo}:", value=pesos_padrao.get(tipo, "00:00"))
            pesos_usuario[tipo] = valor

    with col2:
        for tipo in tipos[len(tipos)//2:]:
            valor = st.text_input(f"{tipo}:", value=pesos_padrao.get(tipo, "00:00"))
            pesos_usuario[tipo] = valor

    # Função para buscar ocorrências ignorando textos entre parênteses
    def limpar_tipo(texto):
        return re.sub(r"\s*\(.*?\)", "", texto).strip()

    # Contagem dos componentes no texto
    contagem = {}
    for tipo in tipos:
        padrao = re.compile(rf'\b{re.escape(tipo)}\b', re.IGNORECASE)
        ocorrencias = len(padrao.findall(re.sub(r'\(.*?\)', '', texto)))
        contagem[tipo] = ocorrencias

    # Conversão de HH:MM para timedelta
    def hhmm_para_timedelta(hhmm):
        try:
            h, m = map(int, hhmm.strip().split(":"))
            return pd.Timedelta(hours=h, minutes=m)
        except:
            return pd.Timedelta(0)

    pesos_tempo = {tipo: hhmm_para_timedelta(valor) for tipo, valor in pesos_usuario.items()}

    # Montagem da tabela de resultados
    df_resultado = pd.DataFrame({
        "Tipo": tipos,
        "Peso (hh:mm)": [pesos_usuario[t] for t in tipos],
        "Quantidade": [contagem[t] for t in tipos],
        "Total de Horas": [pesos_tempo[t] * contagem[t] for t in tipos]
    })

    total_quantidade = df_resultado["Quantidade"].sum()
    total_tempo = df_resultado["Total de Horas"].sum()

    total_row = pd.DataFrame({
        "Tipo": ["TOTAL"],
        "Peso (hh:mm)": [""],
        "Quantidade": [total_quantidade],
        "Total de Horas": [total_tempo]
    })

    df_resultado = pd.concat([df_resultado, total_row], ignore_index=True)

    st.subheader("📊 Resultado Final")
    st.dataframe(df_resultado)

    # Gerar Excel
    def converter_excel(df):
        from io import BytesIO
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name="Resultado")
            writer.close()
        return output.getvalue()

    st.download_button(
        label="📥 Baixar Resultado em Excel",
        data=converter_excel(df_resultado),
        file_name="resultado_pesos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.info("Cole o texto acima para começar.")
