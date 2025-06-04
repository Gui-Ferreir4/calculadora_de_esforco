import streamlit as st
import pandas as pd
import re


st.set_page_config(page_title="Calculadora de esforço", layout="wide")

st.title("⏱️ Calculadora de esforço - Jornada")

st.markdown("""
Cole abaixo qualquer texto que contenha os componentes (não precisa estar formatado como tabela).  
O app irá identificar, contar e calcular o esforço aplicado com base nos pesos definidos.
""")

# Lista dos tipos conhecidos
tipos = [
    "Origem", "Grupo de Controle", "Canal", "Decisão", "Espera",
    "Multiplas Rotas Paralelas", "Contagem Dinâmica", "Exportação de Público",
    "Espera por uma data", "Random Split", "Join", "Término"
]

# Pesos padrão no formato HH:MM
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

# Campo de entrada de texto
texto = st.text_area(
    "📋 Cole aqui o texto (copiado do histórico de contagem, ou histórico de execução)",
    height=300,
    placeholder="Cole aqui..."
)

if texto.strip() != "":
    st.subheader("⚙️ Ajustar Pesos (HH:MM)")
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
    texto_limpo = re.sub(r'\(.*?\)', '', texto)
    for tipo in tipos:
        padrao = re.compile(rf'\b{re.escape(tipo)}\b', re.IGNORECASE)
        ocorrencias = len(padrao.findall(texto_limpo))
        contagem[tipo] = ocorrencias

    # Conversão de HH:MM para minutos
    def hhmm_para_minutos(hhmm):
        try:
            h, m = map(int, hhmm.strip().split(":"))
            return h * 60 + m
        except:
            return 0

    # Conversão de minutos para HH:MM
    def minutos_para_hhmm(minutos):
        h = minutos // 60
        m = minutos % 60
        return f"{h:02d}:{m:02d}"

    pesos_minutos = {tipo: hhmm_para_minutos(valor) for tipo, valor in pesos_usuario.items()}

    # Montagem da tabela de resultados
    total_por_tipo = {tipo: pesos_minutos[tipo] * contagem[tipo] for tipo in tipos}

    df_resultado = pd.DataFrame({
        "Tipo": tipos,
        "Peso (HH:MM)": [pesos_usuario[t] for t in tipos],
        "Quantidade": [contagem[t] for t in tipos],
        "Total de Horas": [minutos_para_hhmm(total_por_tipo[t]) for t in tipos]
    })

    total_quantidade = df_resultado["Quantidade"].sum()
    total_tempo_minutos = sum(total_por_tipo.values())

    total_row = pd.DataFrame({
        "Tipo": ["TOTAL"],
        "Peso (HH:MM)": [""],
        "Quantidade": [total_quantidade],
        "Total de Horas": [minutos_para_hhmm(total_tempo_minutos)]
    })

    df_resultado = pd.concat([df_resultado, total_row], ignore_index=True)

    st.subheader("📊 Resultado Final")
    st.table(df_resultado)  # Tabela sem barra de rolagem

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
