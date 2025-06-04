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
    "Origem": "00:05",
    "Grupo de Controle": "00:01",
    "Canal": "00:05",
    "Decisão": "00:05",
    "Espera": "00:01",
    "Multiplas Rotas Paralelas": "00:05",
    "Contagem Dinâmica": "00:01",
    "Exportação de Público": "00:05",
    "Espera por uma data": "00:01",
    "Random Split": "00:05",
    "Join": "00:01",
    "Término": "00:01"
}

# 🔧 Funções auxiliares
def hhmm_para_minutos(hhmm):
    try:
        horas, minutos = map(int, str(hhmm).strip().split(":"))
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
    placeholder="Exemplo:\n
                ID\t                       Componente\t Status\t    Início\t                Tempo de execução\t    Público Selecionado\t    Mais informações\n
                684058ef31243a261fb51baa\t Origem\t     Ok\t        04/06/2025 - 11:37\t    5s\t                   10\t                     -"
)

# 🚦 Processamento
if texto.strip() != "":
    texto_processado = limpar_texto(texto)

    dados = []

    for componente in componentes:
        nome_proc = componente.lower()

        ocorrencias = len(re.findall(rf'\b{re.escape(nome_proc)}\b', texto_processado))

        dados.append({
            "Componente": componente,
            "Peso (HH:MM)": pesos_padrao.get(componente, "00:00"),
            "Quantidade": ocorrencias,
        })

    df_base = pd.DataFrame(dados)

    st.subheader("⚙️ Ajuste Peso ou Quantidade se necessário")

    tabela_editada = st.data_editor(
        df_base,
        use_container_width=True,
        num_rows="fixed",
        column_config={
            "Peso (HH:MM)": st.column_config.TextColumn(
                help="Formato HH:MM. Ex.: 01:30",
                width="medium"
            ),
            "Quantidade": st.column_config.NumberColumn(
                help="Ajuste se necessário",
                step=1,
                min_value=0,
                width="small"
            )
        }
    )

    # 🚦 Cálculo dos totais
    totais_hhmm = []
    total_geral_min = 0
    total_geral_qtd = 0

    for _, row in tabela_editada.iterrows():
        peso_min = hhmm_para_minutos(row["Peso (HH:MM)"])
        qtd = int(row["Quantidade"])

        total_min = peso_min * qtd
        totais_hhmm.append(minutos_para_hhmm(total_min))

        total_geral_min += total_min
        total_geral_qtd += qtd

    tabela_editada["Total de Horas (HH:MM)"] = totais_hhmm

    # ➕ Linha de total
    linha_total = pd.DataFrame([{
        "Componente": "TOTAL",
        "Peso (HH:MM)": "",
        "Quantidade": total_geral_qtd,
        "Total de Horas (HH:MM)": minutos_para_hhmm(total_geral_min)
    }])

    resultado_final = pd.concat([tabela_editada, linha_total], ignore_index=True)

    st.subheader("📊 Resultado Final")
    st.dataframe(
        resultado_final,
        use_container_width=True,
        height=(len(resultado_final) + 1) * 35
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
        data=gerar_excel(resultado_final),
        file_name="resultado_tempos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.info("Cole o texto acima para gerar o resultado.")
