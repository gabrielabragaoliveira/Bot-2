import streamlit as st
import re
import pandas as pd
import io

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Bot Separador de Levantamentos", layout="wide", page_icon="🛣️")

st.title("🛣️ Bot - Relatórios de Conserva (3 Categorias)")
st.markdown("Cole o texto do WhatsApp abaixo. O sistema irá ler o conteúdo e separar automaticamente em tabelas de Defensas, Drenagem e Sinalização.")

# Interface de Entrada
texto_bruto_input = st.text_area("WhatsApp (Cole o texto aqui):", height=200)

# Função auxiliar para gerar o arquivo Excel em memória (para o botão de download)
def gerar_excel(df):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Levantamento')
    return buffer.getvalue()

# 2. LÓGICA DE PROCESSAMENTO PRINCIPAL
if st.button("Gerar Tabelas em Sequência", type="primary", use_container_width=True):
    if texto_bruto_input:
        with st.spinner("⏳ Analisando o texto e separando as categorias..."):
            texto = texto_bruto_input.lower()
            
            # --- Extração Geral (KM e Sentido) ---
            km_match = re.search(r'km\s*(\d+\+\d+)', texto, re.IGNORECASE)
            sentido_match = re.search(r'(norte|sul|leste|oeste)', texto, re.IGNORECASE)
            
            km = km_match.group(1) if km_match else "N/A"
            sentido = sentido_match.group(1).capitalize() if sentido_match else "N/A"
            
            # Listas para guardar os resultados
            dados_defensas = []
            dados_drenagem = []
            dados_sinalizacao = []
            
            # --- Lógica: DEFENSAS ---
            if any(p in texto for p in ["lâmina", "lamina", "perfil", "defensa", "tk", "obex"]):
                laminas = sum(int(num) for num in re.findall(r'(\d+)\s*l[âa]minas?', texto))
                perfis = sum(int(num) for num in re.findall(r'(\d+)\s*perfil', texto))
                
                dados_defensas.append({
                    "KM INICIAL": km, "SENTIDO": sentido, 
                    "Quantidade de lâminas": laminas, "Quantidade de postes": perfis, 
                    "DISPOSITIVO": "Defensa Metálica"
                })

            # --- Lógica: DRENAGEM E MEIO FIO ---
            if any(p in texto for p in ["bueiro", "sarjeta", "valeta", "meio fio", "descida", "dissipador", "tampa"]):
                dados_drenagem.append({
                    "KM INICIAL": km, "SENTIDO": sentido, 
                    "DISPOSITIVO": "Elemento de Drenagem", "Observação": "Revisar texto"
                })

            # --- Lógica: SINALIZAÇÃO ---
            if any(p in texto for p in ["placa", "balizador"]):
                dados_sinalizacao.append({
                    "KM INICIAL": km, "SENTIDO": sentido, 
                    "DISPOSITIVO": "Sinalização / Balizador", "Observação": "Revisar texto"
                })

            st.divider()
            
            # 3. EXIBIÇÃO EM SEQUÊNCIA (Três colunas na tela)
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.subheader("🛡️ Defensas")
                if dados_defensas:
                    df_def = pd.DataFrame(dados_defensas)
                    st.dataframe(df_def, use_container_width=True)
                    st.download_button("Baixar Excel - Defensas", data=gerar_excel(df_def), file_name="Defensas.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                else:
                    st.info("Nenhum dado de Defensa encontrado.")
                    
            with col2:
                st.subheader("💧 Drenagem")
                if dados_drenagem:
                    df_dren = pd.DataFrame(dados_drenagem)
                    st.dataframe(df_dren, use_container_width=True)
                    st.download_button("Baixar Excel - Drenagem", data=gerar_excel(df_dren), file_name="Drenagem.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                else:
                    st.info("Nenhum dado de Drenagem encontrado.")
                    
            with col3:
                st.subheader("🛑 Sinalização")
                if dados_sinalizacao:
                    df_sin = pd.DataFrame(dados_sinalizacao)
                    st.dataframe(df_sin, use_container_width=True)
                    st.download_button("Baixar Excel - Sinalização", data=gerar_excel(df_sin), file_name="Sinalizacao.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                else:
                    st.info("Nenhum dado de Sinalização encontrado.")
                    
    else:
        st.warning("⚠️ Por favor, cole algum texto do WhatsApp antes de gerar as tabelas.")
