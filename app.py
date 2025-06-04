import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Calculadora de Tempos", layout="wide")

st.title("⏱️ Calculadora de Tempos por Componente")

# Definição dos componentes
tipos = [
    "Origem", "Grupo de Controle", "Canal", "Decisão", "Espera",
    "Multiplas Rotas Paralelas", "Contagem Dinâmica", "Exportação de Público",
    "Espera por uma data", "Random Split", "Join", "Término"
]

# Pesos padrão no formato HH:MM
pesos_padrao = ["00:30", "01:00", "01:00", "00:30", "00:15", "01:30",
                "01:00", "00:30", "00:15", "01:00", "01:00", "00:15"]

# ---------------------
# Funções auxiliares
# ---------------------

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

# ---------------------
# Layout com abas
# ---------------------

aba1, aba2, aba3 = st.tabs(["📝 Entrada de Texto", "⚙️ Configuração de Pesos", "📊 Resultado"])

# ---------------------
# Aba 1 - Entrada
# ---------------------

with aba1:
    st.subheader("📝 Cole o texto com os componentes")
    texto = st.text_area(
        "Cole aqui o texto (copiado de qualquer fonte, como Excel ou sistemas).",
        height=300,
        placeholder="Cole aqui..."
    )

# ---------------------
# Aba 2 - Configuração de Pesos
# ---------------------

with aba2:
    st.subheader("⚙️ Defina os Pesos de Cada Componente (HH:MM)")

    df_pesos = pd.DataFrame({
        "Componente": tipos,
        "Peso (HH:MM)": pesos_padrao
    })

    df_pesos_editado = st.data_editor(
        df_pesos,
        num_rows="fixed",
        use_container_width=True
    )

    # Validação dos pesos
    pesos_validos = True
    for p in df_pesos_editado["Peso (HH:MM)"]:
        if hhmm_para_minutos(p) is None:
            pesos_validos = False
            st.error(f"❌ Peso inválido encontrado: '{p}'. Use o formato HH:MM.")
            break

# ---------------------
# Aba 3 - Resultado
# ---------------------

with aba3:
    st.subheader("📊 Resultado Final")

    if texto.strip() == "":
        st.info("⚠️ Cole o texto na aba 'Entrada de Texto' para gerar o resultado.")
    elif not pesos_validos:
        st.warning("⚠️ Corrija os pesos na aba 'Configuração de Pesos' para gerar o resultado.")
    else:
        texto_processado = limpar_texto(texto)

        contagem = []
        total_por_tipo = []

        for idx, row in df_pesos_editado.iterrows():
            componente = row["Componente"]
            peso_hhmm = row["Peso (HH:MM)"]
            peso_min = hhmm_para_minutos(peso_hhmm)

            ocorrencias = len(
                re.findall(rf'\b{re.escape(componente.lower())}\b', texto_processado)
            )

            total_min = ocorrencias * peso_min
            contagem.append(ocorrencias)
            total_por_tipo.append(total_min)

        df_resultado = pd.DataFrame({
            "Componente": tipos,
            "Peso (HH:MM)": df_pesos_editado["Peso (HH:MM)"],
            "Quantidade": contagem,
            "Total de Horas (HH:MM)": [minutos_para_hhmm(m) for m in total_por_tipo]
        })

        total_geral_min = sum(total_por_tipo)
        total_geral_qtd = sum(contagem)

        df_total = pd.DataFrame({
            "Componente": ["TOTAL"],
            "Peso (HH:MM)": [""],
            "Quantidade": [total_geral_qtd],
            "Total de Horas (HH:MM)": [minutos_para_hhmm(total_geral_min)]
        })

        df_resultado = pd.concat([df_resultado, df_total], ignore_index=True)

        st.table(df_resultado)

        # Download Excel
        def gerar_excel(df):
            from io import BytesIO
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name="Resultado")
            return output.getvalue()

        st.download_button(
            label="📥 Baixar Resultado em Excel",
            data=gerar_excel(df_resultado),
            file_name="resultado_tempos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
