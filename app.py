import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px
from datetime import datetime

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA Y CSS
# ==========================================
st.set_page_config(page_title="Trading Lab Pro", page_icon="⚡", layout="wide")

# Inyección de CSS para diseño oscuro, neón y bordes redondeados
st.markdown("""
<style>
    /* Fondo principal y textos */
    [data-testid="stAppViewContainer"] {
        background-color: #070d19;
        color: #e2e8f0;
    }
    [data-testid="stSidebar"] {
        background-color: #0b1325;
        border-right: 1px solid #1e293b;
    }
    [data-testid="stHeader"] {
        background-color: transparent;
    }
    
    /* Estilos del Teclado Numérico */
    .pin-btn button {
        width: 70px !important;
        height: 70px !important;
        border-radius: 50% !important;
        font-size: 24px !important;
        background-color: #111c33 !important;
        color: #00d2ff !important;
        border: 2px solid #1e293b !important;
        transition: all 0.3s ease !important;
    }
    .pin-btn button:hover {
        border-color: #00d2ff !important;
        box-shadow: 0 0 15px rgba(0, 210, 255, 0.4) !important;
    }
    
    /* Tarjetas KPI (Dashboards) */
    .kpi-card {
        background: linear-gradient(145deg, #111a2e, #0b1221);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid #1e293b;
        box-shadow: 0 8px 32px 0 rgba(0,0,0,0.3);
        margin-bottom: 20px;
    }
    .kpi-title {
        color: #64748b;
        font-size: 13px;
        font-weight: 600;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 5px;
    }
    .kpi-value {
        color: #00d2ff;
        font-size: 32px;
        font-weight: 700;
        margin: 0;
    }
    .kpi-value.loss { color: #ff3366; }
    .kpi-value.win { color: #00ffa3; }
    
    /* Botones generales */
    .stButton>button {
        background-color: #00d2ff;
        color: #000000;
        border: none;
        border-radius: 8px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #00a8cc;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# SISTEMA DE LOGIN: TECLADO NUMÉRICO
# ==========================================
def custom_pin_pad():
    if "pin_input" not in st.session_state:
        st.session_state.pin_input = ""
        
    st.markdown("<h2 style='text-align: center; color: #00d2ff;'>⚡ TRADING LAB LOGIN</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b;'>Ingresa tu PIN de seguridad</p>", unsafe_allow_html=True)
    
    # Mostrar asteriscos según lo escrito
    pin_display = "● " * len(st.session_state.pin_input) + "○ " * (4 - len(st.session_state.pin_input))
    st.markdown(f"<h1 style='text-align: center; letter-spacing: 10px; color: #fff;'>{pin_display}</h1>", unsafe_allow_html=True)
    
    # Diseño del teclado centrado
    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 2])
    
    def add_digit(digit):
        if len(st.session_state.pin_input) < 4:
            st.session_state.pin_input += str(digit)
            
    def clear_pin():
        st.session_state.pin_input = ""

    # Fila 1
    with col2: st.markdown('<div class="pin-btn">', unsafe_allow_html=True); st.button("1", on_click=add_digit, args=(1,)); st.markdown('</div>', unsafe_allow_html=True)
    with col3: st.markdown('<div class="pin-btn">', unsafe_allow_html=True); st.button("2", on_click=add_digit, args=(2,)); st.markdown('</div>', unsafe_allow_html=True)
    with col4: st.markdown('<div class="pin-btn">', unsafe_allow_html=True); st.button("3", on_click=add_digit, args=(3,)); st.markdown('</div>', unsafe_allow_html=True)
    
    # Fila 2
    with col2: st.markdown('<div class="pin-btn">', unsafe_allow_html=True); st.button("4", on_click=add_digit, args=(4,)); st.markdown('</div>', unsafe_allow_html=True)
    with col3: st.markdown('<div class="pin-btn">', unsafe_allow_html=True); st.button("5", on_click=add_digit, args=(5,)); st.markdown('</div>', unsafe_allow_html=True)
    with col4: st.markdown('<div class="pin-btn">', unsafe_allow_html=True); st.button("6", on_click=add_digit, args=(6,)); st.markdown('</div>', unsafe_allow_html=True)
    
    # Fila 3
    with col2: st.markdown('<div class="pin-btn">', unsafe_allow_html=True); st.button("7", on_click=add_digit, args=(7,)); st.markdown('</div>', unsafe_allow_html=True)
    with col3: st.markdown('<div class="pin-btn">', unsafe_allow_html=True); st.button("8", on_click=add_digit, args=(8,)); st.markdown('</div>', unsafe_allow_html=True)
    with col4: st.markdown('<div class="pin-btn">', unsafe_allow_html=True); st.button("9", on_click=add_digit, args=(9,)); st.markdown('</div>', unsafe_allow_html=True)
    
    # Fila 4
    with col2: st.button("🗑️", on_click=clear_pin)
    with col3: st.markdown('<div class="pin-btn">', unsafe_allow_html=True); st.button("0", on_click=add_digit, args=(0,)); st.markdown('</div>', unsafe_allow_html=True)
    
    # Validación automática al llegar a 4 dígitos
    if len(st.session_state.pin_input) == 4:
        if st.session_state.pin_input == str(st.secrets["APP_PASSWORD"]):
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("PIN Incorrecto")
            st.session_state.pin_input = ""
            
    return False

if "password_correct" not in st.session_state:
    custom_pin_pad()
elif not st.session_state["password_correct"]:
    custom_pin_pad()
else:
    # ==========================================
    # LÓGICA PRINCIPAL Y BASE DE DATOS
    # ==========================================
    @st.cache_resource(ttl=3600)
    def get_db_connection():
        conexion = psycopg2.connect(st.secrets["DATABASE_URL"])
        conexion.autocommit = True
        return conexion

    # Obtenemos la conexión
    conn = get_db_connection()
    
    # Si la conexión se cerró por inactividad, limpiamos la memoria y reconectamos
    if conn.closed != 0:
        st.cache_resource.clear()
        conn = get_db_connection()

    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS accounts (id SERIAL PRIMARY KEY, broker VARCHAR(100), account_name VARCHAR(100), initial_balance NUMERIC)''')
    c.execute('''CREATE TABLE IF NOT EXISTS trades (id SERIAL PRIMARY KEY, account_id INTEGER REFERENCES accounts(id), date_time TIMESTAMP, market VARCHAR(50), asset VARCHAR(50), direction VARCHAR(50), amount NUMERIC, result VARCHAR(50), pnl NUMERIC)''')

    def get_accounts(): return pd.read_sql_query("SELECT * FROM accounts", conn)
    def get_trades(account_id): return pd.read_sql_query(f"SELECT * FROM trades WHERE account_id = {account_id} ORDER BY date_time ASC", conn)

    # ==========================================
    # INTERFAZ DEL DASHBOARD
    # ==========================================
    st.sidebar.markdown("<h2 style='color: #00d2ff;'>⚡ Panel de Control</h2>", unsafe_allow_html=True)
    menu = st.sidebar.radio("Navegación", ["📊 Dashboard Principal", "🏦 Gestionar Cuentas"])
    
    st.sidebar.divider()
    if st.sidebar.button("Cerrar Sesión 🔒"):
        del st.session_state["password_correct"]
        st.session_state.pin_input = ""
        st.rerun()

    if menu == "🏦 Gestionar Cuentas":
        st.markdown("<h2>🏦 Gestión de Cuentas</h2>", unsafe_allow_html=True)
        with st.form("new_account_form", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            with col1: broker = st.text_input("Bróker (Ej. Quotex)")
            with col2: acc_name = st.text_input("Nombre de Cuenta")
            with col3: init_balance = st.number_input("Balance Inicial ($)", min_value=0.0, value=100.0)
            if st.form_submit_button("Crear Cuenta") and broker:
                c.execute("INSERT INTO accounts (broker, account_name, initial_balance) VALUES (%s, %s, %s)", (broker, acc_name, init_balance))
                st.success("Cuenta creada.")
                st.rerun()

        st.dataframe(get_accounts(), use_container_width=True, hide_index=True)

    elif menu == "📊 Dashboard Principal":
        df_accounts = get_accounts()
        if df_accounts.empty:
            st.warning("⚠️ Crea una cuenta en el menú lateral.")
        else:
            # Selector superior
            col_sel, _ = st.columns([1, 2])
            with col_sel:
                account_options = df_accounts.apply(lambda x: f"{x['broker']} - {x['account_name']} (ID:{x['id']})", axis=1).tolist()
                selected_account_str = st.selectbox("CUENTA ACTIVA:", account_options, label_visibility="collapsed")
            
            selected_acc_id = int(selected_account_str.split("ID:")[1].replace(")", ""))
            initial_balance = float(df_accounts[df_accounts['id'] == selected_acc_id]['initial_balance'].values[0])
            df_trades = get_trades(selected_acc_id)

            # Cálculo de métricas
            win_rate, net_profit, wins, losses = 0, 0, 0, 0
            current_balance = initial_balance
            total_trades = len(df_trades)
            
            if total_trades > 0:
                df_trades['pnl'] = pd.to_numeric(df_trades['pnl'])
                wins = len(df_trades[df_trades['result'].str.contains("WIN")])
                losses = len(df_trades[df_trades['result'].str.contains("LOSS")])
                ties = len(df_trades[df_trades['result'].str.contains("EMPATE")])
                win_rate = (wins / (total_trades - ties)) * 100 if (total_trades - ties) > 0 else 0
                net_profit = df_trades['pnl'].sum()
                current_balance = initial_balance + net_profit

            # Tarjetas Estilo Plataforma Pro (HTML Inyectado)
            st.markdown("<br>", unsafe_allow_html=True)
            kpi_cols = st.columns(4)
            
            color_pnl = "win" if net_profit >= 0 else "loss"
            signo = "+" if net_profit >= 0 else ""
            
            with kpi_cols[0]:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">WIN RATE</div>
                    <div class="kpi-value">{win_rate:.1f}%</div>
                    <div style="color: #94a3b8; font-size: 12px; margin-top:5px;">{wins} Ganadas / {losses} Perdidas</div>
                </div>
                """, unsafe_allow_html=True)
                
            with kpi_cols[1]:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">NET PNL (BENEFICIO)</div>
                    <div class="kpi-value {color_pnl}">{signo}${net_profit:.2f}</div>
                    <div style="color: #94a3b8; font-size: 12px; margin-top:5px;">Periodo actual</div>
                </div>
                """, unsafe_allow_html=True)

            with kpi_cols[2]:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">BALANCE TOTAL</div>
                    <div class="kpi-value" style="color: #ffffff;">${current_balance:.2f}</div>
                    <div style="color: #94a3b8; font-size: 12px; margin-top:5px;">Capital disponible</div>
                </div>
                """, unsafe_allow_html=True)
                
            with kpi_cols[3]:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">TRADES EJECUTADOS</div>
                    <div class="kpi-value" style="color: #00d2ff;">{total_trades}</div>
                    <div style="color: #94a3b8; font-size: 12px; margin-top:5px;">Volumen total</div>
                </div>
                """, unsafe_allow_html=True)

            # Formulario de registro (Diseño compacto)
            with st.expander("⚡ NUEVO TRADE", expanded=False):
                with st.form("trade_form", clear_on_submit=True):
                    c1, c2, c3, c4 = st.columns(4)
                    with c1:
                        market = st.selectbox("Mercado", ["Opciones Binarias", "Forex"])
                        asset = st.text_input("Activo (Ej. EURUSD)").upper()
                    with c2:
                        direction = st.selectbox("Dirección", ["CALL / BUY 🟢", "PUT / SELL 🔴"])
                        amount = st.number_input("Inversión ($)", min_value=0.1, value=10.0)
                    with c3:
                        result = st.selectbox("Resultado", ["WIN 🎉", "LOSS ❌", "EMPATE ➖"])
                        pnl = st.number_input("P/L Neto ($)", value=0.0)
                    with c4:
                        date_time = st.date_input("Fecha", datetime.today())
                        time_input = st.time_input("Hora", datetime.now().time())
                    
                    if st.form_submit_button("REGISTRAR EJECUCIÓN") and asset:
                        dt_string = f"{date_time} {time_input}"
                        c.execute('''INSERT INTO trades (account_id, date_time, market, asset, direction, amount, result, pnl) 
                                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''', 
                                  (selected_acc_id, dt_string, market, asset, direction, amount, result, pnl))
                        st.rerun()

            # Gráfico con estilo de plataforma
            st.markdown("<br><h3>📈 Histórico de Equidad</h3>", unsafe_allow_html=True)
            if total_trades > 0:
                df_trades['Balance'] = initial_balance + df_trades['pnl'].cumsum()
                df_trades['Trade #'] = range(1, len(df_trades) + 1)
                
                fig = px.area(df_trades, x='Trade #', y='Balance', markers=True)
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#94a3b8'),
                    margin=dict(l=0, r=0, t=10, b=0),
                    yaxis=dict(gridcolor='#1e293b')
                )
                fig.update_traces(line_color='#00d2ff', fillcolor='rgba(0, 210, 255, 0.1)')
                st.plotly_chart(fig, use_container_width=True)
                
                # Tabla estilizada
                st.dataframe(df_trades.drop(columns=['id', 'account_id']), use_container_width=True, hide_index=True)
