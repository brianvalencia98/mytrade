import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px
from datetime import datetime

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(page_title="Trading Journal Pro", page_icon="📈", layout="wide")

# ==========================================
# SISTEMA DE LOGIN (SEGURIDAD)
# ==========================================
def check_password():
    """Devuelve True si el usuario tiene la contraseña correcta."""
    def password_entered():
        if st.session_state["password"] == st.secrets["APP_PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # No guardar la contraseña
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.title("🔒 Acceso Restringido")
        st.text_input("Ingresa tu contraseña de acceso:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.title("🔒 Acceso Restringido")
        st.text_input("Ingresa tu contraseña de acceso:", type="password", on_change=password_entered, key="password")
        st.error("Contraseña incorrecta. Intenta de nuevo.")
        return False
    return True

if check_password():
    # ==========================================
    # CONEXIÓN A BASE DE DATOS NEON (POSTGRESQL)
    # ==========================================
    @st.cache_resource
    def get_db_connection():
        return psycopg2.connect(st.secrets["DATABASE_URL"])

    conn = get_db_connection()
    conn.autocommit = True
    c = conn.cursor()

    # Crear tablas si no existen (Sintaxis de PostgreSQL)
    c.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id SERIAL PRIMARY KEY,
            broker VARCHAR(100),
            account_name VARCHAR(100),
            initial_balance NUMERIC
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id SERIAL PRIMARY KEY,
            account_id INTEGER REFERENCES accounts(id),
            date_time TIMESTAMP,
            market VARCHAR(50),
            asset VARCHAR(50),
            direction VARCHAR(50),
            amount NUMERIC,
            result VARCHAR(50),
            pnl NUMERIC
        )
    ''')

    # ==========================================
    # FUNCIONES DE BASE DE DATOS
    # ==========================================
    def get_accounts():
        return pd.read_sql_query("SELECT * FROM accounts", conn)

    def get_trades(account_id):
        query = f"SELECT * FROM trades WHERE account_id = {account_id} ORDER BY date_time ASC"
        return pd.read_sql_query(query, conn)

    # ==========================================
    # INTERFAZ DE USUARIO
    # ==========================================
    st.sidebar.title("⚙️ Navegación")
    menu = st.sidebar.radio("Ir a:", ["📊 Dashboard & Registro", "🏦 Gestionar Cuentas"])
    
    st.sidebar.divider()
    st.sidebar.caption("Sesión Segura Activa 🟢")

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
                c.execute("INSERT INTO accounts (broker, account_name, initial_balance) VALUES (%s, %s, %s)", 
                          (broker, acc_name, init_balance))
                st.success(f"Cuenta '{acc_name}' creada con éxito.")
                st.rerun()

        st.divider()
        st.subheader("Tus Cuentas Actuales")
        df_accounts = get_accounts()
        if not df_accounts.empty:
            st.dataframe(df_accounts, use_container_width=True, hide_index=True)

    elif menu == "📊 Dashboard & Registro":
        st.title("📊 Panel de Trading")
        
        df_accounts = get_accounts()
        if df_accounts.empty:
            st.warning("⚠️ Primero crea una cuenta en 'Gestionar Cuentas'.")
        else:
            account_options = df_accounts.apply(lambda x: f"{x['broker']} - {x['account_name']} (ID:{x['id']})", axis=1).tolist()
            selected_account_str = st.selectbox("Selecciona la cuenta:", account_options)
            
            selected_acc_id = int(selected_account_str.split("ID:")[1].replace(")", ""))
            initial_balance = float(df_accounts[df_accounts['id'] == selected_acc_id]['initial_balance'].values[0])
            
            df_trades = get_trades(selected_acc_id)
            
            with st.expander("➕ REGISTRAR NUEVA OPERACIÓN", expanded=True):
                with st.form("trade_form", clear_on_submit=True):
                    c1, c2, c3, c4 = st.columns(4)
                    with c1:
                        market = st.selectbox("Mercado", ["Opciones Binarias", "Forex"])
                        asset = st.text_input("Activo").upper()
                    with c2:
                        direction = st.selectbox("Dirección", ["CALL / COMPRA 🟢", "PUT / VENTA 🔴"])
                        amount = st.number_input("Inversión / Lote ($)", min_value=0.1, value=10.0)
                    with c3:
                        result = st.selectbox("Resultado", ["WIN (Ganada) 🎉", "LOSS (Perdida) ❌", "EMPATE ➖"])
                        pnl = st.number_input("Ganancia/Pérdida Neta ($)", value=0.0)
                    with c4:
                        date_time = st.date_input("Fecha", datetime.today())
                        time_input = st.time_input("Hora", datetime.now().time())
                    
                    submit_trade = st.form_submit_button("Guardar Operación")
                    
                    if submit_trade and asset:
                        dt_string = f"{date_time} {time_input}"
                        c.execute('''INSERT INTO trades (account_id, date_time, market, asset, direction, amount, result, pnl) 
                                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''', 
                                  (selected_acc_id, dt_string, market, asset, direction, amount, result, pnl))
                        st.success("Operación guardada.")
                        st.rerun()

            st.divider()
            if not df_trades.empty:
                # Convertir la columna pnl a numérico
                df_trades['pnl'] = pd.to_numeric(df_trades['pnl'])
                
                total_trades = len(df_trades)
                wins = len(df_trades[df_trades['result'].str.contains("WIN")])
                losses = len(df_trades[df_trades['result'].str.contains("LOSS")])
                ties = len(df_trades[df_trades['result'].str.contains("EMPATE")])
                
                win_rate = (wins / (total_trades - ties)) * 100 if (total_trades - ties) > 0 else 0
                net_profit = df_trades['pnl'].sum()
                current_balance = initial_balance + net_profit
                
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Balance Actual", f"${current_balance:.2f}", f"{net_profit:+.2f} Neto")
                m2.metric("Win Rate", f"{win_rate:.1f}%", f"{wins}W - {losses}L")
                m3.metric("Total Trades", total_trades)
                
                st.subheader("📈 Curva de Crecimiento")
                df_trades['Balance'] = initial_balance + df_trades['pnl'].cumsum()
                df_trades['Trade #'] = range(1, len(df_trades) + 1)
                
                fig = px.line(df_trades, x='Trade #', y='Balance', markers=True, template="plotly_dark")
                fig.update_traces(line_color='#00ff88' if net_profit >= 0 else '#ff4b4b')
                st.plotly_chart(fig, use_container_width=True)
                
                st.dataframe(df_trades.drop(columns=['id', 'account_id']), use_container_width=True, hide_index=True)
