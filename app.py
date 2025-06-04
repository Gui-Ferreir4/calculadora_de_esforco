import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="⏱️ Calculadora de Tempos por Componente", layout="wide")

st.title("⏱️ Calculadora de Tempos por Componente")

# 🔧 Lista de componentes e pesos padrão
tipos = [
    "Origem", "Grupo de Controle", "Canal", "Decisão", "Espera",
    "Multiplas Rotas Paralelas", "Contagem Dinâmica", "Exportação de Público",
    "Espera por uma data", "Random Split", "Join", "Término"
]

pesos_padrao = ["00:30", "01:00", "01:00", "00:30", "00:15", "01:30",
                "01:00", "00:30", "00:15", "01:00", "01:00", "00:15"]

# 🔣 Funções auxiliares

def hhmm_para_minutos(hhmm):
    try:
        h, m = map(int, hhmm.strip().split(":"))
        return h * 60 + m
    except:
        return None

def minutos_para_hhmm(minutos):
    h = minutos // 60
    m = minutos % 60
    return f"{h:02d}:{m:02d}"

def limpar_texto(texto):
    return re.sub(r'\(.*?\)', '', texto).lower()

# 📝 Entrada de dados
st.subheader("📝 Cole o texto com os componentes")
texto = st.text_area(
    "Cole aqui o texto (copiado do Excel, sistema ou outra fonte)",
    height=250,
    placeholder="Exemplo:\nID\tComponente\tStatus\tInício\tTempo de execução\tPúblico\tInformações\n..."
)

# 🔢 Processamento
if texto.strip() != "":
    texto_processado = limpar_texto(texto)

    # 🏗️ Construção da tabela
    dados = []
    for tipo, peso in zip(tipos, pesos_padrao):
        dados.append({
            "Componente": tipo,
            "Peso (HH:MM)": peso,
            "Quantidade": 0,
            "Total de Horas (HH:MM)": "00:00"
        })

    df = pd.DataFrame(dados)

    # 🎯 Contagem
    for i, row in df.iterrows():
        componente = row["Componente"]
        ocorrencias = len(
            re.findall(rf'\b{re.escape(componente.lower())}\b', texto_processado)
        )
        df.at[i, "Quantidade"] = ocorrencias

    # 🖊️ Editor da tabela (permite alterar os pesos)
    st.subheader("📊 Resultado e Configuração dos Pesos")
    df_editado = st.data_editor(
        df,
        num_rows="fixed",
        use_container_width=True,
        key="editor"
    )

    # 🚦 Validação dos pesos e cálculo dos totais
    pesos_validos = True
    total_geral_min = 0
    total_geral_qtd = 0

    totais = []

    for i, row in df_editado.iterrows():
        peso_min = hhmm_para_minutos(str(row["Peso (HH:MM)"]))
        if peso_min is None:
            pesos_validos = False
            st.error(f"❌ Peso inválido para '{row['Componente']}'. Use HH:MM.")
            break

        qtd = int(row["Quantidade"])
        total_min = peso_min * qtd

        totais.append(minutos_para_hhmm(total_min))

        total_geral_min += total_min
        total_geral_qtd += qtd

    if pesos_validos:
        df_editado["Total de Horas (HH:MM)"] = totais

        # ➕ Adiciona linha de total
        df_total = pd.DataFrame({
            "Componente": ["TOTAL"],
            "Peso (HH:MM)": [""],
            "Quantidade": [total_geral_qtd],
            "Total de Horas (HH:MM)": [minutos_para_hhmm(total_geral_min)]
        })

        df_final = pd.concat([df_editado, df_total], ignore_index=True)

        st.dataframe(
            df_final,
            use_container_width=True,
            height=(len(df_final) + 1) * 35
        )

        # 📥 Download Excel
        def gerar_excel(df):
            from io import BytesIO
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name="Resultado")
            return output.getvalue()

        st.download_button(
            label="📥 Baixar Resultado em Excel",
            data=gerar_excel(df_final),
            file_name="resultado_tempos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.info("🔎 Cole o texto no campo acima para gerar o resultado.")
