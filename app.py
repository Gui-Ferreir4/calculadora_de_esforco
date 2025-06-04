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

# Se texto colado:
if texto.strip() != "":
    texto_processado = limpar_texto(texto)

    # Inicializa DataFrame base com pesos padrão
    df_base = pd.DataFrame({
        "Componente": tipos,
        "Peso (HH:MM)": pesos_padrao,
    })

    # Interface editável dos pesos
    st.subheader("📊 Tabela de Componentes — Edite os Pesos para Recalcular")
    df_editado = st.data_editor(
        df_base,
        use_container_width=True,
        num_rows="fixed",
        key="editor",
        column_config={
            "Peso (HH:MM)": st.column_config.TextColumn(help="Formato HH:MM", width="medium")
        }
    )

    # Validação e cálculo
    pesos_validos = True
    total_geral_min = 0
    total_geral_qtd = 0
    resultados = []

    for _, row in df_editado.iterrows():
        componente = row["Componente"]
        peso_texto = row["Peso (HH:MM)"]
        peso_min = hhmm_para_minutos(str(peso_texto))

        if peso_min is None:
            st.error(f"❌ Peso inválido para '{componente}': '{peso_texto}' — Use o formato HH:MM.")
            pesos_validos = False
            break

        ocorrencias = len(re.findall(rf'\b{re.escape(componente.lower())}\b', texto_processado))
        total_min = ocorrencias * peso_min

        total_geral_min += total_min
        total_geral_qtd += ocorrencias

        resultados.append({
            "Componente": componente,
            "Peso (HH:MM)": peso_texto,
            "Quantidade": ocorrencias,
            "Total de Horas (HH:MM)": minutos_para_hhmm(total_min)
        })

    if pesos_validos:
        # Adiciona linha de total
        resultados.append({
            "Componente": "TOTAL",
            "Peso (HH:MM)": "",
            "Quantidade": total_geral_qtd,
            "Total de Horas (HH:MM)": minutos_para_hhmm(total_geral_min)
        })

        df_resultado = pd.DataFrame(resultados)

        st.dataframe(
            df_resultado,
            use_container_width=True,
            height=(len(df_resultado) + 1) * 35
        )

        # Botão para baixar em Excel
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
else:
    st.info("Cole o texto acima para iniciar o cálculo.")
