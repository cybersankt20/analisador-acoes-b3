import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import io

st.set_page_config(page_title="Plataforma Completa de Análise Financeira B3", layout="wide")

st.title("📊 Plataforma de Análise Fundamentalista, Valuation & Comparador B3")

# --- BARRA LATERAL: CONFIGURAÇÕES E PARÂMETROS ---
st.sidebar.header("⚙️ Parâmetros & Filtros")

# Regras Customizáveis
with st.sidebar.expander("🛠️ Personalizar Regras de Indicadores", expanded=False):
    pl_max_ideal = st.number_input("P/L Ideal Máximo", value=15.0)
    pvp_max_ideal = st.number_input("P/VP Ideal Máximo", value=1.5)
    roe_min_ideal = st.number_input("ROE Mínimo Ideal (%)", value=10.0)
    margem_min_ideal = st.number_input("Margem Líquida Mínima (%)", value=10.0)
    divida_max_ideal = st.number_input("Dívida Líq./EBITDA Máximo", value=2.5)

def buscar_dados_ativo(ticker_str):
    symbol = f"{ticker_str}.SA" if not ticker_str.endswith(".SA") else ticker_str
    stock = yf.Ticker(symbol)
    info = stock.info
    
    preco = round(info.get('currentPrice') or info.get('regularMarketPrice') or 0.0, 2)
    lpa = round(info.get('trailingEps') or 0.0, 2)
    vpa = round(info.get('bookValue') or 0.0, 2)
    dpa = round(info.get('trailingAnnualDividendRate') or 0.0, 2)
    pl = round(info.get('trailingPE') or 0.0, 2)
    pvp = round(info.get('priceToBook') or 0.0, 2)
    roe = round((info.get('returnOnEquity') or 0.0) * 100, 2)
    margem = round((info.get('profitMargins') or 0.0) * 100, 2)
    divida_ebitda = round(info.get('debtToEbitda') or 0.0, 2)
    liquidez = round(info.get('currentRatio') or 0.0, 2)
    
    return {
        "Ticker": ticker_str,
        "Preço": preco, "LPA": lpa, "VPA": vpa, "DPA": dpa,
        "P/L": pl, "P/VP": pvp, "ROE (%)": roe, "Margem Líq. (%)": margem,
        "Dívida Líq./EBITDA": divida_ebitda, "Liquidez Corrente": liquidez
    }

def avaliar_status(row):
    if row['P/L'] <= 0 or row['P/L'] > pl_max_ideal * 1.5 or row['ROE (%)'] < 0 or row['Liquidez Corrente'] < 1.0:
        return 'Crítico'
    elif row['P/L'] <= pl_max_ideal and row['P/VP'] <= pvp_max_ideal and row['ROE (%)'] >= roe_min_ideal:
        return 'Bom'
    return 'Alerta'

# --- NAVEGAÇÃO POR ABAS ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Análise Individual & Valuation", 
    "⚔️ Comparador de Ações", 
    "📈 Simulador Bola de Neve", 
    "📥 Exportar Relatório"
])

# === ABA 1: ANÁLISE INDIVIDUAL ===
with tab1:
    ticker_ind = st.text_input("Digite o Ticker da Ação (ex: PETR4, VALE3, ITUB4):", value="PETR4").upper().strip()
    if ticker_ind:
        try:
            dados = buscar_dados_ativo(ticker_ind)
            
            # Valuation
            col1, col2, col3 = st.columns(3)
            p_graham = round(np.sqrt(22.5 * dados['LPA'] * dados['VPA']), 2) if dados['LPA'] > 0 and dados['VPA'] > 0 else "N/A"
            p_bazin = round(dados['DPA'] / 0.06, 2) if dados['DPA'] > 0 else "N/A"
            
            col1.metric("Preço Justo (Graham)", f"R$ {p_graham}" if p_graham != "N/A" else "N/A")
            col2.metric("Preço Teto (Bazin 6%)", f"R$ {p_bazin}" if p_bazin != "N/A" else "N/A")
            col3.metric("Preço de Mercado Atual", f"R$ {dados['Preço']}")
            
            # Tabela de Indicadores
            df_ind = pd.DataFrame([dados]).T.reset_index()
            df_ind.columns = ["Indicador", "Valor"]
            st.subheader(f"Indicadores Fundamentalistas - {ticker_ind}")
            st.dataframe(df_ind, use_container_width=True)
        except Exception as e:
            st.error(f"Erro ao buscar dados de {ticker_ind}: {e}")

# === ABA 2: COMPARADOR DE AÇÕES ===
with tab2:
    st.subheader("⚔️ Comparação Direta Lado a Lado")
    col_a, col_b = st.columns(2)
    t1 = col_a.text_input("Ação 1:", value="PETR4").upper().strip()
    t2 = col_b.text_input("Ação 2:", value="VALE3").upper().strip()
    
    if st.button("Comparar Ações") or (t1 and t2):
        try:
            d1, d2 = buscar_dados_ativo(t1), buscar_dados_ativo(t2)
            df_comp = pd.DataFrame([d1, d2]).set_index("Ticker").T
            st.dataframe(df_comp, use_container_width=True)
        except Exception as e:
            st.error(f"Erro na comparação: {e}")

# === ABA 3: SIMULADOR BOLA DE NEVE ===
with tab3:
    st.subheader("📈 Projeção de Juros Compostos com Reinvestimento")
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    ap_inicial = col_s1.number_input("Aporte Inicial (R$)", value=5000)
    ap_mensal = col_s2.number_input("Aporte Mensal (R$)", value=500)
    anos_sim = col_s3.slider("Anos de Investimento", 1, 30, 10)
    dy_sim = col_s4.number_input("Dividend Yield Anual (%)", value=8.0)
    
    meses = anos_sim * 12
    taxa_dy_m = (1 + dy_sim/100)**(1/12) - 1
    
    patrimonio = ap_inicial
    total_inv = ap_inicial
    hist = []
    
    for m in range(1, meses + 1):
        div = patrimonio * taxa_dy_m
        patrimonio += div + ap_mensal
        total_inv += ap_mensal
        if m % 12 == 0:
            hist.append({"Ano": m//12, "Total Investido": round(total_inv, 2), "Patrimônio com Dividendos": round(patrimonio, 2)})
            
    df_sim = pd.DataFrame(hist)
    fig = px.line(df_sim, x="Ano", y=["Total Investido", "Patrimônio com Dividendos"], title="Evolução Patrimonial")
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

# === ABA 4: EXPORTAÇÃO DE RELATÓRIO ===
with tab4:
    st.subheader("📥 Exportar Dados para Planilhas")
    if 'df_ind' in locals():
        # Exportar CSV
        csv_buffer = df_ind.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📄 Baixar Relatório em CSV",
            data=csv_buffer,
            file_name=f"Relatorio_{ticker_ind}.csv",
            mime="text/csv"
        )
        
        # Exportar Excel
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df_ind.to_excel(writer, sheet_name="Analise", index=False)
        excel_buffer.seek(0)
        
        st.download_button(
            label="📊 Baixar Relatório em Excel (.xlsx)",
            data=excel_buffer,
            file_name=f"Relatorio_{ticker_ind}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("Realize uma consulta na Aba 1 para gerar o relatório de download.")