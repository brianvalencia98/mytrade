import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import calendar
import time
import textwrap

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(page_title="Trading Lab Pro", page_icon="⚡", layout="wide")

# ==========================================
# BLOQUES DE CSS (FUTURISTA / NEON AVANZADO)
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
    [data-testid="stButton"] button:hover { border-color: #00d2ff !important; box-shadow: 0 0 15px rgba(0, 210, 255, 0.4) !important; }
</style>
"""

CSS_DASHBOARD = """
<style>
    [data-testid="stAppViewContainer"] { background-color: #070d19; color: #e2e8f0; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #050b14 0%, #0b1325 100%); border-right: 1px solid #1e293b; box-shadow: 5px 0 25px rgba(0, 0, 0, 0.5); }
    [data-testid="stHeader"] { background-color: transparent; }
    
    .sidebar-title { color: #00d2ff; font-size: 20px; font-weight: 800; letter-spacing: 2px; text-transform: uppercase; text-shadow: 0 0 10px rgba(0, 210, 255, 0.4); margin-bottom: 20px; display: flex; align-items: center; gap: 10px; }
    [data-testid="stSidebar"] .stRadio > label { color: #94a3b8 !important; font-weight: 600 !important; letter-spacing: 1px; }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] { gap: 10px; }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label { background: rgba(17, 26, 46, 0.6); border: 1px solid #1e293b; border-radius: 12px; padding: 12px 15px; transition: all 0.3s ease; }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover { border-color: #00d2ff; background: rgba(0, 210, 255, 0.08); box-shadow: 0 0 15px rgba(0, 210, 255, 0.2); transform: translateX(4px); }

    [data-testid="stSidebar"] .stButton button { background: linear-gradient(135deg, #ff3366, #d22d56) !important; color: #ffffff !important; border: 1px solid #ff3366 !important; border-radius: 12px !important; font-weight: bold !important; letter-spacing: 1px; width: 100% !important; box-shadow: 0 4px 15px rgba(255, 51, 102, 0.3) !important; transition: all 0.3s ease !important; }
    [data-testid="stSidebar"] .stButton button:hover { background: linear-gradient(135deg, #ff1948, #ff3366) !important; box-shadow: 0 0 20px rgba(255, 51, 102, 0.6) !important; transform: translateY(-2px); }

    /* Bloquear escritura en Selectbox */
    [data-testid="stSelectbox"] div[data-baseweb="select"] input { caret-color: transparent !important; pointer-events: none !important; }
    [data-testid="stSelectbox"] > div > div {
        background: linear-gradient(145deg, #0b1325, #070d19) !important;
        border: 1px solid #1e293b !important;
        border-radius: 14px !important;
        color: #00d2ff !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    }
    [data-testid="stSelectbox"] > div > div:hover {
        border-color: #00d2ff !important;
        box-shadow: 0 0 20px rgba(0, 210, 255, 0.35) !important;
        transform: translateY(-2px);
    }
    [data-testid="stSelectbox"] span { color: #00d2ff !important; font-weight: 700 !important; letter-spacing: 0.5px; }

    /* Estilo futurista para Expanders */
    [data-testid="stExpander"] {
        background: linear-gradient(145deg, #070d19, #0b1325) !important;
        border: 1px solid #00d2ff !important;
        border-radius: 16px !important;
        box-shadow: 0 8px 32px 0 rgba(0,0,0,0.4), 0 0 15px rgba(0, 210, 255, 0.1) !important;
        transition: all 0.3s ease !important;
    }
    [data-testid="stExpander"] summary {
        background: linear-gradient(135deg, #0b1325, #111a2e) !important;
        border-radius: 12px !important;
        color: #00d2ff !important;
        font-weight: bold !important;
        border: 1px solid #1e293b !important;
        transition: all 0.3s ease !important;
    }
    [data-testid="stExpander"] summary:hover {
        border-color: #00d2ff !important;
        box-shadow: 0 0 15px rgba(0, 210, 255, 0.3) !important;
        color: #ffffff !important;
    }

    .stTextInput input, .stNumberInput input, .stDateInput input, .stTimeInput input {
        background-color: #050b14 !important;
        border: 1px solid #1e293b !important;
        border-radius: 12px !important;
        color: #e2e8f0 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    .stTextInput input:focus, .stNumberInput input:focus, .stDateInput input:focus, .stTimeInput input:focus {
        border-color: #00d2ff !important;
        box-shadow: 0 0 15px rgba(0, 210, 255, 0.35) !important;
        background-color: #070d19 !important;
    }

    .stForm [data-testid="stFormSubmitButton"] button {
        background: linear-gradient(135deg, #00d2ff, #0072ff) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 14px !important;
        font-weight: 800 !important;
        letter-spacing: 1.5px !important;
        text-transform: uppercase !important;
        box-shadow: 0 4px 20px rgba(0, 210, 255, 0.4) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        padding: 12px 24px !important;
    }
    .stForm [data-testid="stFormSubmitButton"] button:hover {
        background: linear-gradient(135deg, #00ffa3, #00d2ff) !important;
        box-shadow: 0 0 30px rgba(0, 255, 163, 0.6) !important;
        transform: translateY(-3px) scale(1.02);
    }

    .kpi-card-exact { background: linear-gradient(145deg, #070d19, #0b1325); border-radius: 16px; padding: 18px; border: 1px solid #1e293b; box-shadow: 0 8px 32px 0 rgba(0,0,0,0.4); margin-bottom: 20px; position: relative; height: 130px; display: flex; flex-direction: column; justify-content: space-between; }
    .profile-card { background: linear-gradient(145deg, #070d19, #0b1325); border-radius: 16px; padding: 20px; border: 1px solid #1e293b; box-shadow: 0 8px 32px 0 rgba(0,0,0,0.4); height: 100%;}
    .profile-title { color: #ffffff; font-size: 20px; font-weight: bold; margin-bottom: 0px;}
    .progress-bar-bg { height: 4px; background-color: #1e293b; border-radius: 2px; margin-top: 10px; position: relative; }
    .progress-bar-fill { height: 100%; background: linear-gradient(90deg, #ff3366, #ffb800, #00ffa3); border-radius: 2px; position: absolute; left: 0; top: 0; }

    .chart-box { background: linear-gradient(145deg, #070d19, #0b1325); border-radius: 16px; padding: 20px; border: 1px solid #1e293b; box-shadow: 0 8px 32px 0 rgba(0,0,0,0.4); margin-top: 20px; height: 100%; }
    .best-worst-card { background: rgba(11, 19, 37, 0.8); border-radius: 12px; padding: 12px 14px; border: 1px solid #1e293b; margin-top: 12px; }
    .best-card { border-left: 4px solid #00ffa3 !important; }
    .worst-card { border-left: 4px solid #ff3366 !important; }

    .futuristic-card { background: linear-gradient(145deg, #070d19, #0b1325); border-radius: 16px; padding: 20px; border: 1px solid #1e293b; box-shadow: 0 8px 32px 0 rgba(0,0,0,0.4); height: 100%; display: flex; flex-direction: column; justify-content: space-between; }
    .session-badge { display: flex; align-items: center; justify-content: space-between; padding: 8px 12px; border-radius: 10px; margin-bottom: 8px; border: 1px solid #1e293b; background: rgba(17, 26, 46, 0.5); }
    .session-badge.active { border-color: #00ffa3; background: rgba(0, 255, 163, 0.08); box-shadow: 0 0 10px rgba(0, 255, 163, 0.15); }
    .dot-live { height: 8px; width: 8px; background-color: #00ffa3; border-radius: 50%; display: inline-block; box-shadow: 0 0 8px #00ffa3; animation: pulse 1.5s infinite; }
    .dot-closed { height: 8px; width: 8px; background-color: #64748b; border-radius: 50%; display: inline-block; }
    @keyframes pulse { 0% { transform: scale(0.95); opacity: 0.8; } 50% { transform: scale(1.2); opacity: 1; box-shadow: 0 0 12px #00ffa3; } 100% { transform: scale(0.95); opacity: 0.8; } }

    .trade-log-card {
        background: linear-gradient(145deg, #0b1325, #070d19);
        border: 1px solid #1e293b;
        border-radius: 14px;
        padding: 16px 20px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .trade-log-card:hover {
        border-color: #00d2ff;
        box-shadow: 0 0 20px rgba(0, 210, 255, 0.3);
        transform: translateY(-2px);
    }
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
        df_copy = df_trades.copy()
        df_copy['date_time'] = pd.to_datetime(df_copy['date_time'])
        df_copy['pnl'] = pd.to_numeric(df_copy['pnl'], errors='coerce').fillna(0.0)
        current_month = df_copy[(df_copy['date_time'].dt.year == year) & (df_copy['date_time'].dt.month == month)]
        if not current_month.empty:
            grouped = current_month.groupby(current_month['date_time'].dt.day)['pnl'].sum()
            daily_pnl = {int(k): float(v) for k, v in grouped.items()}

    cal = calendar.monthcalendar(year, month)
    
    html = f"""
    <div style="background-color: #070d19; padding: 20px; border-radius: 16px; border: 1px solid #1e293b; box-shadow: 0 8px 32px 0 rgba(0,0,0,0.4); height: 100%;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <div style="color: #ffffff; font-size: 20px; font-weight: bold; display: flex; align-items: center; gap: 10px;">📅 Calendario</div>
            <div style="color: #ffffff; font-size: 14px; font-weight: bold; letter-spacing: 2px; text-transform: uppercase;">&lt; &nbsp; {month_name} &nbsp; &gt;</div>
        </div>
        <table style="width: 100%; border-collapse: collapse; table-layout: fixed;">
            <tr>
                <th style="color: #00d2ff; padding: 8px 0; text-align: center; border-bottom: 1px solid #1e293b; font-weight: bold; font-size: 12px;">L</th>
                <th style="color: #00d2ff; padding: 8px 0; text-align: center; border-bottom: 1px solid #1e293b; font-weight: bold; font-size: 12px;">M</th>
                <th style="color: #00d2ff; padding: 8px 0; text-align: center; border-bottom: 1px solid #1e293b; font-weight: bold; font-size: 12px;">M</th>
                <th style="color: #00d2ff; padding: 8px 0; text-align: center; border-bottom: 1px solid #1e293b; font-weight: bold; font-size: 12px;">J</th>
                <th style="color: #00d2ff; padding: 8px 0; text-align: center; border-bottom: 1px solid #1e293b; font-weight: bold; font-size: 12px;">V</th>
                <th style="color: #00d2ff; padding: 8px 0; text-align: center; border-bottom: 1px solid #1e293b; font-weight: bold; font-size: 12px;">S</th>
                <th style="color: #00d2ff; padding: 8px 0; text-align: center; border-bottom: 1px solid #1e293b; font-weight: bold; font-size: 12px;">D</th>
                <th style="color: #00d2ff; padding: 8px 0; text-align: center; border-bottom: 1px solid #1e293b; font-weight: bold; font-size: 12px;">∑</th>
            </tr>
    """
    for week in cal:
        html += "<tr>"
        week_total = 0.0
        has_trades = False
        
        for day in week:
            if day == 0:
                html += '<td style="border: 1px solid #10192d; height: 70px; background-color: #080f1e;"></td>'
            else:
                pnl = daily_pnl.get(day, None)
                td_style = "border: 1px solid #10192d; height: 70px; vertical-align: top; padding: 6px; background-color: #080f1e; position: relative;"
                pnl_html = ""
                
                if pnl is not None:
                    has_trades = True
                    week_total += pnl
                    if pnl > 0:
                        td_style = "border: 1px solid #00d284; border-bottom: 3.5px solid #00ffa3; height: 70px; vertical-align: top; padding: 6px; background-color: rgba(0, 255, 163, 0.08); position: relative;"
                        pnl_html = f'<div style="color: #00ffa3; font-weight: bold; font-size: 10px; position: absolute; bottom: 5px; right: 5px;">+{pnl:.2f}$</div>'
                    elif pnl < 0:
                        td_style = "border: 1px solid #d22d56; border-bottom: 3.5px solid #ff3366; height: 70px; vertical-align: top; padding: 6px; background-color: rgba(255, 51, 102, 0.08); position: relative;"
                        pnl_html = f'<div style="color: #ff3366; font-weight: bold; font-size: 10px; position: absolute; bottom: 5px; right: 5px;">{pnl:.2f}$</div>'
                    else:
                        pnl_html = f'<div style="color: #94a3b8; font-weight: bold; font-size: 10px; position: absolute; bottom: 5px; right: 5px;">0.00$</div>'
                
                html += f'<td style="{td_style}"><div style="font-size: 12px; color: #94a3b8; font-weight: bold;">{day}</div>{pnl_html}</td>'
        
        total_style = "border: 1px solid #10192d; height: 70px; vertical-align: middle; text-align: center; background-color: #060b16;"
        total_pnl_html = ""
        
        if has_trades:
            if week_total > 0:
                total_style = "border: 1px solid #00d284; height: 70px; vertical-align: middle; text-align: center; background-color: rgba(0, 255, 163, 0.06);"
                total_pnl_html = f'<div style="color: #00ffa3; font-weight: bold; font-size: 11px; margin-top: 4px;">+{week_total:.2f}$</div>'
            elif week_total < 0:
                total_style = "border: 1px solid #d22d56; height: 70px; vertical-align: middle; text-align: center; background-color: rgba(255, 51, 102, 0.06);"
                total_pnl_html = f'<div style="color: #ff3366; font-weight: bold; font-size: 11px; margin-top: 4px;">{week_total:.2f}$</div>'
            else:
                total_pnl_html = f'<div style="color: #94a3b8; font-weight: bold; font-size: 11px; margin-top: 4px;">0.00$</div>'
        
        html += f'<td style="{total_style}"><div style="font-size: 9px; color: #64748b; font-weight: bold; letter-spacing: 1px;">TOTAL</div>{total_pnl_html}</td>'
        html += "</tr>"
        
    html += "</table></div>"
    return html

# ==========================================
# SISTEMA DE LOGIN
# ==========================================
def custom_pin_pad():
    st.markdown(CSS_LOGIN, unsafe_allow_html=True)
    if "pin_input" not in st.session_state: st.session_state.pin_input = ""
    st.markdown("<br><h2 style='text-align: center; color: #00d2ff;'>⚡ TRADING LAB LOGIN</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b;'>Ingresa tu PIN de seguridad</p>", unsafe_allow_html=True)
    pin_display = "● " * len(st.session_state.pin_input) + "○ " * (4 - len(st.session_state.pin_input))
    st.markdown(f"<h1 style='text-align: center; letter-spacing: 15px; color: #fff;'>{pin_display}</h1><br>", unsafe_allow_html=True)
    
    _, col1, col2, col3, _ = st.columns([1.5, 0.4, 0.4, 0.4, 1.5])
    def add_digit(digit):
        if len(st.session_state.pin_input) < 4: st.session_state.pin_input += str(digit)
    def clear_pin(): st.session_state.pin_input = ""

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
    
    for col_query in [
        "ALTER TABLE trades ADD COLUMN IF NOT EXISTS emotion VARCHAR(50) DEFAULT 'Neutral 😐';",
        "ALTER TABLE trades ADD COLUMN IF NOT EXISTS confidence VARCHAR(50) DEFAULT 'Alto 🔥';",
        "ALTER TABLE trades ADD COLUMN IF NOT EXISTS session VARCHAR(50) DEFAULT 'New York';",
        "ALTER TABLE trades ADD COLUMN IF NOT EXISTS observation TEXT DEFAULT '';"
    ]:
        try:
            c.execute(col_query)
        except:
            pass
    conn.commit()

    def get_accounts(): return pd.read_sql_query("SELECT * FROM accounts", conn)
    def get_trades(account_id): return pd.read_sql_query(f"SELECT * FROM trades WHERE account_id = {account_id} ORDER BY date_time ASC", conn)

    # ==========================================
    # BARRA LATERAL (SIDEBAR FUTURISTA)
    # ==========================================
    st.sidebar.markdown('<div class="sidebar-title">⚡ Panel Lab</div>', unsafe_allow_html=True)
    st.sidebar.markdown('<p style="color: #64748b; font-size: 11px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 10px;">Navegación</p>', unsafe_allow_html=True)
    
    menu = st.sidebar.radio("", ["📊 Dashboard Principal", "🏦 Gestionar Cuentas"], label_visibility="collapsed")
    
    st.sidebar.markdown("<br><br><br>", unsafe_allow_html=True)
    st.sidebar.markdown("<hr style='border-color: #1e293b;'>", unsafe_allow_html=True)
    
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
                conn.commit()
                st.success("✅ Cuenta creada correctamente.")
                time.sleep(0.5)
                st.rerun()
        st.dataframe(get_accounts(), use_container_width=True, hide_index=True)

    elif menu == "📊 Dashboard Principal":
        df_accounts = get_accounts()
        if df_accounts.empty:
            st.warning("⚠️ Crea una cuenta en el menú lateral para iniciar.")
        else:
            st.markdown('<div style="color: #64748b; font-size: 11px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 5px;">⚡ Selector de Cuenta Activa</div>', unsafe_allow_html=True)
            col_sel, _ = st.columns([1, 2])
            with col_sel:
                account_options = df_accounts.apply(lambda x: f"🌐 {x['broker']} — {x['account_name']} (ID:{x['id']})", axis=1).tolist()
                selected_account_str = st.selectbox("CUENTA ACTIVA:", account_options, label_visibility="collapsed")
            
            selected_acc_id = int(selected_account_str.split("ID:")[1].replace(")", ""))
            initial_balance = float(df_accounts[df_accounts['id'] == selected_acc_id]['initial_balance'].values[0])
            df_trades = get_trades(selected_acc_id)

            win_rate, net_profit, wins, losses = 0.0, 0.0, 0, 0
            current_balance = initial_balance
            total_trades = len(df_trades)
            score_win = score_pf = score_awal = score_rec = score_dd = score_cons = 0
            overall_score = 0
            total_win_sum = 0.0
            total_loss_sum = 0.0
            
            if total_trades > 0:
                df_trades['pnl'] = pd.to_numeric(df_trades['pnl'], errors='coerce').fillna(0.0)
                df_trades['date_time'] = pd.to_datetime(df_trades['date_time'])
                
                wins = len(df_trades[df_trades['result'].str.contains("WIN")])
                losses = len(df_trades[df_trades['result'].str.contains("LOSS")])
                ties = len(df_trades[df_trades['result'].str.contains("EMPATE")])
                win_rate = (wins / (total_trades - ties)) * 100 if (total_trades - ties) > 0 else 0.0
                net_profit = float(df_trades['pnl'].sum())
                current_balance = initial_balance + net_profit
                
                total_win_sum = float(df_trades[df_trades['pnl'] > 0]['pnl'].sum())
                total_loss_sum = float(df_trades[df_trades['pnl'] < 0]['pnl'].sum())
                
                score_win = win_rate
                gross_profit = total_win_sum
                gross_loss = abs(total_loss_sum)
                pf = gross_profit / gross_loss if gross_loss > 0 else 2.5
                score_pf = min((pf / 2.0) * 100, 100)
                
                avg_win = df_trades[df_trades['pnl'] > 0]['pnl'].mean()
                avg_loss = abs(df_trades[df_trades['pnl'] < 0]['pnl'].mean())
                if pd.isna(avg_win): avg_win = 0
                if pd.isna(avg_loss) or avg_loss == 0: avg_loss = 1
                score_awal = min((avg_win / avg_loss / 1.5) * 100, 100)
                
                daily_pnl_score = df_trades.groupby(df_trades['date_time'].dt.date)['pnl'].sum()
                score_cons = (len(daily_pnl_score[daily_pnl_score > 0]) / len(daily_pnl_score) * 100) if len(daily_pnl_score) > 0 else 0
                
                df_trades['equity'] = initial_balance + df_trades['pnl'].cumsum()
                df_trades['peak'] = df_trades['equity'].cummax()
                df_trades['dd'] = (df_trades['peak'] - df_trades['equity']) / df_trades['peak']
                max_dd = df_trades['dd'].max()
                score_dd = max(100 - (max_dd * 500), 0)
                score_rec = (score_win * 0.7) + (score_pf * 0.3)
                overall_score = int(sum([score_win, score_pf, score_awal, score_rec, score_dd, score_cons]) / 6)

            # ==========================================
            # 5 PANELES SUPERIORES EXACTOS
            # ==========================================
            st.markdown("<br>", unsafe_allow_html=True)
            kpi_cols = st.columns(5)
            color_pnl = "win" if net_profit >= 0 else "loss"
            signo = "+" if net_profit >= 0 else ""
            
            with kpi_cols[0]:
                st.markdown(f'''
                <div class="kpi-card-exact">
                    <div style="color: #64748b; font-size: 11px; font-weight: 600; letter-spacing: 1.5px; text-transform: uppercase;">WIN RATE</div>
                    <div style="color: #00d2ff; font-size: 26px; font-weight: 700; margin: 0;">{win_rate:.1f}%</div>
                    <div style="color: #94a3b8; font-size: 11px;">{wins} Ganadas / {losses} Perdidas</div>
                </div>
                ''', unsafe_allow_html=True)
                
            with kpi_cols[1]:
                st.markdown(f'''
                <div class="kpi-card-exact">
                    <div style="color: #64748b; font-size: 11px; font-weight: 600; letter-spacing: 1.5px; text-transform: uppercase;">AVG WIN / LOSS</div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 2px;">
                        <span style="color: #94a3b8; font-size: 11px; font-weight: 500;">WIN</span>
                        <span style="color: #00ffa3; font-size: 15px; font-weight: bold;">${total_win_sum:.2f}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 2px;">
                        <span style="color: #94a3b8; font-size: 11px; font-weight: 500;">LOSS</span>
                        <span style="color: #ff3366; font-size: 15px; font-weight: bold;">-${abs(total_loss_sum):.2f}</span>
                    </div>
                </div>
                ''', unsafe_allow_html=True)

            with kpi_cols[2]:
                pnl_color_hex = "#00ffa3" if net_profit >= 0 else "#ff3366"
                st.markdown(f'''
                <div class="kpi-card-exact">
                    <div style="color: #64748b; font-size: 11px; font-weight: 600; letter-spacing: 1.5px; text-transform: uppercase;">NET PNL (BENEFICIO)</div>
                    <div style="color: {pnl_color_hex}; font-size: 26px; font-weight: 700; margin: 0; text-shadow: 0 0 10px rgba(0,255,163,0.2);">{signo}${net_profit:.2f}</div>
                    <div style="color: #94a3b8; font-size: 11px;">Periodo actual</div>
                </div>
                ''', unsafe_allow_html=True)

            with kpi_cols[3]:
                st.markdown(f'''
                <div class="kpi-card-exact">
                    <div style="color: #64748b; font-size: 11px; font-weight: 600; letter-spacing: 1.5px; text-transform: uppercase;">BALANCE TOTAL</div>
                    <div style="color: #ffffff; font-size: 26px; font-weight: 700; margin: 0;">${current_balance:.2f}</div>
                    <div style="color: #94a3b8; font-size: 11px;">Capital disponible</div>
                </div>
                ''', unsafe_allow_html=True)
                
            with kpi_cols[4]:
                st.markdown(f'''
                <div class="kpi-card-exact">
                    <div style="color: #64748b; font-size: 11px; font-weight: 600; letter-spacing: 1.5px; text-transform: uppercase;">TRADES EJECUTADOS</div>
                    <div style="color: #00d2ff; font-size: 26px; font-weight: 700; margin: 0;">{total_trades}</div>
                    <div style="color: #94a3b8; font-size: 11px;">Volumen total</div>
                </div>
                ''', unsafe_allow_html=True)

            # ==========================================
            # LAYOUT SUPERIOR: CALENDARIO, PERFIL, EMOCIÓN, CONFIANZA, SESIONES, OBSERVACIONES
            # ==========================================
            col_cal, col_prof, col_emo, col_conf, col_sess, col_obs = st.columns([2.0, 1.2, 1.2, 1.2, 1.2, 1.2])
            
            with col_cal:
                st.markdown(render_calendar(df_trades), unsafe_allow_html=True)
                
            with col_prof:
                categories = ['Win %', 'Profit Factor', 'Avg Win/Loss', 'Recovery', 'Drawdown', 'Consistency']
                values = [score_win, score_pf, score_awal, score_rec, score_dd, score_cons]
                values_loop = values + [values[0]]
                categories_loop = categories + [categories[0]]
                
                fig_radar = go.Figure(data=go.Scatterpolar(
                    r=values_loop, theta=categories_loop, fill='toself',
                    fillcolor='rgba(0, 255, 163, 0.25)', line=dict(color='#00ffa3', width=2), marker=dict(size=1)
                ))
                fig_radar.update_layout(
                    polar=dict(radialaxis=dict(visible=False, range=[0, 100]), angularaxis=dict(color='#94a3b8', gridcolor='#1e293b', linecolor='#1e293b', gridwidth=1), bgcolor='rgba(0,0,0,0)'),
                    showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=25, r=25, t=10, b=10), height=170
                )

                st.markdown('<div class="profile-card">', unsafe_allow_html=True)
                st.markdown('<div class="profile-title">Perfil de Trading <span style="float:right; color:#64748b; font-size: 14px; font-weight:normal;">ⓘ</span></div>', unsafe_allow_html=True)
                st.plotly_chart(fig_radar, use_container_width=True, config={'displayModeBar': False})
                st.markdown(f'''
                    <div style="margin-top: -10px;">
                        <div style="display: flex; justify-content: space-between; align-items: flex-end;">
                            <div style="color: #94a3b8; font-size: 11px;">Trading Score</div>
                            <div><span style="color: #00ffa3; font-size: 20px; font-weight: bold;">{overall_score}</span><span style="color: #64748b; font-size: 10px;"> / 100</span></div>
                        </div>
                        <div class="progress-bar-bg"><div class="progress-bar-fill" style="width: {overall_score}%;"></div></div>
                        <div style="display: flex; justify-content: space-between; margin-top: 3px;">
                            <div style="color: #64748b; font-size: 8px; font-weight: bold;">NOVATO</div>
                            <div style="color: #64748b; font-size: 8px; font-weight: bold;">PRO</div>
                        </div>
                    </div>
                </div>
                ''', unsafe_allow_html=True)

            with col_emo:
                emoji_res = "😐"
                label_res = "Desconocido"
                if not df_trades.empty and 'emotion' in df_trades.columns:
                    seven_days_ago = datetime.now() - timedelta(days=7)
                    recent_trades = df_trades[df_trades['date_time'] >= seven_days_ago]
                    if not recent_trades.empty and 'emotion' in recent_trades.columns:
                        top_emotion = recent_trades['emotion'].mode()
                        if not top_emotion.empty:
                            full_emo = top_emotion[0]
                            if " " in full_emo:
                                parts = full_emo.split(" ")
                                label_res = parts[0]
                                emoji_res = parts[1]
                            else:
                                label_res = full_emo

                st.markdown(f'''
                <div class="futuristic-card">
                    <div>
                        <div style="color: #ffffff; font-size: 13px; font-weight: bold; letter-spacing: 1px;">ESTADO EMOCIONAL</div>
                        <div style="color: #64748b; font-size: 10px; font-weight: 600; letter-spacing: 1px;">BIOMETRÍA & SENTIMIENTO</div>
                        <div style="position: absolute; top: 15px; right: 15px; background: rgba(0, 210, 255, 0.1); border: 1px solid #1e293b; border-radius: 50%; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; color: #00d2ff; font-size: 14px;">🧠</div>
                    </div>
                    <div style="text-align: center; padding: 10px 0;">
                        <div style="font-size: 45px; margin-bottom: 5px;">{emoji_res}</div>
                        <div style="color: #ffffff; font-size: 22px; font-weight: bold; margin-bottom: 2px;">{label_res}</div>
                        <div style="color: #94a3b8; font-size: 11px; font-weight: 500;">Promedio 7 días</div>
                    </div>
                    <div style="text-align: center; color: #00d2ff; font-size: 12px; font-weight: bold; padding: 6px; border: 1px solid #1e293b; border-radius: 8px; background: rgba(0,210,255,0.05);">Biometría Activa</div>
                </div>
                ''', unsafe_allow_html=True)

            with col_conf:
                conf_label = "Sin datos"
                conf_color = "#64748b"
                if not df_trades.empty and 'confidence' in df_trades.columns:
                    seven_days_ago = datetime.now() - timedelta(days=7)
                    recent_trades = df_trades[df_trades['date_time'] >= seven_days_ago]
                    if not recent_trades.empty:
                        top_conf = recent_trades['confidence'].mode()
                        if not top_conf.empty:
                            conf_label = top_conf[0]
                            if "Alto" in conf_label or "🔥" in conf_label: conf_color = "#00ffa3"
                            elif "Medio" in conf_label or "⚡" in conf_label: conf_color = "#ffb800"
                            else: conf_color = "#ff3366"

                st.markdown(f'''
                <div class="futuristic-card">
                    <div>
                        <div style="color: #ffffff; font-size: 13px; font-weight: bold; letter-spacing: 1px;">NIVEL DE CONFIANZA</div>
                        <div style="color: #64748b; font-size: 10px; font-weight: 600; letter-spacing: 1px;">SEGURIDAD OPERATIVA</div>
                        <div style="position: absolute; top: 15px; right: 15px; background: rgba(255, 184, 0, 0.1); border: 1px solid #1e293b; border-radius: 50%; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; color: #ffb800; font-size: 14px;">🎯</div>
                    </div>
                    <div style="text-align: center; padding: 10px 0;">
                        <div style="font-size: 45px; margin-bottom: 5px;">🛡️</div>
                        <div style="color: {conf_color}; font-size: 22px; font-weight: bold; margin-bottom: 2px;">{conf_label}</div>
                        <div style="color: #94a3b8; font-size: 11px; font-weight: 500;">Promedio 7 días</div>
                    </div>
                    <div style="text-align: center; color: {conf_color}; font-size: 12px; font-weight: bold; padding: 6px; border: 1px solid #1e293b; border-radius: 8px; background: rgba(255,255,255,0.02);">Psico-Trading</div>
                </div>
                ''', unsafe_allow_html=True)

            with col_sess:
                utc_hour = datetime.utcnow().hour
                sydney_active = 22 <= utc_hour or utc_hour < 7
                tokyo_active = 0 <= utc_hour < 9
                london_active = 8 <= utc_hour < 16
                ny_active = 13 <= utc_hour < 22

                def badge_html(name, is_active):
                    cls = "active" if is_active else ""
                    dot = "dot-live" if is_active else "dot-closed"
                    color = "#00ffa3" if is_active else "#64748b"
                    return f'<div class="session-badge {cls}"><span style="color: #ffffff; font-size: 11px; font-weight: bold;">{name}</span><span><span class="{dot}"></span> <span style="color: {color}; font-size: 10px; font-weight: bold;">{"ACTIVA" if is_active else "CERRADA"}</span></span></div>'

                st.markdown(f'''
                <div class="futuristic-card">
                    <div>
                        <div style="color: #ffffff; font-size: 13px; font-weight: bold; letter-spacing: 1px;">SESIÓN DE TRADING</div>
                        <div style="color: #64748b; font-size: 10px; font-weight: 600; letter-spacing: 1px;">MERCADOS GLOBALES</div>
                        <div style="position: absolute; top: 15px; right: 15px; background: rgba(0, 255, 163, 0.1); border: 1px solid #1e293b; border-radius: 50%; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; color: #00ffa3; font-size: 14px;">🌐</div>
                    </div>
                    <div style="padding: 5px 0;">
                        {badge_html("Londres", london_active)}
                        {badge_html("New York", ny_active)}
                        {badge_html("Sídney", sydney_active)}
                        {badge_html("Tokio", tokyo_active)}
                    </div>
                    <div style="text-align: center; color: #00d2ff; font-size: 10px; font-weight: bold;">Reloj Mundial UTC</div>
                </div>
                ''', unsafe_allow_html=True)

            with col_obs:
                last_obs = "Sin notas recientes."
                if not df_trades.empty and 'observation' in df_trades.columns:
                    valid_obs = df_trades[df_trades['observation'].notnull() & (df_trades['observation'] != '')]
                    if not valid_obs.empty:
                        last_obs = valid_obs.iloc[-1]['observation']
                        if len(last_obs) > 60: last_obs = last_obs[:57] + "..."

                st.markdown(f'''
                <div class="futuristic-card">
                    <div>
                        <div style="color: #ffffff; font-size: 13px; font-weight: bold; letter-spacing: 1px;">OBSERVACIONES</div>
                        <div style="color: #64748b; font-size: 10px; font-weight: 600; letter-spacing: 1px;">NOTAS & BITÁCORA</div>
                        <div style="position: absolute; top: 15px; right: 15px; background: rgba(210, 0, 255, 0.1); border: 1px solid #1e293b; border-radius: 50%; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; color: #d200ff; font-size: 14px;">📝</div>
                    </div>
                    <div style="background: rgba(11, 19, 37, 0.8); border: 1px solid #1e293b; border-radius: 10px; padding: 12px; margin: 10px 0; min-height: 80px; max-height: 90px; overflow-y: auto;">
                        <div style="color: #94a3b8; font-size: 11px; font-style: italic; line-height: 1.4;">"{last_obs}"</div>
                    </div>
                    <div style="text-align: center; color: #d200ff; font-size: 11px; font-weight: bold; padding: 6px; border: 1px solid #1e293b; border-radius: 8px; background: rgba(210, 0, 255, 0.05);">Bitácora Activa</div>
                </div>
                ''', unsafe_allow_html=True)

            # ==========================================
            # PANELES DE GRÁFICOS: 3 COLUMNAS (CRECIMIENTO, P&L DIARIO Y DONUT RATIO)
            # ==========================================
            st.markdown("<br>", unsafe_allow_html=True)
            col_chart1, col_chart2, col_chart3 = st.columns(3)

            # 1. Crecimiento Acumulado
            with col_chart1:
                pct_growth = (net_profit / initial_balance * 100) if initial_balance > 0 else 0.0
                sign_growth = "+" if net_profit >= 0 else ""
                
                chart_box_1 = textwrap.dedent(f"""
                <div class="chart-box">
                    <div style="display: flex; justify-content: space-between; align-items: center; padding-bottom: 8px; border-bottom: 1px solid #1e293b; margin-bottom: 12px;">
                        <div>
                            <div style="font-size: 15px; font-weight: bold; color: #ffffff;">📁 Crecimiento Acumulado</div>
                            <div style="font-size: 10px; color: #64748b;">P&L Acumulado Diario</div>
                        </div>
                        <div style="text-align: right; font-size: 15px; font-weight: bold; color: #00ffa3;">
                            {sign_growth}${net_profit:.2f} <span style="font-size: 10px;">{sign_growth}{pct_growth:.1f}%</span>
                        </div>
                    </div>
                """)
                st.markdown(chart_box_1.strip(), unsafe_allow_html=True)
                
                if total_trades > 0:
                    df_trades['Trade #'] = range(1, len(df_trades) + 1)
                    fig_growth = px.area(df_trades, x='Trade #', y='equity', markers=True)
                    fig_growth.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#94a3b8'), margin=dict(l=0, r=0, t=5, b=0),
                        yaxis=dict(gridcolor='#1e293b', title=''), xaxis=dict(gridcolor='#1e293b', title=''),
                        height=210
                    )
                    fig_growth.update_traces(line_color='#00d2ff', fillcolor='rgba(0, 210, 255, 0.15)')
                    st.plotly_chart(fig_growth, use_container_width=True, config={'displayModeBar': False})
                else:
                    st.markdown('<div style="text-align: center; color: #64748b; padding: 40px;">Sin datos disponibles.</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # 2. P&L Diario
            with col_chart2:
                green_days_count = 0
                red_days_count = 0
                best_day_val = 0.0
                best_day_date = "N/A"
                worst_day_val = 0.0
                worst_day_date = "N/A"

                if total_trades > 0:
                    df_daily = df_trades.copy()
                    df_daily['day_only'] = df_daily['date_time'].dt.date
                    df_grouped = df_daily.groupby('day_only')['pnl'].sum().reset_index()
                    
                    green_days_count = len(df_grouped[df_grouped['pnl'] > 0])
                    red_days_count = len(df_grouped[df_grouped['pnl'] < 0])
                    
                    if not df_grouped.empty:
                        best_row = df_grouped.loc[df_grouped['pnl'].idxmax()]
                        best_day_val = best_row['pnl']
                        best_day_date = best_row['day_only'].strftime('%d de %B de %Y')
                        
                        worst_row = df_grouped.loc[df_grouped['pnl'].idxmin()]
                        worst_day_val = worst_row['pnl']
                        worst_day_date = worst_row['day_only'].strftime('%d de %B de %Y')

                chart_box_2 = textwrap.dedent(f"""
                <div class="chart-box">
                    <div style="display: flex; justify-content: space-between; align-items: center; padding-bottom: 8px; border-bottom: 1px solid #1e293b; margin-bottom: 12px;">
                        <div>
                            <div style="font-size: 15px; font-weight: bold; color: #ffffff;">📊 P&L Diario</div>
                            <div style="font-size: 10px; color: #64748b;">Ganancias y pérdidas por día</div>
                        </div>
                        <div style="text-align: right; font-size: 10px; color: #94a3b8;">
                            <span style="color: #00ffa3;">🟢 {green_days_count}D</span> &nbsp; <span style="color: #ff3366;">🔴 {red_days_count}D</span>
                        </div>
                    </div>
                """)
                st.markdown(chart_box_2.strip(), unsafe_allow_html=True)

                if total_trades > 0:
                    fig_daily = px.bar(df_grouped, x='day_only', y='pnl', color='pnl',
                                       color_continuous_scale=['#ff3366', '#00ffa3'])
                    fig_daily.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#94a3b8'), margin=dict(l=0, r=0, t=5, b=0),
                        yaxis=dict(gridcolor='#1e293b', title=''), xaxis=dict(gridcolor='#1e293b', title=''),
                        coloraxis_showscale=False, height=110
                    )
                    st.plotly_chart(fig_daily, use_container_width=True, config={'displayModeBar': False})
                else:
                    st.markdown('<div style="text-align: center; color: #64748b; padding: 40px;">Sin datos diarios.</div>', unsafe_allow_html=True)

                sub_c1, sub_c2 = st.columns(2)
                with sub_c1:
                    best_card_html = textwrap.dedent(f"""
                    <div class="best-worst-card best-card">
                        <div style="font-size: 9px; font-weight: bold; color: #64748b; letter-spacing: 1px;">MEJOR DÍA</div>
                        <div style="font-size: 14px; font-weight: bold; color: #00ffa3; margin-top: 2px;">+{best_day_val:.2f}$</div>
                        <div style="font-size: 8px; color: #94a3b8; margin-top: 1px;">{best_day_date}</div>
                    </div>
                    """)
                    st.markdown(best_card_html.strip(), unsafe_allow_html=True)
                with sub_c2:
                    worst_card_html = textwrap.dedent(f"""
                    <div class="best-worst-card worst-card">
                        <div style="font-size: 9px; font-weight: bold; color: #64748b; letter-spacing: 1px;">PEOR DÍA</div>
                        <div style="font-size: 14px; font-weight: bold; color: #ff3366; margin-top: 2px;">{worst_day_val:.2f}$</div>
                        <div style="font-size: 8px; color: #94a3b8; margin-top: 1px;">{worst_day_date}</div>
                    </div>
                    """)
                    st.markdown(worst_card_html.strip(), unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)

            # 3. Nuevo Panel: Ratio de Impacto P&L (Donut Chart Cuántico)
            with col_chart3:
                chart_box_3 = textwrap.dedent(f"""
                <div class="chart-box">
                    <div style="display: flex; justify-content: space-between; align-items: center; padding-bottom: 8px; border-bottom: 1px solid #1e293b; margin-bottom: 12px;">
                        <div>
                            <div style="font-size: 15px; font-weight: bold; color: #ffffff;">🍩 Ratio de Impacto P&L</div>
                            <div style="font-size: 10px; color: #64748b;">Ganadas vs Pérdidas ($)</div>
                        </div>
                    </div>
                """)
                st.markdown(chart_box_3.strip(), unsafe_allow_html=True)

                if total_trades > 0:
                    gross_win = float(df_trades[df_trades['pnl'] > 0]['pnl'].sum())
                    gross_loss = float(abs(df_trades[df_trades['pnl'] < 0]['pnl'].sum()))
                    if gross_win == 0 and gross_loss == 0:
                        gross_win = 1.0

                    fig_donut = go.Figure(data=[go.Pie(
                        labels=['Ganadas', 'Pérdidas'],
                        values=[gross_win, gross_loss],
                        hole=0.68,
                        marker_colors=['#00ffa3', '#ff3366'],
                        textinfo='percent',
                        textfont=dict(color='#ffffff', size=11),
                        hoverinfo='label+value+percent'
                    )])

                    net_color = "#00ffa3" if net_profit >= 0 else "#ff3366"
                    sign_net = "+" if net_profit >= 0 else ""

                    fig_donut.update_layout(
                        showlegend=True,
                        legend=dict(orientation="h", yanchor="bottom", y=-0.22, xanchor="center", x=0.5, font=dict(color="#94a3b8", size=10)),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        margin=dict(l=5, r=5, t=5, b=5),
                        height=195,
                        annotations=[dict(
                            text=f"<b style='color:{net_color}; font-size:14px;'>{sign_net}${net_profit:.2f}</b><br><span style='color:#64748b; font-size:9px;'>NETO</span>",
                            x=0.5, y=0.5, showarrow=False, font=dict(size=11, color="#ffffff")
                        )]
                    )
                    st.plotly_chart(fig_donut, use_container_width=True, config={'displayModeBar': False})
                else:
                    st.markdown('<div style="text-align: center; color: #64748b; padding: 40px;">Sin datos disponibles.</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # ==========================================
            # REGISTRO DE OPERACIONES Y FORMULARIO FUTURISTA ANIMADO
            # ==========================================
            st.markdown("<br>", unsafe_allow_html=True)
            with st.expander("⚡ REGISTRAR NUEVO TRADE", expanded=True):
                st.markdown('<p style="color: #00d2ff; font-size: 12px; font-weight: 700; letter-spacing: 1.5px; margin-bottom: 20px; text-shadow: 0 0 10px rgba(0,210,255,0.3);">⚡ MÓDULO DE EJECUCIÓN CUÁNTICA</p>', unsafe_allow_html=True)
                with st.form("trade_form", clear_on_submit=True):
                    c1, c2, c3, c4 = st.columns(4)
                    with c1:
                        market = st.selectbox("🌐 Mercado", ["Opciones Binarias", "Forex"])
                        asset = st.text_input("💎 Activo (Ej. EURUSD)").upper()
                        session = st.selectbox("🌍 Sesión", ["New York", "Londres", "Sídney", "Tokio"])
                    with c2:
                        direction = st.selectbox("📈 Dirección", ["CALL / BUY 🟢", "PUT / SELL 🔴"])
                        amount = st.number_input("💵 Inversión / Lote ($)", min_value=0.1, value=10.0, step=1.0)
                        confidence = st.selectbox("🎯 Nivel de Confianza", ["Alto 🔥", "Medio ⚡", "Bajo ⚠️"])
                    with c3:
                        result = st.selectbox("🏆 Resultado", ["WIN 🎉", "LOSS ❌", "EMPATE ➖"])
                        emotion = st.selectbox("🧠 Estado Emocional", ["Neutral 😐", "Confiado 😎", "Enfocado 🎯", "Ansioso 😰", "Frustrado 😤", "Eufórico 🤩"])
                        payout_percent = st.number_input("📊 % Retorno (Binarias)", min_value=1, max_value=100, value=85)
                    with c4:
                        date_time = st.date_input("📅 Fecha", datetime.today())
                        time_input = st.time_input("⏰ Hora", datetime.now().time())
                        observation = st.text_input("📝 Observaciones / Notas")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    guardar_ejecucion = st.form_submit_button("🚀 EJECUTAR Y REGISTRAR TRADE")
                    
                    if guardar_ejecucion and asset:
                        try:
                            if "WIN" in result:
                                pnl_calc = amount * (payout_percent / 100.0) if market == "Opciones Binarias" else amount
                            elif "LOSS" in result:
                                pnl_calc = -amount
                            else:
                                pnl_calc = 0.0

                            dt_string = f"{date_time} {time_input}"
                            c.execute('''INSERT INTO trades (account_id, date_time, market, asset, direction, amount, result, pnl, emotion, confidence, session, observation) 
                                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''', 
                                      (selected_acc_id, dt_string, market, asset, direction, amount, result, pnl_calc, emotion, confidence, session, observation))
                            conn.commit()
                            st.success(f"✅ Trade registrado con éxito en la red! PnL: {pnl_calc:+.2f}$")
                            time.sleep(0.5)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error guardando en la BD: {e}")

            # ==========================================
            # HISTORIAL DE OPERACIONES EXPANDIBLE Y FUTURISTA
            # ==========================================
            st.markdown("<br>", unsafe_allow_html=True)
            with st.expander("📋 HISTORIAL DE OPERACIONES Y BITÁCORA CUÁNTICA", expanded=False):
                st.markdown('<p style="color: #00d2ff; font-size: 12px; font-weight: 700; letter-spacing: 1.5px; margin-bottom: 15px; text-shadow: 0 0 10px rgba(0,210,255,0.3);">⚡ FILTRADO TEMPORAL Y REGISTRO DE EJECUCIONES</p>', unsafe_allow_html=True)
                
                if total_trades > 0:
                    f_col1, _ = st.columns([2, 2])
                    with f_col1:
                        time_filter = st.selectbox("⏱️ Filtrar Temporalidad", ["Todo el Histórico", "Diario", "Esta Semana", "Este Mes", "Este Año"])
                    
                    df_filtered = df_trades.copy()
                    df_filtered['date_time'] = pd.to_datetime(df_filtered['date_time'])
                    now = datetime.now()
                    
                    if time_filter == "Diario":
                        df_filtered = df_filtered[df_filtered['date_time'].dt.date == now.date()]
                    elif time_filter == "Esta Semana":
                        start_of_week = now - timedelta(days=now.weekday())
                        df_filtered = df_filtered[df_filtered['date_time'] >= pd.to_datetime(start_of_week.date())]
                    elif time_filter == "Este Mes":
                        df_filtered = df_filtered[(df_filtered['date_time'].dt.year == now.year) & (df_filtered['date_time'].dt.month == now.month)]
                    elif time_filter == "Este Año":
                        df_filtered = df_filtered[df_filtered['date_time'].dt.year == now.year]
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # 1. TABLA ANALÍTICA GENERAL (PRIMERO)
                    st.markdown('<div style="color: #ffffff; font-size: 16px; font-weight: bold; margin-bottom: 10px;">📊 Tabla Analítica General</div>', unsafe_allow_html=True)
                    if not df_filtered.empty:
                        display_df = df_filtered.drop(columns=['id', 'account_id', 'equity', 'peak', 'dd']).copy()
                        st.dataframe(display_df, use_container_width=True, hide_index=True)
                    else:
                        st.markdown('<div style="color: #64748b; padding: 15px; text-align: center;">No hay operaciones para la temporalidad seleccionada.</div>', unsafe_allow_html=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # 2. DETALLADO DE TRADES CON CONTENEDORES NATIVOS (SEGUNDO)
                    st.markdown('<div style="color: #ffffff; font-size: 16px; font-weight: bold; margin-bottom: 10px;">🔍 Detallado Cuántico de Ejecuciones</div>', unsafe_allow_html=True)
                    if not df_filtered.empty:
                        for idx, row in df_filtered.iterrows():
                            pnl_val = float(row['pnl'])
                            res_color = "#00ffa3" if pnl_val > 0 else "#ff3366" if pnl_val < 0 else "#94a3b8"
                            sign_pnl = "+" if pnl_val > 0 else ""
                            obs_text = row.get('observation', '')
                            
                            with st.container(border=True):
                                col_card1, col_card2 = st.columns([3, 1])
                                with col_card1:
                                    st.markdown(f"<span style='color: #00d2ff; font-weight: bold; font-size: 13px;'>💎 {row['asset']} &nbsp;|&nbsp; <b style='color:#e2e8f0'>{row['market']}</b></span>", unsafe_allow_html=True)
                                    st.markdown(f"<span style='color: #64748b; font-size: 11px;'>📅 {row['date_time']}</span>", unsafe_allow_html=True)
                                    st.markdown(f"""
                                    <div style="color: #94a3b8; font-size: 11px; margin-top: 4px;">
                                        Dir: <b style="color:#e2e8f0">{row['direction']}</b> &nbsp;|&nbsp; 
                                        Sesión: <b style="color:#e2e8f0">{row.get('session', 'N/A')}</b> &nbsp;|&nbsp; 
                                        Confianza: <b style="color:#e2e8f0">{row.get('confidence', 'N/A')}</b> &nbsp;|&nbsp; 
                                        Emoción: <b style="color:#e2e8f0">{row.get('emotion', 'N/A')}</b>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    if obs_text:
                                        st.markdown(f"<div style='color: #d200ff; font-size: 11px; margin-top: 4px; font-style: italic;'>📝 Nota: {obs_text}</div>", unsafe_allow_html=True)
                                with col_card2:
                                    st.markdown(f"<div style='text-align: right; color: {res_color}; font-size: 16px; font-weight: bold;'>{sign_pnl}${pnl_val:.2f}</div>", unsafe_allow_html=True)
                                    st.markdown(f"<div style='text-align: right; color: #64748b; font-size: 11px; margin-top: 2px;'>Inv: ${row['amount']} | {row['result']}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown('<div style="color: #64748b; padding: 15px; text-align: center;">Sin registros detallados para mostrar.</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div style="text-align: center; color: #64748b; padding: 30px;">No hay operaciones registradas en esta cuenta.</div>', unsafe_allow_html=True)
