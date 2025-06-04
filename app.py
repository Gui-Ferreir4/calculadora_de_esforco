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
        h, m = map(int, str(hhmm).strip().split(":"))
        return h * 60 + m
    except:
        return None

def minutos_para_hhmm(minutos):
    h = minutos // 60
    m = minutos % 60
    return f"{h:02d}:{m:02d}"

def limpar_texto(texto):
    texto_sem_parenteses = re.sub(r'\(.*?\)', '', texto)
    return texto_sem_parenteses.lower()

# 📝 Entrada de dados
st.subheader("📝 Cole o texto com os componentes")
texto = st.text_area(
    "Cole aqui o texto (copiado do Excel, sistema ou outra fonte)",
    height=250,
    placeholder="Exemplo:\nID\tComponente\tStatus\tInício\tTempo de execução\tPúblico\tInformações\n..."
)

# Processamento quando há texto
if texto.strip() != "":
    texto_processado = limpar_texto(texto)

    # 🏗️ Inicializa DataFrame com os dados base
    dados_iniciais = pd.DataFrame({
        "Componente": tipos,
        "Peso (HH:MM)": pesos_padrao,
    })

    # 🎯 Conta quantas vezes cada componente aparece no texto
    quantidades = []
    for componente in dados_iniciais["Componente"]:
        ocorrencias = len(re.findall(rf'\b{re.escape(componente.lower())}\b', texto_processado))
        quantidades.append(ocorrencias)

    dados_iniciais["Quantidade"] = quantidades

    # 🖊️ Exibe a tabela editável para pesos
    st.subheader("📊 Tabela de Resultados — Edite os Pesos para Atualizar o Total")

    tabela_editada = st.data_editor(
        dados_iniciais,
        num_rows="fixed",
        use_container_width=True,
        column_config={
            "Peso (HH:MM)": st.column_config.TextColumn(help="Formato HH:MM (ex: 01:30)", width="medium")
        }
    )

    # 🚦 Processa os cálculos
    resultados = []
    total_geral_min = 0
    total_geral_qtd = 0
    erro_peso = False

    for _, row in tabela_editada.iterrows():
        peso_min = hhmm_para_minutos(row["Peso (HH:MM)"])
        if peso_min is None:
            st.error(f"❌ Peso inválido para '{row['Componente']}': '{row['Peso (HH:MM)']}'. Use HH:MM.")
            erro_peso = True
            break

        qtd = int(row["Quantidade"])
        total_min = peso_min * qtd

        total_geral_min += total_min
        total_geral_qtd += qtd

        resultados.append({
            "Componente": row["Componente"],
            "Peso (HH:MM)": row["Peso (HH:MM)"],
            "Quantidade": qtd,
            "Total de Horas (HH:MM)": minutos_para_hhmm(total_min)
        })

    if not erro_peso:
        # ➕ Adiciona linha de total
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

        # 📥 Botão de download
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
