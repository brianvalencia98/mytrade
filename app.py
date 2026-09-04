import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px
from datetime import datetime
import calendar
import time

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(page_title="Trading Lab Pro", page_icon="⚡", layout="wide")

# ==========================================
# BLOQUES DE CSS (SEPARADOS PARA LOGIN Y DASHBOARD)
# ==========================================
CSS_LOGIN = """
<style>
    [data-testid="stAppViewContainer"] { background-color: #070d19; color: #e2e8f0; }
    [data-testid="stHeader"] { background-color: transparent; }
    
    div[data-testid="column"] { display: flex; justify-content: center; align-items: center; }
    
    [data-testid="stButton"] button {
        width: 70px !important;
        height: 70px !important;
        border-radius: 50% !important;
        background-color: transparent !important;
        border: 2px solid #1e293b !important;
        color: #00d2ff !important;
        font-size: 24px !important;
        transition: all 0.3s ease !important;
        padding: 0 !important;
    }
    [data-testid="stButton"] button:hover {
        border-color: #00d2ff !important;
        box-shadow: 0 0 15px rgba(0, 210, 255, 0.4) !important;
    }
</style>
"""

CSS_DASHBOARD = """
<style>
    [data-testid="stAppViewContainer"] { background-color: #070d19; color: #e2e8f0; }
    [data-testid="stSidebar"] { background-color: #0b1325; border-right: 1px solid #1e293b; }
    [data-testid="stHeader"] { background-color: transparent; }
    
    /* Tarjetas KPI */
    .kpi-card { background: linear-gradient(145deg, #111a2e, #0b1221); border-radius: 15px; padding: 20px; border: 1px solid #1e293b; box-shadow: 0 8px 32px 0 rgba(0,0,0,0.3); margin-bottom: 20px;}
    .kpi-title { color: #64748b; font-size: 13px; font-weight: 600; letter-spacing: 1.5px; margin-bottom: 5px;}
    .kpi-value { color: #00d2ff; font-size: 32px; font-weight: 700; margin: 0;}
    .kpi-value.loss { color: #ff3366; }
    .kpi-value.win { color: #00ffa3; }
    
    [data-testid="stButton"] button { background-color: #00d2ff !important; color: #000000 !important; border: none !important; border-radius: 8px !important; font-weight: bold !important; width: 100% !important; }
    [data-testid="stButton"] button:hover { background-color: #00a8cc !important; color: white !important;}

    /* Calendario Avanzado */
    .cal-container { background-color: #0b1325; padding: 20px; border-radius: 15px; border: 1px solid #1e293b; margin-top: 20px; box-shadow: 0 8px 32px 0 rgba(0,0,0,0.3); }
    .cal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
    .cal-title { color: #ffffff; font-size: 20px; font-weight: bold; display: flex; align-items: center; gap: 10px; }
    .cal-month { color: #ffffff; font-size: 16px; font-weight: bold; letter-spacing: 2px; text-transform: uppercase; }
    .cal-table { width: 100%; border-collapse: collapse; table-layout: fixed; }
    .cal-th { color: #00d2ff; padding: 10px 0; text-align: center; border-bottom: 1px solid #1e293b; font-weight: bold; font-size: 14px;}
    
    /* Celdas diarias con posicionamiento relativo */
    .cal-td { border: 1px solid #1e293b; height: 100px; vertical-align: top; padding: 10px; background-color: #070d19; transition: background 0.3s; position: relative; }
    .cal-td:hover { background-color: #111a2e; }
    
    /* Estilos dinámicos para operaciones ganadoras y perdedoras */
    .cal-td.cal-td-win { border: 1px solid #00ffa3; border-bottom: 3px solid #00ffa3; background-color: rgba(0, 255, 163, 0.05); }
    .cal-td.cal-td-loss { border: 1px solid #ff3366; border-bottom: 3px solid #ff3366; background-color: rgba(255, 51, 102, 0.05); }
    
    /* Celda de Totales */
    .cal-td-total { border: 1px solid #1e293b; height: 100px; vertical-align: middle; text-align: center; background-color: #0b1325; }
    .cal-td-total.cal-total-win { border: 1px solid rgba(0, 255, 163, 0.3); background-color: rgba(0, 255, 163, 0.05); }
    .cal-td-total.cal-total-loss { border: 1px solid rgba(255, 51, 102, 0.3); background-color: rgba(255, 51, 102, 0.05); }
    
    .cal-day { font-size: 14px; color: #94a3b8; font-weight: bold;}
    
    /* Posicionamiento absoluto para fijar el monto en la esquina */
    .cal-pnl-win { color: #00ffa3; font-weight: bold; font-size: 13px; position: absolute; bottom: 8px; right: 8px; }
    .cal-pnl-loss { color: #ff3366; font-weight: bold; font-size: 13px; position: absolute; bottom: 8px; right: 8px; }
    
    /* Textos para la celda de totales */
    .cal-pnl-win-total { color: #00ffa3; font-weight: bold; font-size: 14px; margin-top: 5px; }
    .cal-pnl-loss-total { color: #ff3366; font-weight: bold; font-size: 14px; margin-top: 5px; }
    .cal-label-total { font-size: 10px; color: #64748b; font-weight: bold; letter-spacing: 1px;}
</style>
"""

# ==========================================
# GENERADOR DEL CALENDARIO
# ==========================================
def render_calendar(df_trades):
    meses = {1:"ENE", 2:"FEB", 3:"MAR", 4:"ABR", 5:"MAY", 6:"JUN", 7:"JUL", 8:"AGO", 9:"SEP", 10:"OCT", 11:"NOV", 12:"DIC"}
    now = datetime.now()
    year = now.year
    month = now.month
    month_name = f"{meses[month]} {year}"
    
    daily_pnl = {}
    if not df_trades.empty:
        df_trades['date_time'] = pd.to_datetime(df_trades['date_time'])
        current_month_trades = df_trades[(df_trades['date_time'].dt.year == year) & (df_trades['date_time'].dt.month == month)]
        grouped = current_month_trades.groupby(current_month_trades['date_time'].dt.day)['pnl'].sum()
        daily_pnl = grouped.to_dict()

    cal = calendar.monthcalendar(year, month)
    
    html = f"""
    <div class="cal-container">
        <div class="cal-header">
            <div class="cal-title">📅 Calendario</div>
            <div class="cal-month">&lt; &nbsp; {month_name} &nbsp; &gt;</div>
        </div>
        <table class="cal-table">
            <tr>
                <th class="cal-th">L</th><th class="cal-th">M</th><th class="cal-th">M</th>
                <th class="cal-th">J</th><th class="cal-th">V</th><th class="cal-th">S</th>
                <th class="cal-th">D</th><th class="cal-th">∑</th>
            </tr>
    """
    for week in cal:
        html += "<tr>"
        week_total = 0
        for day in week:
            if day == 0:
                html += '<td class="cal-td"></td>'
            else:
                pnl = daily_pnl.get(day, 0)
                week_total += pnl
                
                if pnl > 0:
                    html += f'<td class="cal-td cal-td-win"><div class="cal-day">{day}</div><div class="cal-pnl-win">+{pnl:.2f}$</div></td>'
                elif pnl < 0:
                    html += f'<td class="cal-td cal-td-loss"><div class="cal-day">{day}</div><div class="cal-pnl-loss">{pnl:.2f}$</div></td>'
                else:
                    html += f'<td class="cal-td"><div class="cal-day">{day}</div></td>'
        
        if week_total > 0:
            html += f'<td class="cal-td-total cal-total-win"><div class="cal-label-total">TOTAL</div><div class="cal-pnl-win-total">+{week_total:.2f}$</div></td>'
        elif week_total < 0:
            html += f'<td class="cal-td-total cal-total-loss"><div class="cal-label-total">TOTAL</div><div class="cal-pnl-loss-total">{week_total:.2f}$</div></td>'
        else:
            html += f'<td class="cal-td-total"><div class="cal-label-total">TOTAL</div></td>'
            
        html += "</tr>"
        
    html += "</table></div>"
    return html

# ==========================================
# SISTEMA DE LOGIN
# ==========================================
def custom_pin_pad():
    st.markdown(CSS_LOGIN, unsafe_allow_html=True)
    
    if "pin_input" not in st.session_state:
        st.session_state.pin_input = ""
        
    st.markdown("<br><h2 style='text-align: center; color: #00d2ff;'>⚡ TRADING LAB LOGIN</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b;'>Ingresa tu PIN de seguridad</p>", unsafe_allow_html=True)
    
    pin_display = "● " * len(st.session_state.pin_input) + "○ " * (4 - len(st.session_state.pin_input))
    st.markdown(f"<h1 style='text-align: center; letter-spacing: 15px; color: #fff;'>{pin_display}</h1><br>", unsafe_allow_html=True)
    
    _, col1, col2, col3, _ = st.columns([1.5, 0.4, 0.4, 0.4, 1.5])
    
    def add_digit(digit):
        if len(st.session_state.pin_input) < 4: st.session_state.pin_input += str(digit)
    def clear_pin():
        st.session_state.pin_input = ""

    with col1: st.button("1", on_click=add_digit, args=(1,))
    with col2: st.button("2", on_click=add_digit, args=(2,))
    with col3: st.button("3", on_click=add_digit, args=(3,))
    
    with col1: st.button("4", on_click=add_digit, args=(4,))
    with col2: st.button("5", on_click=add_digit, args=(5,))
    with col3: st.button("6", on_click=add_digit, args=(6,))
    
    with col1: st.button("7", on_click=add_digit, args=(7,))
    with col2: st.button("8", on_click=add_digit, args=(8,))
    with col3: st.button("9", on_click=add_digit, args=(9,))
    
    with col1: st.button("🗑️", on_click=clear_pin)
    with col2: st.button("0", on_click=add_digit, args=(0,))
    with col3: pass
    
    if len(st.session_state.pin_input) == 4:
        if st.session_state.pin_input == str(st.secrets["APP_PASSWORD"]):
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("PIN Incorrecto")
            st.session_state.pin_input = ""
            
    return False

# ==========================================
# RUTEO DE PANTALLAS Y BASE DE DATOS
# ==========================================
if "password_correct" not in st.session_state or not st.session_state["password_correct"]:
    custom_pin_pad()
else:
    st.markdown(CSS_DASHBOARD, unsafe_allow_html=True)
    
    @st.cache_resource(ttl=3600)
    def get_db_connection():
        conexion = psycopg2.connect(st.secrets["DATABASE_URL"])
        conexion.autocommit = True
        return conexion

    conn = get_db_connection()
    if conn.closed != 0:
        st.cache_resource.clear()
        conn = get_db_connection()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS accounts (id SERIAL PRIMARY KEY, broker VARCHAR(100), account_name VARCHAR(100), initial_balance NUMERIC)''')
    c.execute('''CREATE TABLE IF NOT EXISTS trades (id SERIAL PRIMARY KEY, account_id INTEGER REFERENCES accounts(id), date_time TIMESTAMP, market VARCHAR(50), asset VARCHAR(50), direction VARCHAR(50), amount NUMERIC, result VARCHAR(50), pnl NUMERIC)''')
    conn.commit()

    def get_accounts(): return pd.read_sql_query("SELECT * FROM accounts", conn)
    def get_trades(account_id): return pd.read_sql_query(f"SELECT * FROM trades WHERE account_id = {account_id} ORDER BY date_time ASC", conn)

    # ==========================================
    # BARRA LATERAL
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
            
            guardar_cuenta = st.form_submit_button("Crear Cuenta")
            
            if guardar_cuenta and broker:
                c.execute("INSERT INTO accounts (broker, account_name, initial_balance) VALUES (%s, %s, %s)", (broker, acc_name, init_balance))
                conn.commit() # Forzar guardado
                st.success("✅ Cuenta creada correctamente.")
                time.sleep(0.5)
                st.rerun()
                
        st.dataframe(get_accounts(), use_container_width=True, hide_index=True)

    elif menu == "📊 Dashboard Principal":
        df_accounts = get_accounts()
        if df_accounts.empty:
            st.warning("⚠️ Crea una cuenta en el menú lateral.")
        else:
            col_sel, _ = st.columns([1, 2])
            with col_sel:
                account_options = df_accounts.apply(lambda x: f"{x['broker']} - {x['account_name']} (ID:{x['id']})", axis=1).tolist()
                selected_account_str = st.selectbox("CUENTA ACTIVA:", account_options, label_visibility="collapsed")
            
            selected_acc_id = int(selected_account_str.split("ID:")[1].replace(")", ""))
            initial_balance = float(df_accounts[df_accounts['id'] == selected_acc_id]['initial_balance'].values[0])
            df_trades = get_trades(selected_acc_id)

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

            # ==========================================
            # TARJETAS KPI
            # ==========================================
            st.markdown("<br>", unsafe_allow_html=True)
            kpi_cols = st.columns(4)
            color_pnl = "win" if net_profit >= 0 else "loss"
            signo = "+" if net_profit >= 0 else ""
            
            with kpi_cols[0]: st.markdown(f'<div class="kpi-card"><div class="kpi-title">WIN RATE</div><div class="kpi-value">{win_rate:.1f}%</div><div style="color: #94a3b8; font-size: 12px; margin-top:5px;">{wins} Ganadas / {losses} Perdidas</div></div>', unsafe_allow_html=True)
            with kpi_cols[1]: st.markdown(f'<div class="kpi-card"><div class="kpi-title">NET PNL (BENEFICIO)</div><div class="kpi-value {color_pnl}">{signo}${net_profit:.2f}</div><div style="color: #94a3b8; font-size: 12px; margin-top:5px;">Periodo actual</div></div>', unsafe_allow_html=True)
            with kpi_cols[2]: st.markdown(f'<div class="kpi-card"><div class="kpi-title">BALANCE TOTAL</div><div class="kpi-value" style="color: #ffffff;">${current_balance:.2f}</div><div style="color: #94a3b8; font-size: 12px; margin-top:5px;">Capital disponible</div></div>', unsafe_allow_html=True)
            with kpi_cols[3]: st.markdown(f'<div class="kpi-card"><div class="kpi-title">TRADES EJECUTADOS</div><div class="kpi-value" style="color: #00d2ff;">{total_trades}</div><div style="color: #94a3b8; font-size: 12px; margin-top:5px;">Volumen total</div></div>', unsafe_allow_html=True)

            # ==========================================
            # CALENDARIO DE TRADING
            # ==========================================
            st.markdown(render_calendar(df_trades), unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

            # ==========================================
            # REGISTRO DE OPERACIONES
            # ==========================================
            with st.expander("⚡ REGISTRAR NUEVO TRADE", expanded=False):
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
                    
                    guardar_ejecucion = st.form_submit_button("GUARDAR EJECUCIÓN")
                    
                    if guardar_ejecucion and asset:
                        try:
                            dt_string = f"{date_time} {time_input}"
                            c.execute('''INSERT INTO trades (account_id, date_time, market, asset, direction, amount, result, pnl) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''', (selected_acc_id, dt_string, market, asset, direction, amount, result, pnl))
                            conn.commit()  # Forzar escritura en base de datos
                            st.success("✅ Trade registrado exitosamente!")
                            time.sleep(0.5) # Dar tiempo para que el servidor procese antes de recargar
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error guardando en la BD: {e}")

            # ==========================================
            # GRÁFICA HISTÓRICA
            # ==========================================
            st.markdown("<br><h3>📈 Histórico de Equidad</h3>", unsafe_allow_html=True)
            if total_trades > 0:
                df_trades['Balance'] = initial_balance + df_trades['pnl'].cumsum()
                df_trades['Trade #'] = range(1, len(df_trades) + 1)
                
                fig = px.area(df_trades, x='Trade #', y='Balance', markers=True)
                fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8'), margin=dict(l=0, r=0, t=10, b=0), yaxis=dict(gridcolor='#1e293b'))
                fig.update_traces(line_color='#00d2ff', fillcolor='rgba(0, 210, 255, 0.1)')
                st.plotly_chart(fig, use_container_width=True)
                
                st.dataframe(df_trades.drop(columns=['id', 'account_id']), use_container_width=True, hide_index=True)
