import streamlit as st
import re
import pandas as pd
import io

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Bot Separador de Levantamentos", layout="wide", page_icon="🛣️")

st.title("🛣️ Bot - Relatórios de Conserva (3 Categorias)")
st.markdown("Cole o histórico do WhatsApp abaixo. O bot ignora horas/nomes e separa os itens por KM automaticamente.")

texto_bruto_input = st.text_area("WhatsApp (Cole o texto aqui):", height=250)

def gerar_excel(df):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Levantamento')
    return buffer.getvalue()

# 2. LÓGICA DE PROCESSAMENTO
if st.button("Gerar Tabelas em Sequência", type="primary", use_container_width=True):
    if texto_bruto_input:
        with st.spinner("⏳ Analisando e limpando o texto do WhatsApp..."):
            
            # --- PASSO A: Limpar o "lixo" do WhatsApp ---
            # Remove o padrão: [11:14, 17/01/2026] Nome Afirma:
            texto_limpo = re.sub(r'\[\d{2}:\d{2}.*?\].*?:', '\n', texto_bruto_input)
            texto_limpo = texto_limpo.lower()
            
            # --- PASSO B: Separar por KMs ---
            # Corta o texto em pedaços toda vez que achar "km " seguido de números
            # Assim, você pode colar o dia inteiro de trabalho e ele cria várias linhas!
            blocos = re.split(r'(?i)(?=km\s*\d+)', texto_limpo)
            
            dados_defensas = []
            dados_drenagem = []
            dados_sinalizacao = []
            
            # Analisa cada bloco de KM individualmente
            for bloco in blocos:
                if not bloco.strip():
                    continue # Pula blocos vazios
                
                # Procura o KM e o Sentido DENTRO deste bloco específico
                km_match = re.search(r'km\s*(\d+\+\d+)', bloco)
                sentido_match = re.search(r'(norte|sul|leste|oeste)', bloco)
                
                km = km_match.group(1) if km_match else "N/A"
                sentido = sentido_match.group(1).capitalize() if sentido_match else "N/A"
                
                # Ignora blocos que não tenham pelo menos um KM válido
                if km == "N/A":
                    continue

                # --- Lógica: DEFENSAS ---
                if any(p in bloco for p in ["lâmina", "lamina", "perfil", "perfis", "defensa", "tk", "obex"]):
                    # Somando lâminas (lâmina ou lâminas)
                    laminas = sum(int(num) for num in re.findall(r'(\d+)\s*l[âa]minas?', bloco))
                    # Somando perfis (perfil ou perfis)
                    perfis = sum(int(num) for num in re.findall(r'(\d+)\s*perfi[ls]?', bloco))
                    
                    dados_defensas.append({
                        "KM INICIAL": km, "SENTIDO": sentido, 
                        "Quantidade de lâminas": laminas, "Quantidade de postes": perfis, 
                        "DISPOSITIVO": "Defensa Metálica"
                    })

                # --- Lógica: DRENAGEM E MEIO FIO ---
                if any(p in bloco for p in ["bueiro", "sarjeta", "valeta", "meio fio", "descida", "dissipador", "tampa"]):
                    dados_drenagem.append({
                        "KM INICIAL": km, "SENTIDO": sentido, 
                        "DISPOSITIVO": "Elemento de Drenagem", "Observação": "Revisar quantidades no texto"
                    })

                # --- Lógica: SINALIZAÇÃO ---
                if any(p in bloco for p in ["placa", "balizador"]):
                    dados_sinalizacao.append({
                        "KM INICIAL": km, "SENTIDO": sentido, 
                        "DISPOSITIVO": "Sinalização / Balizador", "Observação": "Revisar texto"
                    })

            st.divider()
            
            # 3. EXIBIÇÃO DAS TABELAS
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.subheader("🛡️ Defensas")
                if dados_defensas:
                    df_def = pd.DataFrame(dados_defensas)
                    st.dataframe(df_def, use_container_width=True)
                    st.download_button("Baixar - Defensas", data=gerar_excel(df_def), file_name="Defensas.xlsx")
                else:
                    st.info("Nenhum dado.")
                    
            with col2:
                st.subheader("💧 Drenagem")
                if dados_drenagem:
                    df_dren = pd.DataFrame(dados_drenagem)
                    st.dataframe(df_dren, use_container_width=True)
                    st.download_button("Baixar - Drenagem", data=gerar_excel(df_dren), file_name="Drenagem.xlsx")
                else:
                    st.info("Nenhum dado.")
                    
            with col3:
                st.subheader("🛑 Sinalização")
                if dados_sinalizacao:
                    df_sin = pd.DataFrame(dados_sinalizacao)
                    st.dataframe(df_sin, use_container_width=True)
                    st.download_button("Baixar - Sinalização", data=gerar_excel(df_sin), file_name="Sinalizacao.xlsx")
                else:
                    st.info("Nenhum dado.")
                    
    else:
        st.warning("⚠️ Por favor, cole algum texto do WhatsApp antes de processar.")
