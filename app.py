import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA Y ESTILOS
# ==========================================
st.set_page_config(page_title="Trading Journal Pro", page_icon="📈", layout="wide")

# ==========================================
# CONEXIÓN A BASE DE DATOS SQLITE
# ==========================================
@st.cache_resource
def get_db_connection():
    conn = sqlite3.connect('trading_journal.db', check_same_thread=False)
    return conn

conn = get_db_connection()
c = conn.cursor()

# Crear tablas si no existen
c.execute('''
    CREATE TABLE IF NOT EXISTS accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        broker TEXT,
        account_name TEXT,
        initial_balance REAL
    )
''')
c.execute('''
    CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id INTEGER,
        date_time TIMESTAMP,
        market TEXT,
        asset TEXT,
        direction TEXT,
        amount REAL,
        result TEXT,
        pnl REAL,
        FOREIGN KEY (account_id) REFERENCES accounts(id)
    )
''')
conn.commit()

# ==========================================
# FUNCIONES DE BASE DE DATOS
# ==========================================
def get_accounts():
    return pd.read_sql_query("SELECT * FROM accounts", conn)

def get_trades(account_id):
    query = f"SELECT * FROM trades WHERE account_id = {account_id} ORDER BY date_time ASC"
    return pd.read_sql_query(query, conn)

# ==========================================
# INTERFAZ DE USUARIO (BARRA LATERAL)
# ==========================================
st.sidebar.title("⚙️ Navegación")
menu = st.sidebar.radio("Ir a:", ["📊 Dashboard & Registro", "🏦 Gestionar Cuentas"])

# ==========================================
# SECCIÓN 1: GESTIONAR CUENTAS
# ==========================================
if menu == "🏦 Gestionar Cuentas":
    st.title("🏦 Gestión de Cuentas y Brókers")
    
    with st.form("new_account_form", clear_on_submit=True):
        st.subheader("Añadir Nueva Cuenta")
        col1, col2, col3 = st.columns(3)
        with col1:
            broker = st.text_input("Nombre del Bróker (Ej. Quotex, Exness)")
        with col2:
            acc_name = st.text_input("Nombre de la Cuenta (Ej. Real, Demo)")
        with col3:
            init_balance = st.number_input("Balance Inicial ($)", min_value=0.0, value=100.0, step=10.0)
            
        submit_acc = st.form_submit_button("Crear Cuenta")
        
        if submit_acc and broker and acc_name:
            c.execute("INSERT INTO accounts (broker, account_name, initial_balance) VALUES (?, ?, ?)", 
                      (broker, acc_name, init_balance))
            conn.commit()
            st.success(f"Cuenta '{acc_name}' en {broker} creada con éxito.")
            st.rerun()

    st.divider()
    st.subheader("Tus Cuentas Actuales")
    df_accounts = get_accounts()
    if not df_accounts.empty:
        st.dataframe(df_accounts, use_container_width=True, hide_index=True)
    else:
        st.info("No tienes cuentas registradas. Crea una arriba para empezar.")

# ==========================================
# SECCIÓN 2: DASHBOARD Y REGISTRO
# ==========================================
elif menu == "📊 Dashboard & Registro":
    st.title("📊 Panel de Trading")
    
    df_accounts = get_accounts()
    if df_accounts.empty:
        st.warning("⚠️ Primero debes crear una cuenta en 'Gestionar Cuentas' para poder registrar operaciones.")
    else:
        # Selector de Cuenta
        account_options = df_accounts.apply(lambda x: f"{x['broker']} - {x['account_name']} (ID:{x['id']})", axis=1).tolist()
        selected_account_str = st.selectbox("Selecciona la cuenta a visualizar/operar:", account_options)
        
        # Extraer el ID de la cuenta seleccionada
        selected_acc_id = int(selected_account_str.split("ID:")[1].replace(")", ""))
        initial_balance = df_accounts[df_accounts['id'] == selected_acc_id]['initial_balance'].values[0]
        
        # Cargar operaciones de esta cuenta
        df_trades = get_trades(selected_acc_id)
        
        # ==========================================
        # FORMULARIO DE REGISTRO RÁPIDO
        # ==========================================
        with st.expander("➕ REGISTRAR NUEVA OPERACIÓN", expanded=True):
            with st.form("trade_form", clear_on_submit=True):
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    market = st.selectbox("Mercado", ["Opciones Binarias", "Forex"])
                    asset = st.text_input("Activo (Ej. EUR/USD)").upper()
                with c2:
                    direction = st.selectbox("Dirección", ["CALL / COMPRA 🟢", "PUT / VENTA 🔴"])
                    amount = st.number_input("Inversión / Lote ($)", min_value=0.1, value=10.0)
                with c3:
                    result = st.selectbox("Resultado", ["WIN (Ganada) 🎉", "LOSS (Perdida) ❌", "EMPATE (Break-even) ➖"])
                    pnl = st.number_input("Ganancia/Pérdida Neta ($)", value=0.0, help="Usa negativo para pérdidas (Ej. -10)")
                with c4:
                    date_time = st.date_input("Fecha", datetime.today())
                    time_input = st.time_input("Hora", datetime.now().time())
                
                submit_trade = st.form_submit_button("Guardar Operación")
                
                if submit_trade and asset:
                    dt_string = f"{date_time} {time_input}"
                    c.execute('''INSERT INTO trades (account_id, date_time, market, asset, direction, amount, result, pnl) 
                                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
                              (selected_acc_id, dt_string, market, asset, direction, amount, result, pnl))
                    conn.commit()
                    st.success("Operación registrada correctamente.")
                    st.rerun()

        # ==========================================
        # CÁLCULO DE MÉTRICAS (KPIs)
        # ==========================================
        st.divider()
        if not df_trades.empty:
            total_trades = len(df_trades)
            wins = len(df_trades[df_trades['result'].str.contains("WIN")])
            losses = len(df_trades[df_trades['result'].str.contains("LOSS")])
            ties = len(df_trades[df_trades['result'].str.contains("EMPATE")])
            
            win_rate = (wins / (total_trades - ties)) * 100 if (total_trades - ties) > 0 else 0
            net_profit = df_trades['pnl'].sum()
            current_balance = initial_balance + net_profit
            
            # Gross profit / Gross loss para Profit Factor
            gross_profit = df_trades[df_trades['pnl'] > 0]['pnl'].sum()
            gross_loss = abs(df_trades[df_trades['pnl'] < 0]['pnl'].sum())
            profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else float('inf')

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Balance Actual", f"${current_balance:.2f}", f"{net_profit:+.2f} Beneficio Neto")
            m2.metric("Win Rate", f"{win_rate:.1f}%", f"{wins}W - {losses}L")
            m3.metric("Operaciones Totales", total_trades)
            m4.metric("Profit Factor", f"{profit_factor:.2f}")

            # ==========================================
            # GRÁFICOS INTERACTIVOS (PLOTLY)
            # ==========================================
            st.subheader("📈 Curva de Crecimiento (Equity Curve)")
            
            # Preparamos los datos para la curva sumando el balance acumulado
            df_trades['Balance Acumulado'] = initial_balance + df_trades['pnl'].cumsum()
            df_trades['Operación #'] = range(1, len(df_trades) + 1)
            
            fig_equity = px.line(df_trades, x='Operación #', y='Balance Acumulado', markers=True,
                                 title="Evolución del Capital", template="plotly_dark")
            fig_equity.update_traces(line_color='#00ff88' if net_profit >= 0 else '#ff4b4b')
            st.plotly_chart(fig_equity, use_container_width=True)
            
            # Tabla histórico
            st.subheader("📜 Historial de Operaciones")
            st.dataframe(df_trades.drop(columns=['id', 'account_id']), use_container_width=True, hide_index=True)
            
        else:
            st.info("Aún no hay operaciones registradas en esta cuenta. Añade tu primer trade arriba.")