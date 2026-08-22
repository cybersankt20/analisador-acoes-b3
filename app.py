import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io

# 1. Configuração da Página
st.set_page_config(
    page_title="Terminal B3 Pro | Analytics",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Injeção de CSS Customizado (UI/UX Premium + Hover Effects)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Cards com efeito de elevação e transição no mouse */
    .ux-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 22px;
        margin-bottom: 15px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        backdrop-filter: blur(12px);
    }
    
    .ux-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 12px 28px rgba(0, 230, 118, 0.15);
        border-color: rgba(0, 230, 118, 0.4);
    }

    /* Métricas estilizadas */
    .metric-title {
        font-size: 0.85rem;
        color: #A0AEC0;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #FFFFFF;
        margin-top: 5px;
    }
    
    .metric-sub {
        font-size: 0.8rem;
        color: #00E676;
        margin-top: 2px;
    }

    /* Badges / Veredito */
    .badge-approved {
        background: linear-gradient(135deg, #00E676, #00B0FF);
        color: #000;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: 700;
        display: inline-block;
    }

    .badge-rejected {
        background: linear-gradient(135deg, #FF1744, #FF5252);
        color: #FFF;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: 700;
        display: inline-block;
    }

    /* Ajustes na sidebar */
    .css-1d37Wk {
        background-color: #0E1117;
    }
</style>
""", unsafe_allow_html=True)

# 3. Função Cacheada para Alta Performance
@st.cache_data(ttl=3600)
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

# 4. Cabeçalho Principal
st.markdown("<h1>⚡ Terminal B3 <span style='color:#00E676;'>Analytics Pro</span></h1>", unsafe_allow_html=True)
st.caption("Painel interativo de análise fundamentalista, valuation e projeção patrimonial em tempo real.")

# 5. Sidebar de Parâmetros
st.sidebar.markdown("### ⚙️ Parâmetros do Filtro")
pl_max_ideal = st.sidebar.number_input("P/L Máximo Recomendado", value=15.0)
pvp_max_ideal = st.sidebar.number_input("P/VP Máximo Recomendado", value=1.5)
roe_min_ideal = st.sidebar.number_input("ROE Mínimo (%)", value=10.0)

# 6. Abas Navegáveis com Ícones
tab1, tab2, tab3, tab4 = st.tabs([
    "🎯 Valuation & Resumo", 
    "⚔️ Comparador Side-by-Side", 
    "🚀 Simulador Bola de Neve", 
    "📥 Central de Downloads"
])

# === ABA 1: VALUATION & RESUMO ===
with tab1:
    c1, c2 = st.columns([1, 3])
    with c1:
        ticker_ind = st.text_input("🔍 Buscar Ativo:", value="PETR4").upper().strip()
    
    if ticker_ind:
        try:
            dados = buscar_dados_ativo(ticker_ind)
            p_graham = round(np.sqrt(22.5 * dados['LPA'] * dados['VPA']), 2) if dados['LPA'] > 0 and dados['VPA'] > 0 else "N/A"
            p_bazin = round(dados['DPA'] / 0.06, 2) if dados['DPA'] > 0 else "N/A"
            
            # Cards Interativos com Hover Effect
            st.markdown("### 📊 Modelos de Valuation")
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                st.markdown(f"""
                <div class="ux-card">
                    <div class="metric-title">📐 Preço Justo Graham</div>
                    <div class="metric-value">R$ {p_graham}</div>
                    <div class="metric-sub">Baseado em Lucro e Patrimônio</div>
                </div>
                """, unsafe_allow_html=True)
                
            with col_b:
                st.markdown(f"""
                <div class="ux-card">
                    <div class="metric-title">🛡️ Preço Teto Bazin (6%)</div>
                    <div class="metric-value">R$ {p_bazin}</div>
                    <div class="metric-sub">Baseado nos Proventos Pagos</div>
                </div>
                """, unsafe_allow_html=True)

            with col_c:
                st.markdown(f"""
                <div class="ux-card">
                    <div class="metric-title">🏷️ Cotação Atual</div>
                    <div class="metric-value" style="color: #00B0FF;">R$ {dados['Preço']}</div>
                    <div class="metric-sub">Valor de Mercado B3</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Diagnostic Card
            status = "APROVADO" if (dados['P/L'] <= pl_max_ideal and dados['ROE (%)'] >= roe_min_ideal) else "ATENÇÃO / REPROVADO"
            badge_class = "badge-approved" if status == "APROVADO" else "badge-rejected"
            
            st.markdown(f"""
            <div class="ux-card">
                <span class="metric-title">Veredito do Filtro:</span>
                <span class="{badge_class}">{status}</span>
            </div>
            """, unsafe_allow_html=True)
            
            # Tabela de Indicadores Formatada
            df_ind = pd.DataFrame([dados]).T.reset_index()
            df_ind.columns = ["Indicador Fundamentalista", "Valor"]
            st.dataframe(df_ind, use_container_width=True, hide_index=True)

        except Exception as e:
            st.error(f"Erro ao carregar dados do ativo: {e}")

# === ABA 2: COMPARADOR ===
with tab2:
    st.markdown("### ⚔️ Comparação Lado a Lado")
    ca, cb = st.columns(2)
    t1 = ca.text_input("Ação 1:", value="PETR4").upper().strip()
    t2 = cb.text_input("Ação 2:", value="VALE3").upper().strip()
    
    if t1 and t2:
        try:
            d1, d2 = buscar_dados_ativo(t1), buscar_dados_ativo(t2)
            df_comp = pd.DataFrame([d1, d2]).set_index("Ticker").T
            
            st.dataframe(df_comp, use_container_width=True)
            
            # Gráfico de Radar Interativo
            categories = ['P/L', 'P/VP', 'ROE (%)', 'Margem Líq. (%)']
            fig_radar = go.Figure()

            fig_radar.add_trace(go.Scatterpolar(
                r=[d1['P/L'], d1['P/VP'], d1['ROE (%)'], d1['Margem Líq. (%)']],
                theta=categories, fill='toself', name=t1
            ))
            fig_radar.add_trace(go.Scatterpolar(
                r=[d2['P/L'], d2['P/VP'], d2['ROE (%)'], d2['Margem Líq. (%)']],
                theta=categories, fill='toself', name=t2
            ))

            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 40])),
                showlegend=True, template="plotly_dark", height=400
            )
            st.plotly_chart(fig_radar, use_container_width=True)
            
        except Exception as e:
            st.error(f"Erro na comparação: {e}")

# === ABA 3: SIMULADOR ===
with tab3:
    st.markdown("### 📈 Projeção Patrimonial Interativa")
    cs1, cs2, cs3, cs4 = st.columns(4)
    ap_ini = cs1.number_input("Aporte Inicial (R$)", value=10000)
    ap_men = cs2.number_input("Aporte Mensal (R$)", value=1000)
    anos = cs3.slider("Período (Anos)", 1, 30, 15)
    dy = cs4.number_input("Dividend Yield Esperado (% a.a.)", value=8.5)
    
    meses = anos * 12
    taxa_m = (1 + dy/100)**(1/12) - 1
    
    patrimonio, investido = ap_ini, ap_ini
    historico = []
    
    for m in range(1, meses + 1):
        div = patrimonio * taxa_m
        patrimonio += div + ap_men
        investido += ap_men
        if m % 12 == 0:
            historico.append({
                "Ano": m // 12,
                "Investido": round(investido, 2),
                "Com Reinvestimento": round(patrimonio, 2)
            })
            
    df_sim = pd.DataFrame(historico)
    
    # Gráfico de Área Interativo
    fig = px.area(
        df_sim, x="Ano", y=["Com Reinvestimento", "Investido"],
        title="Efeito Bola de Neve no Patrimônio (Juros Compostos)",
        color_discrete_sequence=["#00E676", "#00B0FF"]
    )
    fig.update_layout(template="plotly_dark", hovermode="x unified", height=420)
    st.plotly_chart(fig, use_container_width=True)

# === ABA 4: DOWNLOADS ===
with tab4:
    st.markdown("### 📥 Baixar Relatório Customizado")
    if 'df_ind' in locals():
        col_d1, col_d2 = st.columns(2)
        
        csv_data = df_ind.to_csv(index=False).encode('utf-8')
        col_d1.download_button(
            "📄 Download em CSV", data=csv_data,
            file_name=f"Analise_{ticker_ind}.csv", mime="text/csv", use_container_width=True
        )
        
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df_ind.to_excel(writer, sheet_name="Resumo", index=False)
        excel_buffer.seek(0)
        
        col_d2.download_button(
            "📊 Download em Excel (.xlsx)", data=excel_buffer,
            file_name=f"Analise_{ticker_ind}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    else:
        st.info("Consulte uma ação na primeira aba para habilitar o download.")
