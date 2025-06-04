import streamlit as st
import pandas as pd
import re


st.set_page_config(page_title="Calculadora de Tempos", layout="wide")

st.title("⏱️ Calculadora de Tempos - Via Tabela Colada (2 linhas por item)")

st.markdown("""
Cole abaixo a tabela copiada do Excel (onde cada item ocupa duas linhas). 
O app buscará a coluna **"Componente"** e fará o cálculo com base nos pesos definidos.
""")

# Função para remover textos entre parênteses
def limpar_tipo(texto):
    if pd.isna(texto):
        return ""
    return re.sub(r"\s*\(.*?\)", "", str(texto)).strip()


tipos = [
    "Origem", "Grupo de Controle", "Canal", "Decisão", "Espera",
    "Multiplas Rotas Paralelas", "Contagem Dinâmica", "Exportação de Público",
    "Espera por uma data", "Random Split", "Join", "Término"
]

pesos_padrao = {
    "Origem": "00:30", "Grupo de Controle": "01:00", "Canal": "01:00",
    "Decisão": "00:30", "Espera": "00:15", "Multiplas Rotas Paralelas": "01:30",
    "Contagem Dinâmica": "01:00", "Exportação de Público": "00:30",
    "Espera por uma data": "00:15", "Random Split": "01:00", "Join": "01:00",
    "Término": "00:15"
}

# Entrada da tabela
st.subheader("📋 Cole aqui sua tabela (incluindo cabeçalhos)")

texto = st.text_area(
    "Cole os dados aqui (copiados do Excel):",
    placeholder="Exemplo:\nID\tComponente\t...\nxxx\tOrigem\t...\n02/06/2025 ...\t3s\t..."
)

if texto.strip() != "":
    try:
        linhas = texto.strip().splitlines()
        linhas = [linha for linha in linhas if linha.strip() != ""]

        # Extrair cabeçalhos
        cabecalho = linhas[0].split('\t')
        linhas = linhas[1:]

        registros = []

        for i in range(0, len(linhas), 2):
            linha1 = linhas[i].split('\t')
            linha2 = linhas[i + 1].split('\t') if i + 1 < len(linhas) else [""] * len(cabecalho)

            registro = {}

            # Combinar colunas da linha 1 e linha 2
            for idx, nome_coluna in enumerate(cabecalho):
                val1 = linha1[idx] if idx < len(linha1) else ""
                val2 = linha2[idx] if idx < len(linha2) else ""

                if nome_coluna in ["ID", "Componente"]:
                    registro[nome_coluna] = val1
                else:
                    registro[nome_coluna] = val2 if val2 else val1

            registros.append(registro)

        df = pd.DataFrame(registros)

        st.subheader("🗂️ Dados Interpretados")
        st.dataframe(df)

        if "Componente" not in df.columns:
            st.error("⚠️ A tabela precisa ter uma coluna chamada 'Componente'. Verifique os cabeçalhos.")
        else:
            componentes = df["Componente"].map(limpar_tipo)
            contagem = componentes.value_counts().reindex(tipos, fill_value=0)

            st.subheader("⚙️ Defina os Pesos (HH:MM)")
            col1, col2 = st.columns(2)

            with col1:
                pesos_usuario = {}
                for tipo in tipos[:len(tipos)//2]:
                    valor = st.text_input(f"{tipo}:", value=pesos_padrao.get(tipo, "00:00"))
                    pesos_usuario[tipo] = valor

            with col2:
                for tipo in tipos[len(tipos)//2:]:
                    valor = st.text_input(f"{tipo}:", value=pesos_padrao.get(tipo, "00:00"))
                    pesos_usuario[tipo] = valor

            # Conversão de HH:MM para timedelta
            def hhmm_para_timedelta(hhmm):
                try:
                    h, m = map(int, hhmm.strip().split(":"))
                    return pd.Timedelta(hours=h, minutes=m)
                except:
                    return pd.Timedelta(0)

            pesos_tempo = {tipo: hhmm_para_timedelta(valor) for tipo, valor in pesos_usuario.items()}

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

    except Exception as e:
        st.error(f"Erro ao processar a tabela: {e}")

else:
    st.info("Cole uma tabela para começar.")
