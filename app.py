import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import calendar
import time

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(page_title="Trading Lab Pro", page_icon="⚡", layout="wide")

# ==========================================
# BLOQUES DE CSS (LOGIN Y DASHBOARD)
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
    [data-testid="stSidebar"] { background-color: #0b1325; border-right: 1px solid #1e293b; }
    [data-testid="stHeader"] { background-color: transparent; }
    
    .kpi-card { background: linear-gradient(145deg, #111a2e, #0b1221); border-radius: 15px; padding: 20px; border: 1px solid #1e293b; box-shadow: 0 8px 32px 0 rgba(0,0,0,0.3); margin-bottom: 20px;}
    .kpi-title { color: #64748b; font-size: 13px; font-weight: 600; letter-spacing: 1.5px; margin-bottom: 5px;}
    .kpi-value { color: #00d2ff; font-size: 32px; font-weight: 700; margin: 0;}
    .kpi-value.loss { color: #ff3366; }
    .kpi-value.win { color: #00ffa3; }
    
    [data-testid="stButton"] button { background-color: #00d2ff !important; color: #000000 !important; border: none !important; border-radius: 8px !important; font-weight: bold !important; width: 100% !important; }
    [data-testid="stButton"] button:hover { background-color: #00a8cc !important; color: white !important;}
    
    /* Panel de Perfil y Emocional */
    .profile-card { background: linear-gradient(145deg, #070d19, #0b1325); border-radius: 15px; padding: 20px; border: 1px solid #1e293b; box-shadow: 0 8px 32px 0 rgba(0,0,0,0.3); margin-top: 20px; height: 96%;}
    .profile-title { color: #ffffff; font-size: 22px; font-weight: bold; margin-bottom: 0px;}
    .progress-bar-bg { height: 4px; background-color: #1e293b; border-radius: 2px; margin-top: 10px; position: relative; }
    .progress-bar-fill { height: 100%; background: linear-gradient(90deg, #ff3366, #ffb800, #00ffa3); border-radius: 2px; position: absolute; left: 0; top: 0; }

    /* Panel Estado Emocional Exacto */
    .emotion-card { background: linear-gradient(145deg, #070d19, #0b1325); border-radius: 16px; padding: 22px; border: 1px solid #1e293b; box-shadow: 0 8px 32px 0 rgba(0,0,0,0.4); margin-top: 20px; height: 96%; position: relative; display: flex; flex-direction: column; justify-content: space-between; }
    .emotion-header-title { color: #ffffff; font-size: 15px; font-weight: bold; letter-spacing: 1px; }
    .emotion-header-sub { color: #64748b; font-size: 11px; font-weight: 600; letter-spacing: 1px; margin-top: 2px; }
    .emotion-brain-icon { position: absolute; top: 20px; right: 20px; background: rgba(0, 210, 255, 0.1); border: 1px solid #1e293b; border-radius: 50%; width: 38px; height: 38px; display: flex; align-items: center; justify-content: center; color: #00d2ff; font-size: 18px; }
    .emotion-content { text-align: center; padding: 15px 0; }
    .emotion-emoji { font-size: 55px; margin-bottom: 8px; filter: drop-shadow(0 0 10px rgba(0,0,0,0.5)); }
    .emotion-status { color: #ffffff; font-size: 26px; font-weight: bold; margin-bottom: 2px; text-shadow: 0 0 15px rgba(255,255,255,0.2); }
    .emotion-subtext { color: #94a3b8; font-size: 13px; font-weight: 500; }
    .emotion-btn { background: transparent !important; border: 1px solid #1e293b !important; color: #94a3b8 !important; border-radius: 10px !important; padding: 10px !important; font-size: 14px !important; font-weight: 500 !important; width: 100% !important; text-align: center !important; transition: all 0.3s ease !important; }
    .emotion-btn:hover { border-color: #00d2ff !important; color: #00d2ff !important; background: rgba(0, 210, 255, 0.05) !important; }
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
    <div style="background-color: #070d19; padding: 20px; border-radius: 15px; border: 1px solid #1e293b; margin-top: 20px; box-shadow: 0 8px 32px 0 rgba(0,0,0,0.3); height: 100%;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <div style="color: #ffffff; font-size: 22px; font-weight: bold; display: flex; align-items: center; gap: 10px;">📅 Calendario</div>
            <div style="color: #ffffff; font-size: 16px; font-weight: bold; letter-spacing: 2px; text-transform: uppercase;">&lt; &nbsp; {month_name} &nbsp; &gt;</div>
        </div>
        <table style="width: 100%; border-collapse: collapse; table-layout: fixed;">
            <tr>
                <th style="color: #00d2ff; padding: 8px 0; text-align: center; border-bottom: 1px solid #1e293b; font-weight: bold; font-size: 13px;">L</th>
                <th style="color: #00d2ff; padding: 8px 0; text-align: center; border-bottom: 1px solid #1e293b; font-weight: bold; font-size: 13px;">M</th>
                <th style="color: #00d2ff; padding: 8px 0; text-align: center; border-bottom: 1px solid #1e293b; font-weight: bold; font-size: 13px;">M</th>
                <th style="color: #00d2ff; padding: 8px 0; text-align: center; border-bottom: 1px solid #1e293b; font-weight: bold; font-size: 13px;">J</th>
                <th style="color: #00d2ff; padding: 8px 0; text-align: center; border-bottom: 1px solid #1e293b; font-weight: bold; font-size: 13px;">V</th>
                <th style="color: #00d2ff; padding: 8px 0; text-align: center; border-bottom: 1px solid #1e293b; font-weight: bold; font-size: 13px;">S</th>
                <th style="color: #00d2ff; padding: 8px 0; text-align: center; border-bottom: 1px solid #1e293b; font-weight: bold; font-size: 13px;">D</th>
                <th style="color: #00d2ff; padding: 8px 0; text-align: center; border-bottom: 1px solid #1e293b; font-weight: bold; font-size: 13px;">∑</th>
            </tr>
    """
    for week in cal:
        html += "<tr>"
        week_total = 0.0
        has_trades = False
        
        for day in week:
            if day == 0:
                html += '<td style="border: 1px solid #10192d; height: 75px; background-color: #080f1e;"></td>'
            else:
                pnl = daily_pnl.get(day, None)
                td_style = "border: 1px solid #10192d; height: 75px; vertical-align: top; padding: 8px; background-color: #080f1e; position: relative;"
                pnl_html = ""
                
                if pnl is not None:
                    has_trades = True
                    week_total += pnl
                    if pnl > 0:
                        td_style = "border: 1px solid #00d284; border-bottom: 3.5px solid #00ffa3; height: 75px; vertical-align: top; padding: 8px; background-color: rgba(0, 255, 163, 0.08); position: relative;"
                        pnl_html = f'<div style="color: #00ffa3; font-weight: bold; font-size: 11px; position: absolute; bottom: 6px; right: 6px;">+{pnl:.2f}$</div>'
                    elif pnl < 0:
                        td_style = "border: 1px solid #d22d56; border-bottom: 3.5px solid #ff3366; height: 75px; vertical-align: top; padding: 8px; background-color: rgba(255, 51, 102, 0.08); position: relative;"
                        pnl_html = f'<div style="color: #ff3366; font-weight: bold; font-size: 11px; position: absolute; bottom: 6px; right: 6px;">{pnl:.2f}$</div>'
                    else:
                        pnl_html = f'<div style="color: #94a3b8; font-weight: bold; font-size: 11px; position: absolute; bottom: 6px; right: 6px;">0.00$</div>'
                
                html += f'<td style="{td_style}"><div style="font-size: 13px; color: #94a3b8; font-weight: bold;">{day}</div>{pnl_html}</td>'
        
        total_style = "border: 1px solid #10192d; height: 75px; vertical-align: middle; text-align: center; background-color: #060b16;"
        total_pnl_html = ""
        
        if has_trades:
            if week_total > 0:
                total_style = "border: 1px solid #00d284; height: 75px; vertical-align: middle; text-align: center; background-color: rgba(0, 255, 163, 0.06);"
                total_pnl_html = f'<div style="color: #00ffa3; font-weight: bold; font-size: 12px; margin-top: 5px;">+{week_total:.2f}$</div>'
            elif week_total < 0:
                total_style = "border: 1px solid #d22d56; height: 75px; vertical-align: middle; text-align: center; background-color: rgba(255, 51, 102, 0.06);"
                total_pnl_html = f'<div style="color: #ff3366; font-weight: bold; font-size: 12px; margin-top: 5px;">{week_total:.2f}$</div>'
            else:
                total_pnl_html = f'<div style="color: #94a3b8; font-weight: bold; font-size: 12px; margin-top: 5px;">0.00$</div>'
        
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
    # Añadir columna de emoción si no existe
    try:
        c.execute('''ALTER TABLE trades ADD COLUMN IF NOT EXISTS emotion VARCHAR(50) DEFAULT 'Neutral 😐';''')
    except:
        pass
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
            col_sel, _ = st.columns([1, 2])
            with col_sel:
                account_options = df_accounts.apply(lambda x: f"{x['broker']} - {x['account_name']} (ID:{x['id']})", axis=1).tolist()
                selected_account_str = st.selectbox("CUENTA ACTIVA:", account_options, label_visibility="collapsed")
            
            selected_acc_id = int(selected_account_str.split("ID:")[1].replace(")", ""))
            initial_balance = float(df_accounts[df_accounts['id'] == selected_acc_id]['initial_balance'].values[0])
            df_trades = get_trades(selected_acc_id)

            win_rate, net_profit, wins, losses = 0.0, 0.0, 0, 0
            current_balance = initial_balance
            total_trades = len(df_trades)
            score_win = score_pf = score_awal = score_rec = score_dd = score_cons = 0
            overall_score = 0
            
            if total_trades > 0:
                df_trades['pnl'] = pd.to_numeric(df_trades['pnl'], errors='coerce').fillna(0.0)
                df_trades['date_time'] = pd.to_datetime(df_trades['date_time'])
                
                wins = len(df_trades[df_trades['result'].str.contains("WIN")])
                losses = len(df_trades[df_trades['result'].str.contains("LOSS")])
                ties = len(df_trades[df_trades['result'].str.contains("EMPATE")])
                win_rate = (wins / (total_trades - ties)) * 100 if (total_trades - ties) > 0 else 0.0
                net_profit = float(df_trades['pnl'].sum())
                current_balance = initial_balance + net_profit
                
                score_win = win_rate
                gross_profit = df_trades[df_trades['pnl'] > 0]['pnl'].sum()
                gross_loss = abs(df_trades[df_trades['pnl'] < 0]['pnl'].sum())
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
            # LAYOUT: CALENDARIO, PERFIL Y ESTADO EMOCIONAL
            # ==========================================
            col_cal, col_prof, col_emo = st.columns([2.0, 1.2, 1.2])
            
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
                    margin=dict(l=30, r=30, t=10, b=10), height=200
                )

                st.markdown('<div class="profile-card">', unsafe_allow_html=True)
                st.markdown('<div class="profile-title">Perfil de Trading <span style="float:right; color:#64748b; font-size: 16px; font-weight:normal;">ⓘ</span></div>', unsafe_allow_html=True)
                st.plotly_chart(fig_radar, use_container_width=True, config={'displayModeBar': False})
                st.markdown(f'''
                    <div style="margin-top: -5px;">
                        <div style="display: flex; justify-content: space-between; align-items: flex-end;">
                            <div style="color: #94a3b8; font-size: 13px;">Trading Score</div>
                            <div><span style="color: #00ffa3; font-size: 24px; font-weight: bold;">{overall_score}</span><span style="color: #64748b; font-size: 12px;"> / 100</span></div>
                        </div>
                        <div class="progress-bar-bg"><div class="progress-bar-fill" style="width: {overall_score}%;"></div></div>
                        <div style="display: flex; justify-content: space-between; margin-top: 4px;">
                            <div style="color: #64748b; font-size: 9px; font-weight: bold;">NOVATO</div>
                            <div style="color: #64748b; font-size: 9px; font-weight: bold;">PRO</div>
                        </div>
                    </div>
                </div>
                ''', unsafe_allow_html=True)

            with col_emo:
                # Calcular promedio emocional de los últimos 7 días
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
                <div class="emotion-card">
                    <div>
                        <div class="emotion-header-title">ESTADO EMOCIONAL</div>
                        <div class="emotion-header-sub">BIOMETRÍA & SENTIMIENTO</div>
                        <div class="emotion-brain-icon">🧠</div>
                    </div>
                    <div class="emotion-content">
                        <div class="emotion-emoji">{emoji_res}</div>
                        <div class="emotion-status">{label_res}</div>
                        <div class="emotion-subtext">Promedio 7 días</div>
                    </div>
                    <div>
                ''', unsafe_allow_html=True)
                
                if st.button("Ver detalles >", key="btn_details"):
                    st.info("💡 Consejo: Mantén tus emociones neutrales y evita operar bajo frustración o euforia para proteger tu cuenta.")
                    
                st.markdown('</div></div>', unsafe_allow_html=True)

            # ==========================================
            # REGISTRO DE OPERACIONES
            # ==========================================
            st.markdown("<br>", unsafe_allow_html=True)
            with st.expander("⚡ REGISTRAR NUEVO TRADE", expanded=True):
                with st.form("trade_form", clear_on_submit=True):
                    c1, c2, c3, c4 = st.columns(4)
                    with c1:
                        market = st.selectbox("Mercado", ["Opciones Binarias", "Forex"])
                        asset = st.text_input("Activo (Ej. EURUSD)").upper()
                    with c2:
                        direction = st.selectbox("Dirección", ["CALL / BUY 🟢", "PUT / SELL 🔴"])
                        amount = st.number_input("Inversión / Lote ($)", min_value=0.1, value=10.0, step=1.0)
                    with c3:
                        result = st.selectbox("Resultado", ["WIN 🎉", "LOSS ❌", "EMPATE ➖"])
                        emotion = st.selectbox("Estado Emocional", ["Neutral 😐", "Confiado 😎", "Enfocado 🎯", "Ansioso 😰", "Frustrado 😤", "Eufórico 🤩"])
                    with c4:
                        payout_percent = st.number_input("% Retorno (Binarias)", min_value=1, max_value=100, value=85)
                        date_time = st.date_input("Fecha", datetime.today())
                        time_input = st.time_input("Hora", datetime.now().time())
                    
                    guardar_ejecucion = st.form_submit_button("GUARDAR EJECUCIÓN")
                    
                    if guardar_ejecucion and asset:
                        try:
                            if "WIN" in result:
                                pnl_calc = amount * (payout_percent / 100.0) if market == "Opciones Binarias" else amount
                            elif "LOSS" in result:
                                pnl_calc = -amount
                            else:
                                pnl_calc = 0.0

                            dt_string = f"{date_time} {time_input}"
                            c.execute('''INSERT INTO trades (account_id, date_time, market, asset, direction, amount, result, pnl, emotion) 
                                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)''', 
                                      (selected_acc_id, dt_string, market, asset, direction, amount, result, pnl_calc, emotion))
                            conn.commit()
                            st.success(f"✅ Trade guardado con PnL: {pnl_calc:+.2f}$ y Estado: {emotion}")
                            time.sleep(0.5)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error guardando en la BD: {e}")

            # ==========================================
            # GRÁFICA HISTÓRICA
            # ==========================================
            st.markdown("<br><h3>📈 Histórico de Equidad</h3>", unsafe_allow_html=True)
            if total_trades > 0:
                df_trades['Trade #'] = range(1, len(df_trades) + 1)
                fig = px.area(df_trades, x='Trade #', y='equity', markers=True)
                fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8'), margin=dict(l=0, r=0, t=10, b=0), yaxis=dict(gridcolor='#1e293b', title='Balance ($)'))
                fig.update_traces(line_color='#00d2ff', fillcolor='rgba(0, 210, 255, 0.1)')
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(df_trades.drop(columns=['id', 'account_id', 'equity', 'peak', 'dd']), use_container_width=True, hide_index=True)
