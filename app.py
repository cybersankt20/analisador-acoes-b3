import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io

# -----------------------------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Terminal B3 Pro | Analytics",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# 2. ESTILIZAÇÃO CSS CUSTOMIZADA
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Cards em Grid */
    .ux-card {
        background-color: #1A1D24 !important;
        border: 1px solid #2D3748 !important;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        transition: all 0.3s ease;
    }
    
    .ux-card:hover {
        transform: translateY(-3px);
        border-color: #00E676 !important;
        box-shadow: 0 8px 20px rgba(0, 230, 118, 0.2);
    }

    .metric-title {
        font-size: 0.82rem;
        color: #A0AEC0 !important;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-value {
        font-size: 1.7rem;
        font-weight: 800;
        color: #00E676 !important;
        margin-top: 6px;
    }

    .metric-value-blue {
        font-size: 1.7rem;
        font-weight: 800;
        color: #00B0FF !important;
        margin-top: 6px;
    }
    
    .metric-sub {
        font-size: 0.8rem;
        color: #CBD5E0 !important;
        margin-top: 4px;
    }

    /* Header da Empresa */
    .company-header {
        background: linear-gradient(135deg, #1A1D24, #2D3748);
        border: 1px solid #00E676;
        border-radius: 16px;
        padding: 22px;
        margin-bottom: 25px;
        color: #FFFFFF !important;
    }

    .badge-approved {
        background: #00E676;
        color: #000000 !important;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: 700;
        display: inline-block;
    }

    .badge-rejected {
        background: #FF5252;
        color: #FFFFFF !important;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: 700;
        display: inline-block;
    }

    /* Tabela Customizada */
    .custom-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 15px;
        background-color: #1A1D24;
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #2D3748;
    }
    .custom-table th {
        background-color: #2D3748;
        color: #A0AEC0;
        padding: 14px 18px;
        text-align: left;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .custom-table td {
        padding: 14px 18px;
        border-bottom: 1px solid #2D3748;
        color: #FFFFFF;
        font-size: 0.95rem;
    }
    .custom-table tr:last-child td {
        border-bottom: none;
    }
    .custom-table tr:hover {
        background-color: #222732;
    }

    /* Tooltip Interativo */
    .tooltip-icon {
        position: relative;
        display: inline-block;
        cursor: pointer;
        color: #00B0FF;
        margin-left: 8px;
        font-weight: bold;
    }
    .tooltip-icon .tooltip-text {
        visibility: hidden;
        width: 290px;
        background-color: #2D3748;
        color: #FFFFFF;
        text-align: left;
        border-radius: 8px;
        padding: 10px 14px;
        position: absolute;
        z-index: 999;
        bottom: 125%;
        left: 50%;
        transform: translateX(-50%);
        opacity: 0;
        transition: opacity 0.2s ease-in-out;
        font-size: 0.82rem;
        font-weight: normal;
        box-shadow: 0px 8px 20px rgba(0, 0, 0, 0.5);
        border: 1px solid #00E676;
        line-height: 1.4;
    }
    .tooltip-icon:hover .tooltip-text {
        visibility: visible;
        opacity: 1;
    }
</style>
""", unsafe_allow_html=True)

# Lista completa de ações B3
ACOES_B3 = sorted([
    "PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA", "BBAS3.SA", "ABEV3.SA",
    "WEGE3.SA", "RENT3.SA", "ELET3.SA", "SUZB3.SA", "BPAC11.SA", "EQTL3.SA",
    "PRIO3.SA", "GGBR4.SA", "RADL3.SA", "RAIL3.SA", "SBSP3.SA", "VBBR3.SA",
    "B3SA3.SA", "CSAN3.SA", "CPLE6.SA", "EGIE3.SA", "TAEE11.SA", "CMIG4.SA",
    "KLBN11.SA", "VIVT3.SA", "TIMS3.SA", "HYPE3.SA", "TOTS3.SA", "FLRY3.SA",
    "SANB11.SA", "ALUP11.SA", "TRPL4.SA", "BBSE3.SA", "PSSA3.SA", "CXSE3.SA",
    "SAPR11.SA", "CSMG3.SA", "EMBR3.SA", "MULT3.SA", "UGPA3.SA", "LREN3.SA"
])

# -----------------------------------------------------------------------------
# 3. BUSCA DE DADOS FINANCEIROS CACHEADA
# -----------------------------------------------------------------------------
@st.cache_data(ttl=3600)
def buscar_dados_ativo(ticker_str):
    try:
        ticker = yf.Ticker(ticker_str)
        info = ticker.info
        
        preco_atual = info.get('currentPrice') or info.get('regularMarketPrice') or 0.0
        lpa = info.get('trailingEps') or 0.0
        vpa = info.get('bookValue') or 0.0
        
        # Cálculo de Preço Justo Graham
        preco_graham = np.sqrt(22.5 * lpa * vpa) if (lpa > 0 and vpa > 0) else 0.0
        
        # Dividend Yield e Preço Teto Bazin
        dy = (info.get('dividendYield') or 0.0)
        dy_pct = dy * 100 if dy < 1.0 else dy
        dpa = (dy_pct / 100) * preco_atual if dy_pct > 0 else 0.0
        preco_bazin = dpa / 0.06 if dpa > 0 else 0.0
        
        # Indicadores Fundamentalistas
        pl = info.get('trailingPE') or 0.0
        pvp = info.get('priceToBook') or 0.0
        roe = (info.get('returnOnEquity') or 0.0) * 100
        margem_liquida = (info.get('profitMargins') or 0.0) * 100
        liquidez_corrente = info.get('currentRatio') or 0.0
        
        divida_total = info.get('totalDebt') or 0.0
        caixa = info.get('totalCash') or 0.0
        divida_liquida = divida_total - caixa
        ebitda = info.get('ebitda') or 1.0
        divida_ebitda = divida_liquida / ebitda if ebitda > 0 else 0.0
        
        return {
            "symbol": ticker_str.replace(".SA", ""),
            "nome": info.get('longName', ticker_str),
            "setor": info.get('sector', 'N/D'),
            "preco": preco_atual,
            "graham": preco_graham,
            "bazin": preco_bazin,
            "pl": pl,
            "pvp": pvp,
            "roe": roe,
            "dy": dy_pct,
            "margem_liquida": margem_liquida,
            "divida_ebitda": divida_ebitda,
            "liquidez_corrente": liquidez_corrente,
            "lpa": lpa,
            "vpa": vpa
        }
    except Exception:
        return None

# -----------------------------------------------------------------------------
# 4. SIDEBAR - PARÂMETROS DO FILTRO FUNDAMENTALISTA
# -----------------------------------------------------------------------------
st.sidebar.markdown("## ⚙️ Parâmetros do Filtro")
st.sidebar.caption("Ajuste suas réguas de segurança:")

pl_max = st.sidebar.number_input("P/L Máximo Recomendado", value=15.0, step=1.0)
pvp_max = st.sidebar.number_input("P/VP Máximo Recomendado", value=1.5, step=0.1)
roe_min = st.sidebar.number_input("ROE Mínimo (%)", value=10.0, step=1.0)
dy_min = st.sidebar.number_input("Dividend Yield Mínimo (%)", value=6.0, step=0.5)
divida_max = st.sidebar.number_input("Dívida Líq. / EBITDA Máxima", value=2.5, step=0.5)
margem_min = st.sidebar.number_input("Margem Líquida Mínima (%)", value=10.0, step=1.0)
liq_min = st.sidebar.number_input("Liquidez Corrente Mínima", value=1.0, step=0.1)

# -----------------------------------------------------------------------------
# 5. HEADER PRINCIPAL
# -----------------------------------------------------------------------------
st.title("⚡ Terminal B3 Pro — Valuation & Screener")
st.markdown("Análise fundamentalista em tempo real, valuation automático (Graham e Bazin) e simulador de dividendos.")

tabs = st.tabs(["📊 Valuation & Resumo", "⚔️ Comparador Lado a Lado", "📈 Simulador Bola de Neve", "📥 Central de Downloads"])

# -----------------------------------------------------------------------------
# TAB 1: VALUATION & RESUMO
# -----------------------------------------------------------------------------
with tabs[0]:
    col_sel, _ = st.columns([1, 2])
    with col_sel:
        ticker_input = st.selectbox(
            "Digite ou selecione uma ação da B3:",
            ACOES_B3,
            index=0
        )
    
    dados = buscar_dados_ativo(ticker_input)
    
    if dados:
        # Verificação dos critérios do filtro
        aprovado = (
            dados['pl'] <= pl_max and
            dados['pvp'] <= pvp_max and
            dados['roe'] >= roe_min and
            dados['dy'] >= dy_min and
            dados['divida_ebitda'] <= divida_max and
            dados['margem_liquida'] >= margem_min and
            dados['liquidez_corrente'] >= liq_min
        )

        # Banner do Ativo
        badge_html = f'<span class="badge-approved">AÇÃO APROVADA NOS SEUS FILTROS</span>' if aprovado else f'<span class="badge-rejected">ATENÇÃO: ALGUNS INDICADORES FORA DO LIMITE</span>'
        
        st.markdown(f"""
        <div class="company-header">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <h2 style="margin:0; font-weight:800; color:#FFFFFF;">{dados['nome']} ({dados['symbol']})</h2>
                    <p style="margin:4px 0 0 0; color:#A0AEC0;">Setor: <b>{dados['setor']}</b></p>
                </div>
                <div>{badge_html}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.subheader("📊 Modelos de Valuation Automáticos")
        
        desc_graham = ((dados['graham'] - dados['preco']) / dados['preco']) * 100 if dados['preco'] > 0 else 0
        desc_bazin = ((dados['bazin'] - dados['preco']) / dados['preco']) * 100 if dados['preco'] > 0 else 0
        
        c1, c2, c3 = st.columns(3)
        
        with c1:
            st.markdown(f"""
            <div class="ux-card">
                <div class="metric-title">📐 Preço Justo Graham</div>
                <div class="metric-value">R$ {dados['graham']:.2f}</div>
                <div class="metric-sub">Margem/Desconto: <b>{desc_graham:+.1f}%</b></div>
            </div>
            """, unsafe_allow_html=True)
            
        with c2:
            st.markdown(f"""
            <div class="ux-card">
                <div class="metric-title">🛡️ Preço Teto Bazin (6%)</div>
                <div class="metric-value-blue">R$ {dados['bazin']:.2f}</div>
                <div class="metric-sub">Margem/Desconto: <b>{desc_bazin:+.1f}%</b></div>
            </div>
            """, unsafe_allow_html=True)
            
        with c3:
            veredicto_txt = "APROVADA" if aprovado else "ATENÇÃO"
            veredicto_cor = "#00E676" if aprovado else "#FF5252"
            st.markdown(f"""
            <div class="ux-card">
                <div class="metric-title">🎯 Veredito dos Filtros</div>
                <div class="metric-value" style="color:{veredicto_cor} !important;">{veredicto_txt}</div>
                <div class="metric-sub">Baseado nos Limites da Sidebar</div>
            </div>
            """, unsafe_allow_html=True)

        st.subheader("📜 Indicadores Fundamentalistas Detalhados")
        
        # Gerar linhas da tabela sem espaços de recuo nas linhas para evitar que o Markdown crie bloco de código
        indicadores_info = [
            ("💵 Preço Atual", f"R$ {dados['preco']:.2f}", "Cotação em tempo real negociada na B3."),
            ("📐 Preço Justo (Graham)", f"R$ {dados['graham']:.2f}", "Fórmula: √(22.5 × LPA × VPA). Teto de preço pago por ações de valor."),
            ("🛡️ Preço Teto (Bazin 6%)", f"R$ {dados['bazin']:.2f}", "Preço teto para garantir no mínimo 6% a.a. em dividendos."),
            ("📊 P/L (Preço / Lucro)", f"{dados['pl']:.2f}", f"Anos para reaver investimento. Seu teto: {pl_max:.1f}"),
            ("📘 P/VP (Preço / Valor Patrimonial)", f"{dados['pvp']:.2f}", f"Relação preço/patrimônio. Seu teto: {pvp_max:.1f}"),
            ("💎 Dividend Yield (12M)", f"{dados['dy']:.2f}%", f"Rendimento anual em proventos. Seu piso: {dy_min:.1f}%"),
            ("🚀 ROE (Retorno s/ Patrimônio)", f"{dados['roe']:.2f}%", f"Capacidade de gerar lucro com capital próprio. Seu piso: {roe_min:.1f}%"),
            ("💸 Margem Líquida", f"{dados['margem_liquida']:.2f}%", f"Porcentagem da receita que vira lucro líquido. Seu piso: {margem_min:.1f}%"),
            ("🧱 Dívida Líq. / EBITDA", f"{dados['divida_ebitda']:.2f}x", f"Alavancagem financeira. Seu teto: {divida_max:.1f}x"),
            ("💧 Liquidez Corrente", f"{dados['liquidez_corrente']:.2f}", f"Capacidade de honrar compromissos no curto prazo. Seu piso: {liq_min:.1f}")
        ]

        # Construção da tabela garantindo formatação HTML pura sem indentação de código Markdown
        rows_list = []
        for ind, val, exp in indicadores_info:
            rows_list.append(
                f'<tr><td style="font-weight:600;">{ind}</td>'
                f'<td style="font-weight:700; color:#00E676;">{val}</td>'
                f'<td><span class="tooltip-icon">❓<span class="tooltip-text">{exp}</span></span></td></tr>'
            )
        
        html_rows = "".join(rows_list)
        
        html_table = (
            '<table class="custom-table">'
            '<thead><tr>'
            '<th>Indicador</th>'
            '<th>Valor Apurado</th>'
            '<th>Regra de Análise & Conceito (Passe o mouse no ❓)</th>'
            '</tr></thead>'
            f'<tbody>{html_rows}</tbody>'
            '</table>'
        )

        # Exibição correta como HTML no Streamlit
        st.markdown(html_table, unsafe_allow_html=True)

    else:
        st.error("Não foi possível carregar os dados deste ativo. Tente outro ticker.")

# -----------------------------------------------------------------------------
# TAB 2: COMPARADOR LADO A LADO
# -----------------------------------------------------------------------------
with tabs[1]:
    st.subheader("⚔️ Comparação Fundamentalista de Ações")
    c1, c2 = st.columns(2)
    with c1:
        at1 = st.selectbox("Escolha o primeiro ativo:", ACOES_B3, index=0, key="c_at1")
    with c2:
        at2 = st.selectbox("Escolha o segundo ativo:", ACOES_B3, index=1, key="c_at2")
        
    d1 = buscar_dados_ativo(at1)
    d2 = buscar_dados_ativo(at2)
    
    if d1 and d2:
        comp_df = pd.DataFrame({
            "Indicador": ["Preço (R$)", "P/L", "P/VP", "Dividend Yield (%)", "ROE (%)", "Margem Líq. (%)", "Dívida/EBITDA"],
            d1['symbol']: [d1['preco'], d1['pl'], d1['pvp'], d1['dy'], d1['roe'], d1['margem_liquida'], d1['divida_ebitda']],
            d2['symbol']: [d2['preco'], d2['pl'], d2['pvp'], d2['dy'], d2['roe'], d2['margem_liquida'], d2['divida_ebitda']]
        })
        
        col_tb, col_chart = st.columns([1, 1])
        
        with col_tb:
            st.markdown("#### 📊 Tabela Comparativa")
            st.dataframe(comp_df.style.format(precision=2), use_container_width=True, hide_index=True)
            
        with col_chart:
            st.markdown("#### 🕸️ Gráfico Radar de Qualidade")
            categories = ['ROE', 'Dividend Yield', 'Margem Líquida', 'P/L Inverso']
            
            # Normalização simples para exibição no gráfico radar
            v1 = [min(d1['roe'], 40), min(d1['dy'], 20), min(d1['margem_liquida'], 40), max(0, 20 - d1['pl'])]
            v2 = [min(d2['roe'], 40), min(d2['dy'], 20), min(d2['margem_liquida'], 40), max(0, 20 - d2['pl'])]
            
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(r=v1, theta=categories, fill='toself', name=d1['symbol'], line_color='#00E676'))
            fig.add_trace(go.Scatterpolar(r=v2, theta=categories, fill='toself', name=d2['symbol'], line_color='#00B0FF'))
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 40])),
                showlegend=True,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#FFFFFF')
            )
            st.plotly_chart(fig, use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 3: SIMULADOR BOLA DE NEVE
# -----------------------------------------------------------------------------
with tabs[2]:
    st.subheader("📈 Simulador de Efeito Bola de Neve (Proventos Reinvestidos)")
    
    col_inputs, col_sim = st.columns([1, 2])
    
    with col_inputs:
        aport_inicial = st.number_input("Aporte Inicial (R$):", value=10000.0, step=1000.0)
        aporte_mensal = st.number_input("Aporte Mensal (R$):", value=1000.0, step=100.0)
        dy_anual_sim = st.slider("Dividend Yield Anual Esperado (%)", 3.0, 15.0, 8.0)
        anos = st.slider("Tempo de Investimento (Anos)", 1, 30, 10)
        
    months = anos * 12
    rate_monthly = (1 + dy_anual_sim / 100) ** (1/12) - 1
    
    patrimonio = aport_inicial
    historico = []
    
    total_investido = aport_inicial
    total_proventos = 0
    
    for m in range(1, months + 1):
        provento_mes = patrimonio * rate_monthly
        total_proventos += provento_mes
        patrimonio += provento_mes + aporte_mensal
        total_investido += aporte_mensal
        
        historico.append({
            "Mês": m,
            "Total Investido": total_investido,
            "Patrimônio Acumulado": patrimonio,
            "Provento Mensal ESTIMADO": provento_mes
        })
        
    df_sim = pd.DataFrame(historico)
    
    with col_sim:
        m1, m2 = st.columns(2)
        m1.metric("Patrimônio Final Estimado", f"R$ {patrimonio:,.2f}")
        m2.metric("Provento Mensal Estimado no Final", f"R$ {df_sim.iloc[-1]['Provento Mensal ESTIMADO']:,.2f}")
        
        fig_sim = px.area(
            df_sim, 
            x="Mês", 
            y=["Total Investido", "Patrimônio Acumulado"],
            title="Evolução do Patrimônio x Total Investido",
            color_discrete_sequence=['#2D3748', '#00E676']
        )
        fig_sim.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#FFFFFF')
        )
        st.plotly_chart(fig_sim, use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 4: CENTRAL DE DOWNLOADS
# -----------------------------------------------------------------------------
with tabs[3]:
    st.subheader("📥 Exportação de Dados em Excel e CSV")
    st.markdown("Baixe relatórios completos dos ativos analisados para utilizar no Excel ou Google Planilhas.")
    
    lista_relatorio = []
    with st.spinner("Gerando base de dados para exportação..."):
        for tk in ACOES_B3[:15]:
            d = buscar_dados_ativo(tk)
            if d:
                lista_relatorio.append(d)
                
    df_exp = pd.DataFrame(lista_relatorio)
    
    col_d1, col_d2 = st.columns(2)
    
    with col_d1:
        csv_data = df_exp.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📄 Baixar Relatório em CSV",
            data=csv_data,
            file_name="relatorio_acoes_b3.csv",
            mime="text/csv",
            use_container_width=True
        )
        
    with col_d2:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_exp.to_excel(writer, index=False, sheet_name="Ações B3")
        buffer.seek(0)
        
        st.download_button(
            label="📊 Baixar Relatório em Excel (.xlsx)",
            data=buffer,
            file_name="relatorio_acoes_b3.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
