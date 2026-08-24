import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io
import database as db

# Inicializa as tabelas do banco de dados
db.init_db()
# 1. Configuração da Página
st.set_page_config(
    page_title="CyberSankt20 B3 Pro | Analytics",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Injeção de CSS Customizado (Cores e Temas Fixos)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Cards com fundo escuro fixo para visibilidade */
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

    /* Badges */
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
</style>
""", unsafe_allow_html=True)
# --- GERENCIAMENTO DE SESSÃO ---
if "logado" not in st.session_state:
    st.session_state["logado"] = False
if "usuario" not in st.session_state:
    st.session_state["usuario"] = None

# --- TELA DE LOGIN / CADASTRO ---
if not st.session_state["logado"]:
    st.title("⚡ Terminal B3 Pro — Acesso Restrito")
    
    tab_login, tab_cadastro, tab_reset = st.tabs(["🔒 Entrar", "📝 Criar Conta", "🔑 Esqueci a Senha"])
    
    with tab_login:
        with st.form("form_login"):
            username = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar"):
                user = db.autenticar_usuario(username, senha)
                if user:
                    st.session_state["logado"] = True
                    st.session_state["usuario"] = user
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")
                    
    with tab_cadastro:
        with st.form("form_cadastro"):
            novo_user = st.text_input("Novo Usuário")
            novo_email = st.text_input("E-mail")
            nova_senha = st.text_input("Nova Senha", type="password")
            if st.form_submit_button("Cadastrar"):
                if novo_user and novo_email and nova_senha:
                    sucesso, msg = db.criar_usuario(novo_user, novo_email, nova_senha)
                    if sucesso:
                        st.success(msg)
                    else:
                        st.warning(msg)
                else:
                    st.error("Preencha todos os campos.")
    
    with tab_reset:
        with st.form("form_reset"):
            st.subheader("Redefinir Senha")
            usuario_reset = st.text_input("Usuário")
            nova_senha = st.text_input("Nova Senha", type="password")
            confirmar_senha = st.text_input("Confirme a Nova Senha", type="password")
            
            if st.form_submit_button("Alterar Senha"):
                if not usuario_reset or not nova_senha:
                    st.warning("Preencha todos os campos.")
                elif nova_senha != confirmar_senha:
                    st.error("As senhas não coincidem.")
                else:
                    if db.redefinir_senha(usuario_reset, nova_senha):
                        st.success("Senha alterada com sucesso! Volte para a aba Entrar.")
                    else:
                        st.error("Usuário não encontrado.")                
                    
    st.stop() # Bloqueia o carregamento do restante da página para usuários não autenticados
# 3. Lista Pré-carregada para Autocompletar na B3
ACOES_B3 = [
    "PETR4 - Petrobras PN",
    "VALE3 - Vale ON",
    "ITUB4 - Itaú Unibanco PN",
    "BBAS3 - Banco do Brasil ON",
    "BBDC4 - Bradesco PN",
    "WEGE3 - WEG ON",
    "ABEV3 - Ambev ON",
    "RENT3 - Localiza ON",
    "ELET3 - Eletrobras ON",
    "SUZB3 - Suzano ON",
    "JBSS3 - JBS ON",
    "LREN3 - Lojas Renner ON",
    "PRIO3 - Prio ON",
    "VBBR3 - Vibra Energia ON",
    "EQTL3 - Equatorial ON",
    "RADL3 - Raia Drogasil ON",
    "B3SA3 - B3 ON",
    "GGBR4 - Gerdau PN",
    "CSAN3 - Cosan ON",
    "CPLE6 - Copel PNB",
    "TAEE11 - Taesa Unt",
    "KLBN11 - Klabin Unt",
    "CMIG4 - Cemig PN",
    "EGIE3 - Engie Brasil ON",
    "MGLU3 - Magazine Luiza ON",
    "🔍 Outro Ticker (Digitar manualmente)"
]

# 4. Função de Busca e Tratamento dos Indicadores
@st.cache_data(ttl=3600)
def buscar_dados_ativo(ticker_str):
    if not ticker_str:
        return None

    # Extrai apenas o código do ticker (ex: "PETR4 - Petrobras PN" -> "PETR4")
    ticker_clean = ticker_str.strip().split()[0].split("-")[0].upper()
    symbol = f"{ticker_clean}.SA" if not ticker_clean.endswith(".SA") else ticker_clean
    stock = yf.Ticker(symbol)
    
    # Tratamento para evitar o erro de bloqueio (Rate Limit) do Yahoo Finance
    try:
        info = stock.info
        if not info or ("shortName" not in info and "regularMarketPrice" not in info and "currentPrice" not in info):
            return None
    except Exception:
        return None

    nome = info.get('shortName') or info.get('longName') or ticker_clean
    setor = info.get('sector') or "Setor Não Especificado"
    industria = info.get('industry') or "Indústria Não Especificada"

    preco = round(info.get('currentPrice') or info.get('regularMarketPrice') or 0.0, 2)
    lpa = round(info.get('trailingEps') or 0.0, 2)
    vpa = round(info.get('bookValue') or 0.0, 2)

    # Tratamento de DPA (Dividendos Por Ação)
    dpa_raw = info.get('trailingAnnualDividendRate') or info.get('dividendRate') or 0.0
    if dpa_raw == 0 and info.get('dividendYield'):
        dy_check = info.get('dividendYield')
        dpa_raw = (dy_check / 100.0 * preco) if dy_check > 1.0 else (dy_check * preco)
    dpa = round(dpa_raw, 2)

    # Dividend Yield %
    if preco > 0 and dpa > 0:
        dy = round((dpa / preco) * 100, 2)
    else:
        dy_raw = info.get('dividendYield') or 0.0
        dy = round(dy_raw if dy_raw > 1.0 else dy_raw * 100, 2)

    # Indicadores Fundamentalistas
    pl = round(info.get('trailingPE') or 0.0, 2)
    pvp = round(info.get('priceToBook') or 0.0, 2)
    roe = round((info.get('returnOnEquity') or 0.0) * 100, 2)
    margem = round((info.get('profitMargins') or 0.0) * 100, 2)
    divida_ebitda = round(info.get('debtToEbitda') or 0.0, 2)
    liquidez = round(info.get('currentRatio') or 0.0, 2)
    market_cap = info.get('marketCap') or 0

    # Valuation Graham
    if lpa > 0 and vpa > 0:
        p_graham_num = np.sqrt(22.5 * lpa * vpa)
        p_graham_str = f"R$ {p_graham_num:.2f}"
        margem_graham = f"{((p_graham_num - preco) / preco) * 100:+.1f}%"
    else:
        p_graham_str = "N/A (LPA/VPA ≤ 0)"
        margem_graham = "-"

    # Valuation Bazin (Teto 6%)
    if dpa > 0:
        p_bazin_num = dpa / 0.06
        p_bazin_str = f"R$ {p_bazin_num:.2f}"
        margem_bazin = f"{((p_bazin_num - preco) / preco) * 100:+.1f}%"
    else:
        p_bazin_str = "N/A (Sem Prov. Recentes)"
        margem_bazin = "-"

    if market_cap >= 1e9:
        cap_fmt = f"R$ {market_cap/1e9:.2f} Bilhões"
    elif market_cap >= 1e6:
        cap_fmt = f"R$ {market_cap/1e6:.2f} Milhões"
    else:
        cap_fmt = f"R$ {market_cap:,.2f}"

    return {
        "ticker": ticker_clean,
        "Ticker": ticker_clean,
        "nome": nome,
        "Nome": nome,
        "setor": setor,
        "Setor": setor,
        "industria": industria,
        "Indústria": industria,
        "preco": preco,
        "Preço": preco,
        "lpa": lpa,
        "LPA": lpa,
        "vpa": vpa,
        "VPA": vpa,
        "dpa": dpa,
        "DPA": dpa,
        "dy": dy,
        "pl": pl,
        "P/L": pl,
        "pvp": pvp,
        "P/VP": pvp,
        "roe": roe,
        "ROE (%)": roe,
        "margem": margem,
        "divida_ebitda": divida_ebitda,
        "liquidez": liquidez,
        "market_cap": market_cap,
        "cap_fmt": cap_fmt,
        "p_graham": p_graham_str,
        "margem_graham": margem_graham,
        "p_bazin": p_bazin_str,
        "margem_bazin": margem_bazin
    }

# 5. Cabeçalho Principal
st.markdown("<h1>⚡ Sankt20 B3 <span style='color:#00E676;'>Analytics Pro</span></h1>", unsafe_allow_html=True)

# 6. Sidebar (Com Parâmetros Mínimos Recomendados pela Suno / Value Investing)
# --- USUÁRIO E LOGOUT NA SIDEBAR ---
st.sidebar.markdown(f"👤 **Usuário:** {st.session_state['usuario']['username']}")

if st.sidebar.button("🚪 Sair (Logout)"):
    st.session_state["logado"] = False
    st.session_state["usuario"] = None
    st.rerun()

with st.sidebar.expander("🕒 Histórico de Pesquisas"):
    historico = db.obter_historico_usuario(st.session_state['usuario']['id'])
    if historico:
        for ticker, data in historico:
            st.caption(f"📌 **{ticker}** em {data[:16]}")
    else:
        st.caption("Nenhum histórico encontrado.")

# --- COLE AQUI O BLOCO DOS FAVORITOS ---
with st.sidebar.expander("⭐ Minhas Ações Favoritas"):
    favs = db.listar_favoritos(st.session_state['usuario']['id'])
    if favs:
        for fav_ticker, data in favs:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.caption(f"📌 **{fav_ticker}**")
            with col2:
                if st.button("❌", key=f"del_fav_{fav_ticker}"):
                    db.remover_favorito(st.session_state['usuario']['id'], fav_ticker)
                    st.rerun()
    else:
        st.caption("Nenhum favorito salvo.")

st.sidebar.divider()

st.sidebar.markdown("### ⚙️ Parâmetros do Filtro")
pl_max_ideal = st.sidebar.number_input(
    "P/L Máximo Recomendado", value=15.0, 
    help="Valuation: Preço/Lucro ideal até 15x para evitar pagar caro pela empresa."
)

pvp_max_ideal = st.sidebar.number_input(
    "P/VP Máximo Recomendado", value=1.5, 
    help="Preço/Valor Patrimonial: Mínimo aceitável até 1.5x (Graham)."
)

roe_min_ideal = st.sidebar.number_input(
    "ROE Mínimo (%)", value=10.0, 
    help="Rentabilidade: Mede a eficiência do capital próprio. Suno recomenda mínimo de 10% a 15%."
)

dy_min_ideal = st.sidebar.number_input(
    "Dividend Yield Mínimo (%)", value=6.0, 
    help="Método Bazin/Suno: Proventos anuais mínimos de 6% sobre a cotação."
)

divida_max_ideal = st.sidebar.number_input(
    "Dívida Líq. / EBITDA Máxima", value=2.5, 
    help="Risco Financeiro: Máximo de 2.5x para garantir que a empresa aguente juros altos."
)

margem_min_ideal = st.sidebar.number_input(
    "Margem Líquida Mínima (%)", value=10.0, 
    help="Vantagem Competitiva: Garante rentabilidade contra concorrência e custos."
)

liquidez_min_ideal = st.sidebar.number_input(
    "Liquidez Corrente Mínima", value=1.0, 
    help="Solvência: Deve ser maior que 1.0 para ter mais caixa que dívidas de curto prazo."
)

# 7. Abas
tab1, tab2, tab3, tab4 = st.tabs([
    "🎯 Valuation & Resumo", 
    "⚔️ Comparador Side-by-Side", 
    "🚀 Simulador Bola de Neve", 
    "📥 Central de Downloads"
])

# === ABA 1: VALUATION & RESUMO ===
with tab1:
    col_sel1, col_sel2 = st.columns([2, 1])
    with col_sel1:
        opcao_busca = st.selectbox(
            "🔍 Buscar Ação na B3 (Digite o nome ou ticker):",
            ACOES_B3,
            index=0
        )
        
        if opcao_busca == "🔍 Outro Ticker (Digitar manualmente)":
            ticker_ind = st.text_input("Digite o Ticker exato (ex: BBSE3):", value="BBSE3").upper().strip()
        else:
            ticker_ind = opcao_busca.split(" - ")[0].strip()

    if ticker_ind:
        try:
            dados = buscar_dados_ativo(ticker_ind)
        
        # --- SALVA A PESQUISA NO BANCO DE DADOS ---
            db.salvar_pesquisa(st.session_state["usuario"]["id"], ticker_ind)

        # --- BOTÃO DE FAVORITAR O ATIVO ---
            user_id = st.session_state["usuario"]["id"]
            ja_fav = db.eh_favorito(user_id, ticker_ind)

            if ja_fav:
                if st.button("⭐ Remover dos Favoritos", key="btn_rem_fav"):
                    db.remover_favorito(user_id, ticker_ind)
                    st.toast(f"{ticker_ind} removido dos favoritos!", icon="🗑️")
                    st.rerun()
            else:
                if st.button("☆ Adicionar aos Favoritos", key="btn_add_fav"):
                    db.adicionar_favorito(user_id, ticker_ind)
                    st.toast(f"{ticker_ind} adicionado aos favoritos!", icon="⭐")
                    st.rerun()

        # Card Automático da Empresa
            st.markdown(f"""
        <div class="company-header">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
                    <div>
                        <h2 style="margin:0; color:#FFFFFF;">{dados['Nome']} <span style="color:#00E676;">({dados['Ticker']})</span></h2>
                        <p style="margin:5px 0 0 0; color:#A0AEC0;">🏭 {dados['Setor']} • {dados['Indústria']} | 💼 Val. Mercado: {dados['Valor de Mercado']}</p>
                    </div>
                    <div style="text-align:right;">
                        <span style="font-size:0.85rem; color:#A0AEC0;">Cotação Atual</span>
                        <div style="font-size:2rem; font-weight:800; color:#00B0FF;">R$ {dados['Preço']}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Cards de Valuation
            st.markdown("### 📊 Modelos de Valuation Automáticos")
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                st.markdown(f"""
                <div class="ux-card">
                    <div class="metric-title">📐 Preço Justo Graham</div>
                    <div class="metric-value">{dados['Preço Justo Graham']}</div>
                    <div class="metric-sub">Margem/Desconto: <b>{dados['Margem Graham']}</b></div>
                </div>
                """, unsafe_allow_html=True)
                
            with col_b:
                st.markdown(f"""
                <div class="ux-card">
                    <div class="metric-title">🛡️ Preço Teto Bazin (6%)</div>
                    <div class="metric-value-blue">{dados['Preço Teto Bazin']}</div>
                    <div class="metric-sub">Margem/Desconto: <b>{dados['Margem Bazin']}</b></div>
                </div>
                """, unsafe_allow_html=True)

            with col_c:
                # Verificação completa contra TODOS os filtros do investidor
                passou_pl = dados['P/L'] <= pl_max_ideal
                passou_pvp = dados['P/VP'] <= pvp_max_ideal
                passou_roe = dados['ROE (%)'] >= roe_min_ideal
                passou_dy = dados['Dividend Yield (%)'] >= dy_min_ideal
                passou_divida = dados['Dívida Líq./EBITDA'] <= divida_max_ideal
                passou_margem = dados['Margem Líq. (%)'] >= margem_min_ideal
                passou_liquidez = dados['Liquidez Corrente'] >= liquidez_min_ideal

                aprovado_total = all([passou_pl, passou_pvp, passou_roe, passou_dy, passou_divida, passou_margem, passou_liquidez])
                status = "APROVADO" if aprovado_total else "ATENÇÃO"
                badge_class = "badge-approved" if aprovado_total else "badge-rejected"

                st.markdown(f"""
                <div class="ux-card">
                    <div class="metric-title">🎯 Veredito dos Filtros</div>
                    <div style="margin-top:10px;"><span class="{badge_class}">{status}</span></div>
                    <div class="metric-sub">Baseado nos Limites da Sidebar</div>
                </div>
                """, unsafe_allow_html=True)

            # Tabela Estruturada
            st.markdown("### 📋 Indicadores Fundamentalistas Detalhados")
            
            df_exibicao = pd.DataFrame([
                {"Indicador": "💵 Preço Atual", "Valor": f"R$ {dados['Preço']}", "Descrição": "Cotação atualizada na B3"},
                {"Indicador": "📐 Preço Justo (Graham)", "Valor": dados['Preço Justo Graham'], "Descrição": f"Fórmula: √(22.5 × LPA × VPA) | Margem: {dados['Margem Graham']}"},
                {"Indicador": "🛡️ Preço Teto (Bazin 6%)", "Valor": dados['Preço Teto Bazin'], "Descrição": f"Fórmula: DPA / 0.06 | Margem: {dados['Margem Bazin']}"},
                {"Indicador": "📊 P/L (Preço / Lucro)", "Valor": f"{dados['P/L']}x", "Descrição": f"Anos para reaver capital {'✅' if passou_pl else '⚠️'}"},
                {"Indicador": "📖 P/VP (Preço / Valor Patrimonial)", "Valor": f"{dados['P/VP']}x", "Descrição": f"Preço relativo ao patrimônio {'✅' if passou_pvp else '⚠️'}"},
                {"Indicador": "💰 Dividend Yield (DY)", "Valor": f"{dados['Dividend Yield (%)']}%", "Descrição": f"Rendimento anual em dividendos {'✅' if passou_dy else '⚠️'}"},
                {"Indicador": "📈 ROE (Retorno sobre Patrimônio)", "Valor": f"{dados['ROE (%)']}%", "Descrição": f"Eficiência na geração de lucro {'✅' if passou_roe else '⚠️'}"},
                {"Indicador": "💧 Margem Líquida", "Valor": f"{dados['Margem Líq. (%)']}%", "Descrição": f"Lucro líquido sobre receita {'✅' if passou_margem else '⚠️'}"},
                {"Indicador": "🧮 LPA (Lucro Por Ação)", "Valor": f"R$ {dados['LPA']}", "Descrição": "Lucro líquido por cada ação"},
                {"Indicador": "🏛️ VPA (Valor Patrimonial Por Ação)", "Valor": f"R$ {dados['VPA']}", "Descrição": "Patrimônio líquido por ação"},
                {"Indicador": "🎁 DPA (Dividendos Por Ação)", "Valor": f"R$ {dados['DPA']}", "Descrição": "Proventos pagos por ação nos últimos 12 meses"},
                {"Indicador": "⚖️ Dívida Líquida / EBITDA", "Valor": f"{dados['Dívida Líq./EBITDA']}x", "Descrição": f"Nível de endividamento da empresa {'✅' if passou_divida else '⚠️'}"},
                {"Indicador": "🌊 Liquidez Corrente", "Valor": f"{dados['Liquidez Corrente']}x", "Descrição": f"Capacidade de honrar dívidas no curto prazo {'✅' if passou_liquidez else '⚠️'}"}
            ])
            
            st.dataframe(df_exibicao, use_container_width=True, hide_index=True)

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
    if 'df_exibicao' in locals():
        col_d1, col_d2 = st.columns(2)
        
        csv_data = df_exibicao.to_csv(index=False).encode('utf-8')
        col_d1.download_button(
            "📄 Download em CSV", data=csv_data,
            file_name=f"Analise_{ticker_ind}.csv", mime="text/csv", use_container_width=True
        )
        
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df_exibicao.to_excel(writer, sheet_name="Resumo", index=False)
        excel_buffer.seek(0)
        
        col_d2.download_button(
            "📊 Download em Excel (.xlsx)", data=excel_buffer,
            file_name=f"Analise_{ticker_ind}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    else:
        st.info("Consulte uma ação na primeira aba para habilitar o download.")

# --- RENDERIZADOR DE CARDS DO RADAR DE DIVIDENDOS ---
@st.cache_data(ttl=86400)
def obter_meses_dividendos(ticker):
    ticker_b3 = f"{ticker.upper()}.SA" if not ticker.endswith(".SA") else ticker
    try:
        acao = yf.Ticker(ticker_b3)
        divs = acao.dividends
        if divs.empty:
            return set()
        dois_anos_atras = pd.Timestamp.now(tz=divs.index.tz) - pd.DateOffset(years=2)
        divs_recentes = divs[divs.index >= dois_anos_atras]
        return set(divs_recentes.index.month)
    except Exception:
        return set()


def renderizar_card_dividendo(ticker, setor, nome, meses_pagos):
    meses_nome = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    
    chips_html = ""
    for i, mes in enumerate(meses_nome, start=1):
        if i in meses_pagos:
            chips_html += f'<div style="background-color: #d1fae5; color: #065f46; font-weight: bold; padding: 4px; border-radius: 6px; text-align: center; font-size: 11px;">💲 {mes}</div>'
        else:
            chips_html += f'<div style="background-color: #f3f4f6; color: #9ca3af; padding: 4px; border-radius: 6px; text-align: center; font-size: 11px;">{mes}</div>'

    card_css = f"""
    <div style="background: white; border: 1px solid #e5e7eb; border-radius: 12px; padding: 16px; margin-bottom: 16px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);">
        <span style="font-size: 11px; background: #f3f4f6; color: #6b7280; padding: 2px 8px; border-radius: 12px;">{setor}</span>
        <div style="margin-top: 8px; font-weight: bold; font-size: 18px; color: #111827;">{ticker}</div>
        <div style="font-size: 13px; color: #6b7280; margin-bottom: 12px;">{nome}</div>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px;">
            {chips_html}
        </div>
    </div>
    """
    st.markdown(card_css, unsafe_allow_html=True)


# --- SEÇÃO RADAR DE DIVIDENDOS ---
st.divider()
st.header("🎯 Radar de Dividendos Inteligente")
st.write("Mapeamento do histórico de proventos das principais ações nos últimos 24 meses:")

acoes_radar = [
    {"ticker": "PETR4", "setor": "Petróleo e Gás", "nome": "Petrobras"},
    {"ticker": "ITUB4", "setor": "Financeiro", "nome": "Banco Itaú Unibanco"},
    {"ticker": "CMIG4", "setor": "Utilidade Pública", "nome": "Cemig"},
]

cols = st.columns(3)
for i, acao in enumerate(acoes_radar):
    with cols[i % 3]:
        meses = db.obter_meses_dividendos(acao["ticker"])
        renderizar_card_dividendo(acao["ticker"], acao["setor"], acao["nome"], meses)        