import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, timezone
import calendar
import time

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(page_title="MYTRADES", page_icon="⚡", layout="wide")

# ==========================================
# BLOQUES DE CSS (LOGIN Y DASHBOARD RESPONSIVOS)
# ==========================================
CSS_LOGIN = """
<style>
    header, [data-testid="stHeader"], [data-testid="collapsedControl"] { display: none !important; }

    @keyframes pulse-glow {
        0% { box-shadow: 0 0 15px rgba(0, 210, 255, 0.15), 0 15px 50px rgba(0,0,0,0.8); }
        50% { box-shadow: 0 0 35px rgba(0, 210, 255, 0.35), 0 15px 50px rgba(0,0,0,0.8); }
        100% { box-shadow: 0 0 15px rgba(0, 210, 255, 0.15), 0 15px 50px rgba(0,0,0,0.8); }
    }

    @keyframes float-title {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-3px); }
        100% { transform: translateY(0px); }
    }

    [data-testid="stAppViewContainer"] { 
        background: radial-gradient(circle at center, #0b162c 0%, #050a14 100%) !important; 
        color: #e2e8f0 !important; 
    }

    [data-testid="block-container"] {
        background: linear-gradient(145deg, #070d19, #0b1325) !important;
        border: 1.5px solid rgba(0, 210, 255, 0.35) !important;
        border-radius: 24px !important;
        padding: 35px 20px !important;
        box-shadow: 0 15px 50px rgba(0,0,0,0.8) !important;
        animation: pulse-glow 5s ease-in-out infinite !important;
        max-width: 320px !important;
        margin: 12vh auto 0 auto !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
    }

    .login-status-capsule {
        width: 190px; height: 36px; border-radius: 10px;
        border: 1.5px solid rgba(0, 210, 255, 0.4);
        display: flex; align-items: center; justify-content: center;
        font-weight: 800; font-size: 11px; letter-spacing: 2px;
        text-transform: uppercase; margin: 0 auto 14px auto;
        transition: all 0.3s ease; background: rgba(11, 19, 37, 0.6);
    }

    .login-title {
        color: #00d2ff; font-size: 18px; font-weight: 900; letter-spacing: 2px;
        text-align: center; text-transform: uppercase;
        text-shadow: 0 0 12px rgba(0, 210, 255, 0.5); margin-bottom: 3px;
        animation: float-title 4s ease-in-out infinite;
    }

    .login-subtitle {
        color: #64748b; font-size: 8.5px; font-weight: 700; letter-spacing: 1px;
        text-align: center; text-transform: uppercase; margin-bottom: 16px;
    }

    .pin-display { display: flex; justify-content: center; gap: 12px; margin-bottom: 18px; }
    
    .pin-dot {
        width: 11px; height: 11px; border-radius: 50%; border: 2px solid #00d2ff;
        background-color: transparent; transition: all 0.3s ease; box-shadow: 0 0 5px rgba(0, 210, 255, 0.3);
    }
    
    .pin-dot.active {
        background-color: #00ffa3; border-color: #00ffa3;
        box-shadow: 0 0 12px #00ffa3, 0 0 20px rgba(0, 255, 163, 0.6); transform: scale(1.15);
    }

    div[data-testid="stHorizontalBlock"] { justify-content: center !important; gap: 8px !important; margin-bottom: 4px !important; }
    div[data-testid="stColumn"] { flex: 0 0 50px !important; min-width: 50px !important; max-width: 50px !important; display: flex !important; justify-content: center !important; }
    
    div[data-testid="stColumn"] button {
        width: 50px !important; height: 50px !important; border-radius: 50% !important;
        background: linear-gradient(145deg, #0b1325, #050a14) !important;
        border: 1.5px solid rgba(0, 210, 255, 0.3) !important;
        color: #00d2ff !important; font-size: 16px !important; font-weight: 800 !important;
        transition: all 0.2s ease !important; box-shadow: 0 4px 12px rgba(0,0,0,0.5) !important;
        display: flex !important; align-items: center !important; justify-content: center !important;
        padding: 0 !important; margin: 0 !important;
    }
    
    div[data-testid="stColumn"] button:hover {
        border-color: #00ffa3 !important; color: #00ffa3 !important;
        background: rgba(0, 255, 163, 0.12) !important;
        box-shadow: 0 0 18px rgba(0, 255, 163, 0.4) !important; transform: translateY(-2px) scale(1.04);
    }
</style>
"""

CSS_DASHBOARD = """
<style>
    @keyframes float-icon {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-4px); }
        100% { transform: translateY(0px); }
    }

    [data-testid="stAppViewContainer"] { background-color: #070d19; color: #e2e8f0; }
    
    [data-testid="block-container"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        animation: none !important;
        max-width: none !important;
        padding: 4rem 1rem 10rem !important;
        margin: auto !important;
        display: block !important;
    }
    
    [data-testid="stSidebar"] { 
        background: linear-gradient(180deg, #030712 0%, #070d1d 50%, #0b1329 100%) !important; 
        border-right: 1px solid rgba(0, 210, 255, 0.25); 
        box-shadow: 10px 0 35px rgba(0, 0, 0, 0.85); 
    }
    [data-testid="stHeader"] { background-color: transparent; }
    
    .sidebar-title { 
        color: #00d2ff; 
        font-size: 21px; 
        font-weight: 900; 
        letter-spacing: 2.5px; 
        text-transform: uppercase; 
        text-shadow: 0 0 15px rgba(0, 210, 255, 0.6); 
        margin-bottom: 25px; 
        display: flex; 
        align-items: center; 
        gap: 10px; 
        animation: float-icon 4s ease-in-out infinite;
    }

    [data-testid="stSidebar"] .stRadio > label { 
        color: #94a3b8 !important; 
        font-weight: 700 !important; 
        letter-spacing: 1.2px; 
        font-size: 11px;
    }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] { gap: 12px; }
    
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label { 
        background: linear-gradient(135deg, rgba(11, 19, 37, 0.8) 0%, rgba(5, 11, 25, 0.95) 100%) !important; 
        border: 1px solid rgba(30, 41, 59, 0.9) !important; 
        border-radius: 14px !important; 
        padding: 14px 18px !important; 
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1) !important; 
    }
    
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover { 
        border-color: #00d2ff !important; 
        background: linear-gradient(135deg, rgba(0, 210, 255, 0.15) 0%, rgba(11, 19, 37, 0.95) 100%) !important; 
        box-shadow: 0 0 22px rgba(0, 210, 255, 0.35) !important; 
        transform: translateX(6px) scale(1.02); 
    }

    [data-testid="stSidebar"] .stButton button { 
        background: linear-gradient(135deg, #ff3366, #991b33) !important; 
        color: #ffffff !important; 
        border: 1px solid #ff3366 !important; 
        border-radius: 14px !important; 
        font-weight: 900 !important; 
        letter-spacing: 1.5px; 
        width: 100% !important; 
        box-shadow: 0 4px 20px rgba(255, 51, 102, 0.4) !important; 
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important; 
    }

    .kpi-card-exact {
        background: linear-gradient(145deg, #070d19, #0b1325);
        border-radius: 16px;
        padding: 16px 20px;
        border: 1px solid #1e293b;
        box-shadow: 0 8px 25px rgba(0,0,0,0.4);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 115px;
    }

    /* Tarjetas simétricas de Gestión de Riesgo */
    .risk-kpi-card {
        background: linear-gradient(145deg, #091224, #050b16);
        border-radius: 14px;
        padding: 12px 14px;
        border: 1px solid #1e293b;
        box-shadow: 0 4px 18px rgba(0,0,0,0.35);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 100px;
        box-sizing: border-box;
        transition: all 0.25s ease;
    }
    .risk-kpi-card:hover {
        border-color: rgba(0, 210, 255, 0.45);
        box-shadow: 0 4px 22px rgba(0, 210, 255, 0.15);
        transform: translateY(-2px);
    }

    /* Botones de navegación de mes del calendario */
    div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stButton"] > button {
        background: linear-gradient(135deg, #0b162c, #060d1b) !important;
        border: 1.5px solid rgba(0, 210, 255, 0.35) !important;
        color: #00d2ff !important;
        border-radius: 10px !important;
        font-size: 13px !important;
        font-weight: 800 !important;
        height: 32px !important;
        min-height: 32px !important;
        width: 100% !important;
        padding: 0 !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stButton"] > button:hover {
        border-color: #00ffa3 !important;
        color: #00ffa3 !important;
        box-shadow: 0 0 12px rgba(0, 255, 163, 0.3) !important;
        transform: scale(1.05);
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(145deg, #070d19, #0b1325) !important;
        border: 1px solid #1e293b !important;
        border-radius: 18px !important;
        box-shadow: 0 8px 32px rgba(0,0,0,0.45) !important;
        padding: 16px 18px 20px 18px !important;
        margin-bottom: 12px !important;
        transition: border-color 0.3s ease, box-shadow 0.3s ease !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: rgba(0, 210, 255, 0.35) !important;
        box-shadow: 0 10px 35px rgba(0, 210, 255, 0.1) !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        border: none !important;
        background: transparent !important;
        padding: 0 !important;
    }

    .progress-bar-bg { height: 6px; background-color: #1e293b; border-radius: 3px; margin-top: 8px; position: relative; }
    .progress-bar-fill { height: 100%; background: linear-gradient(90deg, #ff3366, #ffb800, #00ffa3); border-radius: 3px; position: absolute; left: 0; top: 0; box-shadow: 0 0 8px rgba(0, 255, 163, 0.4); }

    .best-worst-card { 
        background: rgba(11, 19, 37, 0.85); 
        border-radius: 14px; 
        padding: 10px 14px; 
        border: 1px solid #1e293b; 
        margin-top: 6px;
        margin-bottom: 6px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .best-worst-card:hover { transform: translateY(-2px); }
    .best-card { border-left: 4px solid #00ffa3 !important; box-shadow: 0 4px 15px rgba(0, 255, 163, 0.08); }
    .worst-card { border-left: 4px solid #ff3366 !important; box-shadow: 0 4px 15px rgba(255, 51, 102, 0.08); }

    .status-panel-card {
        background: linear-gradient(145deg, #070d19, #0b1325);
        border: 1px solid #1e293b;
        border-radius: 16px;
        padding: 14px 16px;
        height: 168px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: 0 8px 25px rgba(0,0,0,0.35);
        transition: all 0.28s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .status-panel-card:hover {
        border-color: rgba(0, 210, 255, 0.45);
        box-shadow: 0 8px 30px rgba(0, 210, 255, 0.12);
        transform: translateY(-2px);
    }
    .status-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #1e293b;
        padding-bottom: 8px;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 1.2px;
        color: #94a3b8;
        text-transform: uppercase;
    }
    .status-body-center {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        flex-grow: 1;
        padding: 4px 0;
    }
    .session-item-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 5px 10px;
        border-radius: 8px;
        margin-bottom: 4px;
        border: 1px solid #1e293b;
        background: rgba(11, 19, 37, 0.6);
        transition: all 0.2s ease;
    }
    .session-item-row.active {
        border-color: rgba(0, 255, 163, 0.5);
        background: rgba(0, 255, 163, 0.08);
        box-shadow: 0 0 10px rgba(0, 255, 163, 0.15);
    }
    .dot-live { height: 8px; width: 8px; background-color: #00ffa3; border-radius: 50%; display: inline-block; box-shadow: 0 0 8px #00ffa3; }
    .dot-closed { height: 8px; width: 8px; background-color: #64748b; border-radius: 50%; display: inline-block; }

    div[data-baseweb="input"],
    div[data-baseweb="base-input"],
    div[data-baseweb="select"],
    div[data-baseweb="select"] > div,
    div[data-testid="stTextInput"] > div > div,
    div[data-testid="stNumberInput"] > div > div,
    div[data-testid="stDateInput"] > div > div,
    div[data-testid="stTimeInput"] > div > div,
    div[data-testid="stSelectbox"] > div > div {
        background: linear-gradient(135deg, #0b162c 0%, #060d1b 100%) !important;
        background-color: #081120 !important;
        border: 1.5px solid rgba(0, 210, 255, 0.35) !important;
        border-radius: 12px !important;
        box-shadow: inset 0 2px 6px rgba(0, 0, 0, 0.6) !important;
        transition: all 0.3s ease !important;
    }

    div[data-baseweb="input"] *,
    div[data-baseweb="base-input"] *,
    div[data-baseweb="select"] * { background-color: transparent !important; }

    div[data-baseweb="base-input"]:focus-within,
    div[data-baseweb="select"] > div:hover,
    div[data-baseweb="select"] > div:focus-within,
    div[data-testid="stTextInput"] > div > div:focus-within,
    div[data-testid="stNumberInput"] > div > div:focus-within,
    div[data-testid="stDateInput"] > div > div:focus-within,
    div[data-testid="stTimeInput"] > div > div:focus-within,
    div[data-testid="stSelectbox"] > div > div:focus-within {
        border-color: #00d2ff !important;
        box-shadow: 0 0 16px rgba(0, 210, 255, 0.4), inset 0 2px 6px rgba(0, 0, 0, 0.6) !important;
    }

    input {
        color: #00d2ff !important;
        font-weight: 800 !important;
        font-size: 14px !important;
        letter-spacing: 0.5px !important;
        background-color: transparent !important;
    }
    input::placeholder { color: #475569 !important; }
    div[data-baseweb="select"] span,
    div[data-baseweb="select"] div {
        color: #00d2ff !important;
        font-weight: 800 !important;
        font-size: 13.5px !important;
        letter-spacing: 0.5px !important;
        text-shadow: 0 0 8px rgba(0, 210, 255, 0.25) !important;
    }
    div[data-baseweb="select"] input { caret-color: transparent !important; cursor: pointer !important; }
    svg { fill: #00d2ff !important; }

    [data-testid="stNumberInputContainer"] button { background-color: transparent !important; color: #00d2ff !border: none !important; }
    [data-testid="stNumberInputContainer"] button:hover { color: #00ffa3 !important; background-color: rgba(0, 255, 163, 0.15) !important; border-radius: 8px; }

    div[data-baseweb="popover"], div[data-baseweb="popover"] > div { background-color: transparent !important; }
    ul[data-baseweb="menu"], div[role="listbox"] {
        background: linear-gradient(160deg, #0a1428 0%, #050a14 100%) !important;
        border: 1.5px solid rgba(0, 210, 255, 0.4) !important;
        border-radius: 12px !important;
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.9) !important;
        padding: 6px !important;
    }
    li[role="option"] {
        background: transparent !important;
        color: #cbd5e1 !important;
        font-weight: 700 !important;
        font-size: 13.5px !important;
        border-radius: 8px !important;
        margin-bottom: 2px !important;
        padding: 10px 14px !important;
        transition: all 0.2s ease !important;
    }
    li[role="option"]:hover, li[aria-selected="true"], li[aria-selected="true"]:hover {
        background: rgba(0, 210, 255, 0.15) !important;
        color: #00ffa3 !important;
        border-left: 3px solid #00ffa3 !important;
        transform: translateX(3px);
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

    .quantum-table-wrapper {
        background: linear-gradient(145deg, #070d19, #0b1325);
        border: 1px solid #1e293b;
        border-radius: 16px;
        overflow-x: auto;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.45);
        margin-bottom: 18px;
    }
    .quantum-table { width: 100%; border-collapse: separate; border-spacing: 0; color: #cbd5e1; font-size: 13.5px; }
    .quantum-table th { background: rgba(11, 19, 37, 0.95); color: #00d2ff; font-size: 11px; font-weight: 800; letter-spacing: 1.5px; text-transform: uppercase; padding: 14px 16px; border-bottom: 1px solid #1e293b; white-space: nowrap; }
    .quantum-table td { padding: 13px 16px; border-bottom: 1px solid rgba(30, 41, 59, 0.45); white-space: nowrap; vertical-align: middle; }
    .quantum-table tbody tr { transition: all 0.22s ease-in-out; }
    .quantum-table tbody tr:hover { background: rgba(0, 210, 255, 0.06); }
    .quantum-table tbody tr:last-child td { border-bottom: none; }
    .badge-win { background: rgba(0, 255, 163, 0.12); color: #00ffa3; border: 1px solid rgba(0, 255, 163, 0.35); padding: 4px 10px; border-radius: 8px; font-weight: 800; font-size: 11px; display: inline-block; }
    .badge-loss { background: rgba(255, 51, 102, 0.12); color: #ff3366; border: 1px solid rgba(255, 51, 102, 0.35); padding: 4px 10px; border-radius: 8px; font-weight: 800; font-size: 11px; display: inline-block; }
    .badge-tie { background: rgba(148, 163, 184, 0.12); color: #94a3b8; border: 1px solid rgba(148, 163, 184, 0.35); padding: 4px 10px; border-radius: 8px; font-weight: 800; font-size: 11px; display: inline-block; }
    .badge-call { background: rgba(0, 255, 163, 0.08); color: #00ffa3; border: 1px solid rgba(0, 255, 163, 0.3); padding: 4px 8px; border-radius: 6px; font-weight: 700; font-size: 11.5px; }
    .badge-put { background: rgba(255, 51, 102, 0.08); color: #ff3366; border: 1px solid rgba(255, 51, 102, 0.3); padding: 4px 8px; border-radius: 6px; font-weight: 700; font-size: 11.5px; }

    .trade-quantum-card {
        background: linear-gradient(135deg, rgba(11, 19, 37, 0.95) 0%, rgba(7, 13, 25, 0.98) 100%);
        border: 1px solid #1e293b;
        border-radius: 14px;
        padding: 14px 20px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.35);
    }
    .trade-quantum-card:hover { transform: translateY(-2px); border-color: #00d2ff; box-shadow: 0 6px 20px rgba(0, 210, 255, 0.2); }
    .trade-badge { background: rgba(15, 23, 42, 0.85); border: 1px solid #1e293b; padding: 4px 10px; border-radius: 8px; font-size: 13px; color: #94a3b8; display: inline-flex; align-items: center; gap: 5px; }

    [data-testid="stExpander"] {
        background: linear-gradient(145deg, #070d19, #0b1325) !important;
        border: 1px solid #00d2ff !important;
        border-radius: 16px !important;
        box-shadow: 0 8px 32px rgba(0,0,0,0.4), 0 0 15px rgba(0, 210, 255, 0.1) !important;
    }
    [data-testid="stExpander"] summary {
        background: linear-gradient(135deg, #0b1325, #111a2e) !important;
        border-radius: 12px !important;
        color: #00d2ff !important;
        font-weight: bold !important;
        border: 1px solid #1e293b !important;
    }

    /* ==========================================
       OVERRIDE STREAMLIT: BOTÓN ACTIVO -> AZUL NEÓN
       ========================================== */
    button[kind="primary"], button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #00d2ff 0%, #0072ff 100%) !important;
        background-color: #00d2ff !important;
        border: 1px solid #00d2ff !important;
        box-shadow: 0 0 18px rgba(0, 210, 255, 0.6), 0 4px 15px rgba(0, 210, 255, 0.3) !important;
        border-radius: 14px !important;
        color: #ffffff !important;
        transition: all 0.3s ease !important;
        min-height: 46px !important;
    }
    button[kind="primary"]:hover, button[data-testid="baseButton-primary"]:hover {
        background: linear-gradient(135deg, #00ffa3 0%, #00d284 100%) !important;
        border-color: #00ffa3 !important;
        box-shadow: 0 0 25px rgba(0, 255, 163, 0.6) !important;
        transform: translateY(-2px) scale(1.02) !important;
        color: #050a14 !important;
    }
    button[kind="primary"] p, button[data-testid="baseButton-primary"] p {
        color: inherit !important;
        font-weight: 900 !important;
        letter-spacing: 0.8px !important;
        text-shadow: none !important;
        margin: 0 !important;
    }

    button[kind="secondary"], button[data-testid="baseButton-secondary"] {
        border-radius: 14px !important;
        transition: all 0.3s ease !important;
        min-height: 46px !important;
        background: #111a2e !important;
        background-color: #111a2e !important;
        border: 1.5px solid #233148 !important;
        box-shadow: inset 0 2px 8px rgba(0,0,0,0.4) !important;
    }
    button[kind="secondary"] p, button[data-testid="baseButton-secondary"] p {
        color: #64748b !important;
        font-weight: 700 !important;
        margin: 0 !important;
    }
    button[kind="secondary"]:hover, button[data-testid="baseButton-secondary"]:hover {
        border-color: #00d2ff !important;
        color: #00d2ff !important;
        box-shadow: 0 0 15px rgba(0, 210, 255, 0.25) !important;
        transform: translateY(-1px) !important;
    }
    button[kind="secondary"]:hover p, button[data-testid="baseButton-secondary"]:hover p {
        color: #00d2ff !important;
    }
    
    .pin-display ~ div[data-testid="stHorizontalBlock"] button {
        min-height: 50px !important;
    }

    /* ==========================================
       TABLA DE CALENDARIO NUMÉRICO
       ========================================== */
    .cal-wrapper { width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch; padding-top: 6px; }
    .cal-table { width: 100%; border-collapse: collapse; table-layout: fixed; min-width: 330px; }
    .cal-th { color: #00d2ff; padding: 8px 0; text-align: center; border-bottom: 1px solid #1e293b; font-weight: 800; font-size: 12px; letter-spacing: 0.5px; }
    .cal-td-empty { border: 1px solid #10192d; height: 64px; background-color: #060b16; }
    .cal-cell { border: 1px solid #10192d; height: 64px; vertical-align: top; padding: 6px 5px; background-color: #080f1e; position: relative; }
    .cal-cell-win { border: 1px solid #00d284 !important; border-bottom: 3.5px solid #00ffa3 !important; background-color: rgba(0, 255, 163, 0.08) !important; }
    .cal-cell-loss { border: 1px solid #d22d56 !important; border-bottom: 3.5px solid #ff3366 !important; background-color: rgba(255, 51, 102, 0.08) !important; }
    .cal-day-num { font-size: 11.5px; color: #cbd5e1; font-weight: 700; line-height: 1; }
    .cal-pnl { font-weight: 800; font-size: 10px; position: absolute; bottom: 5px; right: 4px; line-height: 1.1; text-align: right; }
    .cal-win { color: #00ffa3; text-shadow: 0 0 6px rgba(0, 255, 163, 0.4); }
    .cal-loss { color: #ff3366; text-shadow: 0 0 6px rgba(255, 51, 102, 0.4); }
    .cal-tie { color: #94a3b8; }
    .cal-tot-cell { border: 1px solid #10192d; height: 64px; vertical-align: middle; text-align: center; background-color: #060b16; padding: 4px 2px; }

    /* ==========================================
       ESTILOS PARA EL TRADING HEATMAP DINÁMICO
       ========================================== */
    .hm-card {
        background: linear-gradient(165deg, #0b1120 0%, #060a14 100%);
        border: 1.5px solid #1e293b;
        border-radius: 24px;
        padding: 22px 20px 18px 20px;
        box-shadow: 0 10px 35px rgba(0, 0, 0, 0.55);
        margin-bottom: 12px;
        min-height: 380px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    .hm-weekdays {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 8px;
        margin-bottom: 10px;
        text-align: center;
    }
    .hm-weekday {
        color: #94a3b8;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    .hm-grid {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 8px;
        margin-bottom: 20px;
    }
    .hm-cell {
        height: 48px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 13.5px;
        font-weight: 800;
        cursor: pointer;
        transition: all 0.2s ease;
        position: relative;
    }
    .hm-cell:hover {
        transform: translateY(-2px) scale(1.06);
        z-index: 3;
    }
    .hm-empty {
        height: 48px;
    }
    
    .hm-week-grid {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 12px;
        margin-bottom: 22px;
    }
    .hm-week-cell {
        height: 64px;
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
        font-weight: 800;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    .hm-week-cell:hover {
        transform: translateY(-2px) scale(1.05);
    }
    .hm-week-empty {
        height: 64px;
    }

    .hm-year-container {
        display: flex;
        flex-direction: column;
        gap: 10px;
        max-height: 250px;
        overflow-y: auto;
        padding-right: 6px;
        margin-bottom: 14px;
    }
    .hm-year-container::-webkit-scrollbar { width: 5px; }
    .hm-year-container::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 4px; }
    .hm-year-month-row {
        display: flex;
        flex-direction: column;
        gap: 4px;
    }
    .hm-year-month-label {
        color: #cbd5e1;
        font-size: 11.5px;
        font-weight: 800;
        letter-spacing: 0.5px;
    }
    .hm-year-mini-grid {
        display: grid;
        grid-template-columns: repeat(16, 1fr);
        gap: 4.5px;
        max-width: 100%;
    }
    .hm-mini-box {
        height: 13px;
        border-radius: 3px;
        transition: transform 0.15s ease;
        cursor: pointer;
    }
    .hm-mini-box:hover {
        transform: scale(1.35);
        z-index: 2;
    }

    .hm-no-data-box {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 200px;
        color: #94a3b8;
        font-size: 17px;
        font-weight: 600;
        letter-spacing: 0.5px;
    }

    .hm-cell-today {
        border: 2.5px solid #8b5cf6 !important;
        box-shadow: 0 0 16px rgba(139, 92, 246, 0.75) !important;
    }

    .hm-legend {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        align-items: center;
        gap: 12px 18px;
        padding-top: 14px;
        border-top: 1px solid rgba(30, 41, 59, 0.6);
    }
    .hm-leg-item {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        color: #94a3b8;
        font-size: 11px;
        font-weight: 700;
    }
    .hm-dot {
        width: 12px;
        height: 12px;
        border-radius: 4px;
        display: inline-block;
    }

    /* ==========================================
       ADAPTACIÓN MÓVIL (PANTALLAS <= 768px)
       ========================================== */
    @media (max-width: 768px) {
        .cal-wrapper { margin: 0 -4px; padding: 2px 4px; }
        .cal-cell, .cal-td-empty, .cal-tot-cell { height: 48px !important; padding: 3px 2px !important; }
        .cal-th { padding: 5px 0 !important; font-size: 10px !important; }
        .cal-day-num { font-size: 9.5px !important; }
        .cal-pnl { font-size: 8px !important; bottom: 2px !important; right: 2px !important; }
        .cal-sym { display: none !important; }

        .hm-card { padding: 16px 12px; min-height: auto !important; }
        .hm-grid, .hm-weekdays { gap: 4px !important; }
        .hm-cell, .hm-empty { height: 38px !important; font-size: 11px !important; border-radius: 8px !important; }
        .hm-weekday { font-size: 10px !important; }
        
        .hm-week-grid { gap: 6px !important; }
        .hm-week-cell, .hm-week-empty { height: 48px !important; font-size: 12px !important; border-radius: 10px !important; }
        
        .hm-year-mini-grid { gap: 3px !important; }
        .hm-mini-box { height: 11px !important; border-radius: 2px !important; }

        .hm-legend { gap: 8px 12px !important; font-size: 10px !important; }

        .kpi-card-exact { height: auto !important; min-height: 90px !important; padding: 12px 14px !important; margin-bottom: 8px !important; }
        .kpi-card-exact div[style*="font-size: 26px"] { font-size: 20px !important; }

        .trade-quantum-card { flex-direction: column !important; align-items: flex-start !important; gap: 10px !important; }
        .trade-quantum-card > div:last-child { width: 100% !important; text-align: left !important; margin-left: 0 !important; border-top: 1px solid rgba(30, 41, 59, 0.4); padding-top: 6px; }
    }
</style>
"""

# ==========================================
# FUNCIONES AUXILIARES DE MONEDA
# ==========================================
def get_currency_symbol(curr_str):
    if not curr_str:
        return "$"
    if "COP" in curr_str:
        return "COL$"
    elif "EUR" in curr_str:
        return "€"
    elif "MXN" in curr_str:
        return "MXN$"
    elif "USD" in curr_str:
        return "$"
    if "(" in curr_str and ")" in curr_str:
        inside = curr_str.split("(")[1].split(")")[0].strip()
        return inside
    return "$"

# ==========================================
# GENERADOR DEL CALENDARIO NUMÉRICO
# ==========================================
def render_calendar(df_trades, curr_symbol, year, month):
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
    
    html = f"""<div class="cal-wrapper">
<table class="cal-table">
<tr>
<th class="cal-th">L</th>
<th class="cal-th">M</th>
<th class="cal-th">M</th>
<th class="cal-th">J</th>
<th class="cal-th">V</th>
<th class="cal-th">S</th>
<th class="cal-th">D</th>
<th class="cal-th" style="color:#64748b;">∑</th>
</tr>"""
    for week in cal:
        html += "<tr>"
        week_total = 0.0
        has_trades = False
        
        for day in week:
            if day == 0:
                html += '<td class="cal-td-empty"></td>'
            else:
                pnl = daily_pnl.get(day, None)
                cell_class = "cal-cell"
                pnl_html = ""
                
                if pnl is not None:
                    has_trades = True
                    week_total += pnl
                    
                    pnl_fmt = f"{pnl:+,.0f}" if ("COP" in curr_symbol or "COL$" in curr_symbol) else f"{pnl:+,.2f}"
                    
                    if pnl > 0:
                        cell_class = "cal-cell cal-cell-win"
                        pnl_html = f'<div class="cal-pnl cal-win">{pnl_fmt}<span class="cal-sym"> {curr_symbol}</span></div>'
                    elif pnl < 0:
                        cell_class = "cal-cell cal-cell-loss"
                        pnl_html = f'<div class="cal-pnl cal-loss">{pnl_fmt}<span class="cal-sym"> {curr_symbol}</span></div>'
                    else:
                        pnl_html = f'<div class="cal-pnl cal-tie">0.00</div>'
                
                html += f'<td class="{cell_class}"><div class="cal-day-num">{day}</div>{pnl_html}</td>'
        
        total_style = "border: 1px solid #10192d; background-color: #060b16;"
        total_pnl_html = ""
        
        if has_trades:
            tot_fmt = f"{week_total:+,.0f}" if ("COP" in curr_symbol or "COL$" in curr_symbol) else f"{week_total:+,.2f}"
            if week_total > 0:
                total_style = "border: 1px solid #00d284; background-color: rgba(0, 255, 163, 0.07);"
                total_pnl_html = f'<div style="color: #00ffa3; font-weight: bold; font-size: 10.5px; margin-top: 2px;">{tot_fmt}<span class="cal-sym"> {curr_symbol}</span></div>'
            elif week_total < 0:
                total_style = "border: 1px solid #d22d56; background-color: rgba(255, 51, 102, 0.07);"
                total_pnl_html = f'<div style="color: #ff3366; font-weight: bold; font-size: 10.5px; margin-top: 2px;">{tot_fmt}<span class="cal-sym"> {curr_symbol}</span></div>'
            else:
                total_pnl_html = f'<div style="color: #94a3b8; font-weight: bold; font-size: 10px; margin-top: 2px;">0.00</div>'
        
        html += f'<td class="cal-tot-cell" style="{total_style}"><div style="font-size: 8px; color: #64748b; font-weight: bold; letter-spacing: 0.5px;">TOTAL</div>{total_pnl_html}</td>'
        html += "</tr>"
        
    html += "</table></div>"
    return html

# ==========================================
# GENERADOR DEL TRADING HEATMAP CON TEMPORALIDADES EXACTAS
# ==========================================
def render_trading_heatmap(df_trades, curr_symbol, time_filter, initial_balance):
    now = datetime.now()
    year = now.year
    month = now.month
    today_day = now.day
    today_weekday = now.weekday()
    
    daily_pnl_by_date = {}
    
    threshold = 50000.0 if ("COP" in curr_symbol or "COL$" in curr_symbol) else 25.0
    if initial_balance > 0:
        threshold = max(initial_balance * 0.02, threshold)

    if not df_trades.empty:
        df_copy = df_trades.copy()
        df_copy['date_time'] = pd.to_datetime(df_copy['date_time'])
        df_copy['pnl'] = pd.to_numeric(df_copy['pnl'], errors='coerce').fillna(0.0)
        df_copy['date_only'] = df_copy['date_time'].dt.date
        
        grouped_global = df_copy.groupby('date_only')['pnl'].sum()
        daily_pnl_by_date = {k: float(v) for k, v in grouped_global.items()}

    def get_color_details(pnl_val):
        if pnl_val is None:
            return "#1e2533", "#64748b", "No Trade"
        if pnl_val > threshold:
            return "#00e676", "#050a14", f"+{pnl_val:,.2f} {curr_symbol} (Profitable)"
        elif 0 < pnl_val <= threshold:
            return "#0d9488", "#ffffff", f"+{pnl_val:,.2f} {curr_symbol} (Small Profit)"
        elif pnl_val == 0:
            return "#7c3aed", "#ffffff", f"0.00 {curr_symbol} (Break-even)"
        elif -threshold <= pnl_val < 0:
            return "#be123c", "#ffffff", f"{pnl_val:,.2f} {curr_symbol} (Loss)"
        else:
            return "#ff1744", "#ffffff", f"{pnl_val:,.2f} {curr_symbol} (Heavy Loss)"

    content_html = ""

    if time_filter == "This Week":
        start_of_week = now.date() - timedelta(days=now.weekday())
        week_days_info = [
            ("Mon", start_of_week + timedelta(days=0), 0),
            ("Tue", start_of_week + timedelta(days=1), 1),
            ("Wed", start_of_week + timedelta(days=2), 2),
            ("Thu", start_of_week + timedelta(days=3), 3),
            ("Fri", start_of_week + timedelta(days=4), 4),
            ("Sat", start_of_week + timedelta(days=5), 5),
            ("Sun", start_of_week + timedelta(days=6), 6),
        ]
        
        grid_html = '<div class="hm-week-grid">'
        for label, d_date, idx in week_days_info[:5]:
            pnl_val = daily_pnl_by_date.get(d_date, None)
            bg, text_color, tip = get_color_details(pnl_val)
            today_cls = " hm-cell-today" if idx == today_weekday else ""
            grid_html += f'<div class="hm-week-cell{today_cls}" style="background-color:{bg}; color:{text_color};" title="{label} ({d_date}): {tip}">{label}</div>'
        
        for label, d_date, idx in week_days_info[5:]:
            pnl_val = daily_pnl_by_date.get(d_date, None)
            bg, text_color, tip = get_color_details(pnl_val)
            today_cls = " hm-cell-today" if idx == today_weekday else ""
            grid_html += f'<div class="hm-week-cell{today_cls}" style="background-color:{bg}; color:{text_color};" title="{label} ({d_date}): {tip}">{label}</div>'
            
        for _ in range(3):
            grid_html += '<div class="hm-week-empty"></div>'
            
        grid_html += '</div>'
        content_html = grid_html

    elif time_filter == "This Month":
        cal = calendar.monthcalendar(year, month)
        grid_html = '''<div class="hm-weekdays">
<div class="hm-weekday">Mon</div><div class="hm-weekday">Tue</div><div class="hm-weekday">Wed</div>
<div class="hm-weekday">Thu</div><div class="hm-weekday">Fri</div><div class="hm-weekday">Sat</div><div class="hm-weekday">Sun</div>
</div><div class="hm-grid">'''
        for week in cal:
            for day in week:
                if day == 0:
                    grid_html += '<div class="hm-empty"></div>'
                else:
                    d_date = datetime(year, month, day).date()
                    pnl_val = daily_pnl_by_date.get(d_date, None)
                    bg, text_color, tip = get_color_details(pnl_val)
                    today_cls = " hm-cell-today" if day == today_day else ""
                    grid_html += f'<div class="hm-cell{today_cls}" style="background-color:{bg}; color:{text_color};" title="Día {day}: {tip}">{day}</div>'
        grid_html += '</div>'
        content_html = grid_html

    elif time_filter == "This Year":
        months_short = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        year_html = '<div class="hm-year-container">'
        
        for m_idx, m_name in enumerate(months_short, start=1):
            num_days = calendar.monthrange(year, m_idx)[1]
            year_html += f'<div class="hm-year-month-row"><div class="hm-year-month-label">{m_name}</div><div class="hm-year-mini-grid">'
            
            for day in range(1, num_days + 1):
                d_date = datetime(year, m_idx, day).date()
                pnl_val = daily_pnl_by_date.get(d_date, None)
                bg, _, tip = get_color_details(pnl_val)
                today_cls = " hm-cell-today" if (m_idx == month and day == today_day) else ""
                year_html += f'<div class="hm-mini-box{today_cls}" style="background-color:{bg};" title="{m_name} {day}: {tip}"></div>'
                
            year_html += '</div></div>'
            
        year_html += '</div>'
        content_html = year_html

    else:
        if df_trades.empty:
            content_html = '<div class="hm-no-data-box">No trading data available</div>'
        else:
            years_present = sorted(df_trades['date_time'].dt.year.unique(), reverse=True)
            months_short = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            all_html = '<div class="hm-year-container">'
            
            for y in years_present:
                all_html += f'<div style="color:#00d2ff; font-weight:800; font-size:12px; margin: 2px 0 4px 0;">{y}</div>'
                for m_idx, m_name in enumerate(months_short, start=1):
                    num_days = calendar.monthrange(y, m_idx)[1]
                    all_html += f'<div class="hm-year-month-row"><div class="hm-year-month-label">{m_name}</div><div class="hm-year-mini-grid">'
                    for day in range(1, num_days + 1):
                        d_date = datetime(y, m_idx, day).date()
                        pnl_val = daily_pnl_by_date.get(d_date, None)
                        bg, _, tip = get_color_details(pnl_val)
                        today_cls = " hm-cell-today" if (y == year and m_idx == month and day == today_day) else ""
                        all_html += f'<div class="hm-mini-box{today_cls}" style="background-color:{bg};" title="{d_date}: {tip}"></div>'
                    all_html += '</div></div>'
                    
            all_html += '</div>'
            content_html = all_html

    full_html = f"""<div class="hm-card">
<div>{content_html}</div>
<div class="hm-legend">
<div class="hm-leg-item"><span class="hm-dot" style="background:#00e676;"></span> Profitable</div>
<div class="hm-leg-item"><span class="hm-dot" style="background:#0d9488;"></span> Small Profit</div>
<div class="hm-leg-item"><span class="hm-dot" style="background:#7c3aed;"></span> Break-even</div>
<div class="hm-leg-item"><span class="hm-dot" style="background:#be123c;"></span> Loss</div>
<div class="hm-leg-item"><span class="hm-dot" style="background:#ff1744;"></span> Heavy Loss</div>
<div class="hm-leg-item"><span class="hm-dot" style="background:#1e2533;"></span> No Trade</div>
</div>
</div>"""
    return full_html

# ==========================================
# GENERADOR DEL MÓDULO TOP TRADES
# ==========================================
def render_top_trades_list(df_trades, curr_symbol, mode):
    if df_trades.empty:
        return '<div style="color: #64748b; font-size: 14px; text-align: center; padding: 45px 0;">No trading data available</div>'
    
    df_copy = df_trades.copy()
    df_copy['pnl'] = pd.to_numeric(df_copy['pnl'], errors='coerce').fillna(0.0)
    df_copy['date_time'] = pd.to_datetime(df_copy['date_time'])
    
    if mode == "winners":
        df_filtered = df_copy[df_copy['pnl'] > 0].sort_values(by='pnl', ascending=False).head(3)
        badge_bg = "rgba(0, 255, 163, 0.12)"
        badge_color = "#00ffa3"
        badge_border = "rgba(0, 255, 163, 0.4)"
    else:
        df_filtered = df_copy[df_copy['pnl'] < 0].sort_values(by='pnl', ascending=True).head(3)
        badge_bg = "rgba(255, 51, 102, 0.12)"
        badge_color = "#ff3366"
        badge_border = "rgba(255, 51, 102, 0.4)"
        
    if df_filtered.empty:
        cat_name = "ganadoras" if mode == "winners" else "perdedoras"
        return f'<div style="color: #64748b; font-size: 13.5px; text-align: center; padding: 45px 0;">No hay operaciones {cat_name} registradas.</div>'
        
    items_html = []
    for rank, (_, row) in enumerate(df_filtered.iterrows(), start=1):
        pnl_val = abs(float(row['pnl']))
        sign = "" if mode == "winners" else "-"
        fmt_amt = f"{sign}{curr_symbol}{pnl_val:,.0f}" if ("COP" in curr_symbol or "COL$" in curr_symbol) else f"{sign}{curr_symbol}{pnl_val:,.2f}"
        dt_str = row['date_time'].strftime('%b %d, %Y')
        asset_str = row.get('asset', '')
        asset_display = f" · <span style='color:#00d2ff;'>💎 {asset_str}</span>" if asset_str else ""
        
        item_code = f"""
        <div style="display: flex; align-items: center; justify-content: space-between; padding: 12px 6px; border-bottom: 1px solid rgba(30, 41, 59, 0.45);">
            <div style="display: flex; align-items: center; gap: 14px;">
                <div style="width: 44px; height: 44px; border-radius: 12px; background: {badge_bg}; border: 1.5px solid {badge_border}; color: {badge_color}; font-size: 15px; font-weight: 800; display: flex; align-items: center; justify-content: center; flex-shrink: 0; box-shadow: 0 0 10px {badge_bg};">
                    #{rank}
                </div>
                <div>
                    <div style="color: #ffffff; font-size: 20px; font-weight: 800; line-height: 1.2;">
                        {fmt_amt}
                    </div>
                    <div style="color: #94a3b8; font-size: 12.5px; font-weight: 500; margin-top: 2px;">
                        {dt_str}{asset_display}
                    </div>
                </div>
            </div>
        </div>
        """
        items_html.append(item_code)
        
    return "".join(items_html)

# ==========================================
# GENERADOR DE TABLA ANALÍTICA ULTRA ESTILIZADA
# ==========================================
def render_analytics_table(df_table, curr_symbol):
    if df_table.empty:
        return '<div style="color: #64748b; padding: 25px; text-align: center;">No hay operaciones registradas para mostrar en esta temporalidad.</div>'
    
    rows_html = []
    for idx, row in df_table.reset_index(drop=True).iterrows():
        trade_num = idx + 1
        dt_str = pd.to_datetime(row['date_time']).strftime('%Y-%m-%d %H:%M:%S')
        mkt = row.get('market', '-')
        asset = row.get('asset', '-')
        dir_val = str(row.get('direction', '-'))
        amount_val = float(row.get('amount', 0))
        res_val = str(row.get('result', '-'))
        pnl_val = float(row.get('pnl', 0))
        emo = row.get('emotion', '-')
        conf = row.get('confidence', '-')
        sess = row.get('session', '-')
        obs = str(row.get('observation', ''))
        
        if "CALL" in dir_val or "BUY" in dir_val or "🟢" in dir_val:
            dir_badge = '<span class="badge-call">CALL 🟢</span>'
        elif "PUT" in dir_val or "SELL" in dir_val or "🔴" in dir_val:
            dir_badge = '<span class="badge-put">PUT 🔴</span>'
        else:
            dir_badge = f'<span class="trade-badge">{dir_val}</span>'
            
        if "WIN" in res_val:
            res_badge = '<span class="badge-win">WIN 🎉</span>'
        elif "LOSS" in res_val:
            res_badge = '<span class="badge-loss">LOSS ❌</span>'
        else:
            res_badge = '<span class="badge-tie">EMPATE ➖</span>'
            
        if pnl_val > 0:
            pnl_html = f'<b style="color: #00ffa3; font-size: 14px;">+{curr_symbol}{pnl_val:,.2f}</b>'
        elif pnl_val < 0:
            pnl_html = f'<b style="color: #ff3366; font-size: 14px;">-{curr_symbol}{abs(pnl_val):,.2f}</b>'
        else:
            pnl_html = f'<span style="color: #94a3b8; font-size: 13.5px;">{curr_symbol}0.00</span>'
            
        if obs and obs != "None" and obs.strip() != "":
            obs_display = f'<span style="color: #d200ff; font-style: italic; font-size: 12px;">{obs[:35]}...</span>' if len(obs) > 35 else f'<span style="color: #d200ff; font-style: italic; font-size: 12px;">{obs}</span>'
        else:
            obs_display = '<span style="color:#475569;">—</span>'
            
        row_html = (
            f'<tr>'
            f'<td style="color:#00d2ff; font-weight:800; text-align:center;">#{trade_num}</td>'
            f'<td style="color:#94a3b8; font-size:12.5px;">{dt_str}</td>'
            f'<td style="color:#e2e8f0; font-weight:600;">{mkt}</td>'
            f'<td style="color:#00d2ff; font-weight:800; letter-spacing:0.5px;">💎 {asset}</td>'
            f'<td>{dir_badge}</td>'
            f'<td style="color:#ffffff; font-weight:700;">{curr_symbol}{amount_val:,.2f}</td>'
            f'<td>{res_badge}</td>'
            f'<td>{pnl_html}</td>'
            f'<td style="color:#cbd5e1;">{emo}</td>'
            f'<td style="color:#cbd5e1;">{conf}</td>'
            f'<td style="color:#cbd5e1;">{sess}</td>'
            f'<td>{obs_display}</td>'
            f'</tr>'
        )
        rows_html.append(row_html)
        
    table_content = "".join(rows_html)
    full_html = (
        '<div class="quantum-table-wrapper">'
        '<table class="quantum-table">'
        '<thead><tr>'
        '<th style="text-align:center;">#</th>'
        '<th>Fecha & Hora</th>'
        '<th>Mercado</th>'
        '<th>Activo</th>'
        '<th>Dirección</th>'
        '<th>Inversión</th>'
        '<th>Resultado</th>'
        '<th>P&L</th>'
        '<th>Emoción</th>'
        '<th>Confianza</th>'
        '<th>Sesión</th>'
        '<th>Notas</th>'
        '</tr></thead>'
        f'<tbody>{table_content}</tbody>'
        '</table>'
        '</div>'
    )
    return full_html

# ==========================================
# GENERADOR DE TABLA CUÁNTICA DE CUENTAS
# ==========================================
def render_accounts_table(df_acc):
    if df_acc.empty:
        return '<div style="color: #64748b; padding: 25px; text-align: center;">No hay cuentas registradas en el sistema cuántico.</div>'
    
    rows_html = []
    for idx, row in df_acc.iterrows():
        acc_id = row['id']
        broker = row['broker']
        acc_name = row['account_name']
        init_bal = float(row['initial_balance'])
        curr = row.get('currency', 'USD ($)')
        curr_sym = get_currency_symbol(curr)
        
        row_html = (
            f'<tr>'
            f'<td style="color:#00d2ff; font-weight:800; text-align:center;">'
            f'<span style="background:rgba(0,210,255,0.12); border:1px solid rgba(0,210,255,0.35); padding:4px 10px; border-radius:8px;">ID #{acc_id}</span>'
            f'</td>'
            f'<td style="color:#ffffff; font-weight:700; font-size:14.5px;"><span style="color:#00d2ff; margin-right:6px;">🌐</span>{broker}</td>'
            f'<td style="color:#cbd5e1; font-weight:600;"><span style="color:#d200ff; margin-right:6px;">🏷️</span>{acc_name}</td>'
            f'<td style="color:#00ffa3; font-weight:800; font-size:16px; text-shadow:0 0 10px rgba(0,255,163,0.3);">{curr_sym}{init_bal:,.2f} <span style="font-size:11px; color:#94a3b8;">({curr})</span></td>'
            f'<td style="text-align:center;"><span style="background:rgba(0,255,163,0.12); color:#00ffa3; border:1px solid rgba(0,255,163,0.4); padding:4px 12px; border-radius:8px; font-weight:800; font-size:11px; letter-spacing:0.5px;">🟢 VINCULADA</span></td>'
            f'</tr>'
        )
        rows_html.append(row_html)
        
    table_content = "".join(rows_html)
    full_html = (
        '<div class="quantum-table-wrapper">'
        '<table class="quantum-table">'
        '<thead><tr>'
        '<th style="text-align:center; width:130px;">IDENTIFICADOR</th>'
        '<th>BRÓKER</th>'
        '<th>TIPO DE CUENTA</th>'
        '<th>CAPITAL INICIAL</th>'
        '<th style="text-align:center; width:160px;">ESTADO</th>'
        '</tr></thead>'
        f'<tbody>{table_content}</tbody>'
        '</table>'
        '</div>'
    )
    return full_html

# ==========================================
# SISTEMA DE LOGIN (LIMPIO, SIMÉTRICO Y CENTRADO)
# ==========================================
def custom_pin_pad():
    st.markdown(CSS_LOGIN, unsafe_allow_html=True)
    
    if "pin_input" not in st.session_state: 
        st.session_state.pin_input = ""
    if "login_feedback" not in st.session_state:
        st.session_state.login_feedback = "INGRESE SU PIN"
        st.session_state.login_feedback_type = "normal"

    def add_digit(digit):
        if len(st.session_state.pin_input) < 4: 
            st.session_state.pin_input += str(digit)
            if len(st.session_state.pin_input) == 4:
                if st.session_state.pin_input == str(st.secrets["APP_PASSWORD"]):
                    st.session_state.login_feedback = "PIN CORRECTO"
                    st.session_state.login_feedback_type = "success"
                else:
                    st.session_state.login_feedback = "PIN INCORRECTO"
                    st.session_state.login_feedback_type = "error"

    def clear_pin(): 
        st.session_state.pin_input = ""
        st.session_state.login_feedback = "INGRESE SU PIN"
        st.session_state.login_feedback_type = "normal"

    feedback = st.session_state.login_feedback
    fb_type = st.session_state.login_feedback_type
    box_style = "border-color: rgba(0, 210, 255, 0.4); color: #00d2ff;"
    
    if fb_type == "success":
        box_style = "border-color: #00ffa3; color: #00ffa3; box-shadow: 0 0 20px rgba(0,255,163,0.5); background: rgba(0,255,163,0.12);"
    elif fb_type == "error":
        box_style = "border-color: #ff3366; color: #ff3366; box-shadow: 0 0 20px rgba(255,51,102,0.5); background: rgba(255,51,102,0.12);"

    st.markdown(f'<div class="login-status-capsule" style="{box_style}">{feedback}</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="login-title">⚡ MYTRADES</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-subtitle">ACCESO SEGURO AL SISTEMA CUÁNTICO</div>', unsafe_allow_html=True)

    filled_len = len(st.session_state.pin_input)
    dots_html = "".join([f'<div class="pin-dot {"active" if i < filled_len else ""}"></div>' for i in range(4)])
    st.markdown(f'<div class="pin-display">{dots_html}</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1: st.button("1", on_click=add_digit, args=(1,), key="l_1")
    with c2: st.button("2", on_click=add_digit, args=(2,), key="l_2")
    with c3: st.button("3", on_click=add_digit, args=(3,), key="l_3")

    c4, c5, c6 = st.columns(3)
    with c4: st.button("4", on_click=add_digit, args=(4,), key="l_4")
    with c5: st.button("5", on_click=add_digit, args=(5,), key="l_5")
    with c6: st.button("6", on_click=add_digit, args=(6,), key="l_6")

    c7, c8, c9 = st.columns(3)
    with c7: st.button("7", on_click=add_digit, args=(7,), key="l_7")
    with c8: st.button("8", on_click=add_digit, args=(8,), key="l_8")
    with c9: st.button("9", on_click=add_digit, args=(9,), key="l_9")

    c_clear, c0, c_empty = st.columns(3)
    with c_clear: st.button("🗑️", on_click=clear_pin, key="l_clear")
    with c0: st.button("0", on_click=add_digit, args=(0,), key="l_0")
    with c_empty: st.empty()

    if len(st.session_state.pin_input) == 4:
        if st.session_state.pin_input == str(st.secrets["APP_PASSWORD"]):
            time.sleep(0.6)
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            time.sleep(0.6)
            st.session_state.pin_input = ""
            st.session_state.login_feedback = "INGRESE SU PIN"
            st.session_state.login_feedback_type = "normal"
            st.rerun()
    return False

# ==========================================
# RUTEO DE PANTALLAS Y BASE DE DATOS RESILIENTE
# ==========================================
if "password_correct" not in st.session_state or not st.session_state["password_correct"]:
    custom_pin_pad()
else:
    st.markdown(CSS_DASHBOARD, unsafe_allow_html=True)
    
    @st.cache_resource
    def get_db_connection():
        conexion = psycopg2.connect(
            st.secrets["DATABASE_URL"],
            keepalives=1,
            keepalives_idle=30,
            keepalives_interval=10,
            keepalives_count=5
        )
        conexion.autocommit = True
        return conexion

    def get_active_connection():
        try:
            conexion = get_db_connection()
            if conexion.closed != 0:
                st.cache_resource.clear()
                conexion = get_db_connection()
            else:
                with conexion.cursor() as cur_check:
                    cur_check.execute("SELECT 1")
            return conexion
        except Exception:
            st.cache_resource.clear()
            return get_db_connection()

    conn = get_active_connection()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS accounts (id SERIAL PRIMARY KEY, broker VARCHAR(100), account_name VARCHAR(100), initial_balance NUMERIC)''')
    
    try:
        c.execute("ALTER TABLE accounts ADD COLUMN IF NOT EXISTS currency VARCHAR(20) DEFAULT 'USD ($)';")
    except:
        pass

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

    def get_accounts(): 
        active_conn = get_active_connection()
        return pd.read_sql_query("SELECT * FROM accounts", active_conn)

    def get_trades(account_id): 
        active_conn = get_active_connection()
        df = pd.read_sql_query(f"SELECT * FROM trades WHERE account_id = {account_id} ORDER BY date_time ASC", active_conn)
        
        if not df.empty:
            mask = df['result'].str.contains("WIN", na=False) & (df['pnl'] == 0.0)
            if mask.any():
                df.loc[mask, 'pnl'] = df.loc[mask, 'amount'] * 0.85
                
        return df

    # ==========================================
    # BARRA LATERAL (SIDEBAR ANIMADA Y FUTURISTA)
    # ==========================================
    st.sidebar.markdown('<div class="sidebar-title">⚡ MYTRADES</div>', unsafe_allow_html=True)
    st.sidebar.markdown('<p style="color: #64748b; font-size: 11px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 10px;">Navegación</p>', unsafe_allow_html=True)
    
    menu = st.sidebar.radio("Navegación Principal", ["📊 Dashboard Principal", "🏦 Gestionar Cuentas"], label_visibility="collapsed")
    
    st.sidebar.markdown("<br><br><br>", unsafe_allow_html=True)
    st.sidebar.markdown("<hr style='border-color: #1e293b;'>", unsafe_allow_html=True)
    
    if st.sidebar.button("Cerrar Sesión 🔒"):
        del st.session_state["password_correct"]
        st.session_state.pin_input = ""
        st.rerun()

    if menu == "🏦 Gestionar Cuentas":
        st.markdown('''<div style="margin-top: 5px; margin-bottom: 20px;">
<div style="color: #00d2ff; font-size: 18px; font-weight: 800; letter-spacing: 2px; text-transform: uppercase;">🏦 BÓVEDA Y GESTIÓN DE CUENTAS</div>
<div style="color: #64748b; font-size: 12px; margin-top: -2px;">ADMINISTRACIÓN DE PORTAFOLIOS, BRÓKERS Y CAPITAL ASIGNADO</div>
</div>''', unsafe_allow_html=True)
        
        df_accounts = get_accounts()
        total_accs = len(df_accounts)
        
        cap_summary_html = "$0.00"
        if not df_accounts.empty:
            if 'currency' in df_accounts.columns:
                grouped_curr = df_accounts.groupby('currency')['initial_balance'].sum()
                parts = []
                for curr_val, sum_val in grouped_curr.items():
                    sym = get_currency_symbol(curr_val)
                    parts.append(f"{sym}{sum_val:,.2f}")
                cap_summary_html = " &nbsp;|&nbsp; ".join(parts)
            else:
                total_cap = float(df_accounts['initial_balance'].sum())
                cap_summary_html = f"${total_cap:,.2f}"

        top_broker = df_accounts['broker'].mode()[0] if not df_accounts.empty else "N/A"
        
        acc_kpis = st.columns(3)
        with acc_kpis[0]:
            st.markdown(f'''<div class="kpi-card-exact">
<div style="color: #64748b; font-size: 11px; font-weight: 600; letter-spacing: 1.5px; text-transform: uppercase;">CUENTAS REGISTRADAS</div>
<div style="color: #00d2ff; font-size: 26px; font-weight: 700; margin: 0;">{total_accs}</div>
<div style="color: #94a3b8; font-size: 11px;">Portafolios activos</div>
</div>''', unsafe_allow_html=True)
        with acc_kpis[1]:
            st.markdown(f'''<div class="kpi-card-exact">
<div style="color: #64748b; font-size: 11px; font-weight: 600; letter-spacing: 1.5px; text-transform: uppercase;">CAPITAL INICIAL TOTAL</div>
<div style="color: #00ffa3; font-size: 18px; font-weight: 700; margin: 0; text-shadow:0 0 10px rgba(0,255,163,0.3);">{cap_summary_html}</div>
<div style="color: #94a3b8; font-size: 11px;">Fondos por moneda</div>
</div>''', unsafe_allow_html=True)
        with acc_kpis[2]:
            st.markdown(f'''<div class="kpi-card-exact">
<div style="color: #64748b; font-size: 11px; font-weight: 600; letter-spacing: 1.5px; text-transform: uppercase;">BRÓKER PRINCIPAL</div>
<div style="color: #ffffff; font-size: 24px; font-weight: 700; margin: 0;">{top_broker}</div>
<div style="color: #94a3b8; font-size: 11px;">Mayor frecuencia</div>
</div>''', unsafe_allow_html=True)

        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

        currency = st.selectbox("💱 Seleccionar Moneda de la Cuenta", ["USD ($)", "COP (COL$)", "EUR (€)", "MXN ($)"])
        curr_sym_form = get_currency_symbol(currency)
        default_bal = 50000.0 if "COP" in currency else 100.0
        step_bal = 1000.0 if "COP" in currency else 10.0
        fmt_bal = "%.0f" if "COP" in currency else "%.2f"

        # 1. CREAR NUEVA CUENTA DE TRADING
        with st.container(border=True):
            st.markdown('''<div style="display: flex; justify-content: space-between; align-items: center; padding-bottom: 10px; border-bottom: 1px solid #1e293b; margin-bottom: 15px;">
<div style="font-size: 14px; font-weight: 800; color: #ffffff; display: flex; align-items: center; gap: 8px;">
<span>⚡</span> CREAR NUEVA CUENTA DE TRADING
</div>
<div style="color: #00d2ff; font-size: 12px; font-weight: bold; letter-spacing: 1px;">MÓDULO DE REGISTRO</div>
</div>''', unsafe_allow_html=True)
            
            with st.form("new_account_form", clear_on_submit=True):
                col1, col2, col3 = st.columns(3)
                with col1: broker = st.text_input("🌐 Bróker (Ej. Quotex, IQ Option)")
                with col2: acc_name = st.selectbox("🏷️ Tipo de Cuenta", ["Real", "Demo"])
                with col3: init_balance = st.number_input(f"💵 Balance Inicial ({curr_sym_form})", min_value=0.0, value=default_bal, step=step_bal, format=fmt_bal)
                
                st.markdown("<br>", unsafe_allow_html=True)
                guardar_cuenta = st.form_submit_button("🚀 REGISTRAR Y VINCULAR CUENTA")
                
                if guardar_cuenta and broker:
                    active_conn = get_active_connection()
                    with active_conn.cursor() as cur:
                        cur.execute("INSERT INTO accounts (broker, account_name, initial_balance, currency) VALUES (%s, %s, %s, %s)", (broker, acc_name, init_balance, currency))
                        active_conn.commit()
                    st.success("✅ Cuenta cuántica creada y registrada exitosamente.")
                    time.sleep(0.5)
                    st.rerun()

        # 2. TABLA DE PORTAFOLIOS Y CUENTAS VINCULADAS
        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
        st.markdown('<div style="color: #ffffff; font-size: 16px; font-weight: bold; margin-bottom: 12px;">📋 Portafolios y Cuentas Vinculadas</div>', unsafe_allow_html=True)
        st.markdown(render_accounts_table(df_accounts), unsafe_allow_html=True)

        # 3. ZONA DE PELIGRO: ELIMINAR CUENTA INDIVIDUAL
        st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown('''<div style="display: flex; justify-content: space-between; align-items: center; padding-bottom: 10px; border-bottom: 1px solid #1e293b; margin-bottom: 15px;">
<div style="font-size: 14px; font-weight: 800; color: #ff3366; display: flex; align-items: center; gap: 8px;">
<span>⚠️</span> ELIMINAR O DESVINCULAR CUENTA
</div>
<div style="color: #64748b; font-size: 12px; font-weight: bold; letter-spacing: 1px;">ZONA DE PELIGRO</div>
</div>''', unsafe_allow_html=True)
            
            if not df_accounts.empty:
                del_options = df_accounts.apply(lambda x: f"ID #{x['id']} — {x['broker']} ({x['account_name']})", axis=1).tolist()
                with st.form("delete_account_form"):
                    selected_to_delete = st.selectbox("Selecciona la cuenta a eliminar:", del_options)
                    confirm_del = st.checkbox("Confirmo que deseo eliminar esta cuenta y todo su historial de operaciones asociado.")
                    submit_del = st.form_submit_button("🗑️ ELIMINAR CUENTA DEFINITIVAMENTE")
                    
                    if submit_del:
                        if confirm_del:
                            del_id = int(selected_to_delete.split("ID #")[1].split(" —")[0])
                            active_conn = get_active_connection()
                            with active_conn.cursor() as cur:
                                cur.execute("DELETE FROM trades WHERE account_id = %s", (del_id,))
                                cur.execute("DELETE FROM accounts WHERE id = %s", (del_id,))
                                active_conn.commit()
                            st.success("✅ Cuenta e historial de operaciones eliminados correctamente.")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.warning("⚠️ Debes marcar la casilla de confirmación para proceder.")
            else:
                st.markdown('<div style="color: #64748b; font-size: 13px;">No hay cuentas disponibles para eliminar.</div>', unsafe_allow_html=True)

        # 4. ZONA DE PELIGRO: REINICIO DE FÁBRICA / BORRADO TOTAL
        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown('''<div style="display: flex; justify-content: space-between; align-items: center; padding-bottom: 10px; border-bottom: 1px solid #1e293b; margin-bottom: 15px;">
<div style="font-size: 14px; font-weight: 800; color: #ff1948; display: flex; align-items: center; gap: 8px;">
<span>💣</span> REINICIO TOTAL / DEJAR SISTEMA EN BLANCO
</div>
<div style="color: #ff3366; font-size: 11px; font-weight: bold; letter-spacing: 1px;">FORMATO COMPLETO</div>
</div>''', unsafe_allow_html=True)

            st.markdown('<p style="color: #94a3b8; font-size: 12.5px; margin-bottom: 14px;">Esta opción vaciará la base de datos por completo: borrará <b>todas las cuentas</b> y <b>todo el historial de trades</b> para iniciar desde cero.</p>', unsafe_allow_html=True)

            with st.form("reset_all_data_form"):
                confirm_reset_all = st.checkbox("⚠️ Confirmo que estoy totalmente seguro y deseo eliminar ABSOLUTAMENTE TODOS los datos del sistema.")
                submit_reset_all = st.form_submit_button("💥 RESTABLECER Y BORRAR TODO EL SISTEMA")

                if submit_reset_all:
                    if confirm_reset_all:
                        active_conn = get_active_connection()
                        with active_conn.cursor() as cur:
                            try:
                                cur.execute("TRUNCATE TABLE trades, accounts RESTART IDENTITY CASCADE;")
                            except Exception:
                                cur.execute("DELETE FROM trades;")
                                cur.execute("DELETE FROM accounts;")
                            active_conn.commit()
                        st.success("✅ Base de datos formateada con éxito. El sistema ha quedado completamente limpio.")
                        time.sleep(0.8)
                        st.rerun()
                    else:
                        st.warning("⚠️ Debes marcar la casilla de confirmación para autorizar el borrado total de la plataforma.")

    elif menu == "📊 Dashboard Principal":
        df_accounts = get_accounts()
        if df_accounts.empty:
            st.warning("⚠️ Crea una cuenta en el menú lateral para iniciar.")
        else:
            top_col1, top_col2 = st.columns([1.8, 1.2])
            with top_col1:
                st.markdown('<div style="color: #00d2ff; font-size: 16px; font-weight: 800; letter-spacing: 2px; text-transform: uppercase; margin-top: 5px;">⚡ TERMINAL DE COMANDO CUÁNTICO</div>', unsafe_allow_html=True)
                st.markdown('<div style="color: #64748b; font-size: 11px; margin-top: -3px;">CENTRO DE MONITOREO Y EJECUCIÓN EN TIEMPO REAL</div>', unsafe_allow_html=True)
            with top_col2:
                def get_clean_account_label(row):
                    broker_clean = str(row['broker']).strip().title()
                    type_clean = str(row['account_name']).strip().capitalize()
                    raw_curr = str(row.get('currency', 'USD'))
                    curr_clean = "USD"
                    for c in ["USD", "COP", "EUR", "MXN"]:
                        if c in raw_curr:
                            curr_clean = c
                            break
                    return f"{broker_clean} · {type_clean} ({curr_clean})"

                account_ids = df_accounts['id'].tolist()
                account_labels_map = {row['id']: get_clean_account_label(row) for _, row in df_accounts.iterrows()}

                selected_acc_id = st.selectbox(
                    "CUENTA ACTIVA:",
                    options=account_ids,
                    format_func=lambda x: account_labels_map.get(x, f"Cuenta #{x}"),
                    label_visibility="collapsed"
                )
            
            acc_row = df_accounts[df_accounts['id'] == selected_acc_id].iloc[0]
            initial_balance = float(acc_row['initial_balance'])
            account_currency = acc_row.get('currency', 'USD ($)')
            curr_symbol = get_currency_symbol(account_currency)
            
            df_trades = get_trades(selected_acc_id)

            win_rate, net_profit, wins, losses = 0.0, 0.0, 0, 0
            current_balance = initial_balance
            total_trades = len(df_trades)
            score_win = score_pf = score_awal = score_rec = score_dd = score_cons = 0
            overall_score = 0
            total_win_sum = 0.0
            total_loss_sum = 0.0

            # Variables de Gestión de Riesgo
            expectancy = 0.0
            sortino_ratio = 0.0
            calmar_ratio = 0.0
            pf_clean = 0.0
            max_loss_streak = 0
            half_kelly_pct = 0.0
            
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
                if pd.isna(avg_win): avg_win = 0.0
                if pd.isna(avg_loss) or avg_loss == 0: avg_loss = 1.0
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

                # Cálculos Cuantitativos de Riesgo
                valid_trades_count = wins + losses
                if valid_trades_count > 0:
                    w_rate = wins / valid_trades_count
                    l_rate = losses / valid_trades_count
                    
                    expectancy = (w_rate * avg_win) - (l_rate * avg_loss)
                    
                    downside_diff = df_trades['pnl'].apply(lambda x: min(0.0, x))
                    downside_std = (downside_diff**2).mean() ** 0.5
                    mean_pnl = df_trades['pnl'].mean()
                    sortino_ratio = (mean_pnl / downside_std) if downside_std > 0 else (4.0 if mean_pnl > 0 else 0.0)
                    
                    max_dd_amount = (df_trades['peak'] - df_trades['equity']).max()
                    calmar_ratio = (net_profit / max_dd_amount) if max_dd_amount > 0 else (net_profit / 1.0 if net_profit > 0 else 0.0)
                    
                    win_df = df_trades[df_trades['pnl'] > 0]
                    if len(win_df) >= 4:
                        top_5_threshold = win_df['pnl'].quantile(0.95)
                        clean_win_sum = win_df[win_df['pnl'] < top_5_threshold]['pnl'].sum()
                    else:
                        clean_win_sum = total_win_sum
                    pf_clean = (clean_win_sum / gross_loss) if gross_loss > 0 else (clean_win_sum if clean_win_sum > 0 else 0.0)
                    
                    cur_streak = 0
                    max_streak = 0
                    for r in df_trades['result']:
                        if "LOSS" in str(r):
                            cur_streak += 1
                            if cur_streak > max_streak:
                                max_streak = cur_streak
                        else:
                            cur_streak = 0
                    max_loss_streak = max_streak
                    
                    if avg_loss > 0 and avg_win > 0:
                        payoff_ratio = avg_win / avg_loss
                        kelly = w_rate - (l_rate / payoff_ratio)
                        half_kelly = kelly * 0.5
                        half_kelly_pct = max(0.0, min(half_kelly * 100, 25.0))

            # ==========================================
            # 5 PANELES SUPERIORES EXACTOS
            # ==========================================
            st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
            kpi_cols = st.columns(5)
            signo = "+" if net_profit >= 0 else ""
            
            with kpi_cols[0]:
                st.markdown(f'''<div class="kpi-card-exact">
<div style="color: #64748b; font-size: 11px; font-weight: 600; letter-spacing: 1.5px; text-transform: uppercase;">WIN RATE</div>
<div style="color: #00d2ff; font-size: 26px; font-weight: 700; margin: 0;">{win_rate:.1f}%</div>
<div style="color: #94a3b8; font-size: 11px;">{wins} Ganadas / {losses} Perdidas</div>
</div>''', unsafe_allow_html=True)
                
            with kpi_cols[1]:
                st.markdown(f'''<div class="kpi-card-exact">
<div style="color: #64748b; font-size: 11px; font-weight: 600; letter-spacing: 1.5px; text-transform: uppercase;">AVG WIN / LOSS</div>
<div style="display: flex; justify-content: space-between; align-items: center; margin-top: 2px;">
<span style="color: #94a3b8; font-size: 11px; font-weight: 500;">WIN</span>
<span style="color: #00ffa3; font-size: 15px; font-weight: bold;">{curr_symbol}{total_win_sum:,.2f}</span>
</div>
<div style="display: flex; justify-content: space-between; align-items: center; margin-top: 2px;">
<span style="color: #94a3b8; font-size: 11px; font-weight: 500;">LOSS</span>
<span style="color: #ff3366; font-size: 15px; font-weight: bold;">-{curr_symbol}{abs(total_loss_sum):,.2f}</span>
</div>
</div>''', unsafe_allow_html=True)

            with kpi_cols[2]:
                pnl_color_hex = "#00ffa3" if net_profit >= 0 else "#ff3366"
                st.markdown(f'''<div class="kpi-card-exact">
<div style="color: #64748b; font-size: 11px; font-weight: 600; letter-spacing: 1.5px; text-transform: uppercase;">NET PNL (BENEFICIO)</div>
<div style="color: {pnl_color_hex}; font-size: 26px; font-weight: 700; margin: 0; text-shadow: 0 0 10px rgba(0,255,163,0.2);">{signo}{curr_symbol}{net_profit:,.2f}</div>
<div style="color: #94a3b8; font-size: 11px;">Moneda: {account_currency}</div>
</div>''', unsafe_allow_html=True)

            with kpi_cols[3]:
                st.markdown(f'''<div class="kpi-card-exact">
<div style="color: #64748b; font-size: 11px; font-weight: 600; letter-spacing: 1.5px; text-transform: uppercase;">BALANCE TOTAL</div>
<div style="color: #ffffff; font-size: 26px; font-weight: 700; margin: 0;">{curr_symbol}{current_balance:,.2f}</div>
<div style="color: #94a3b8; font-size: 11px;">Capital disponible</div>
</div>''', unsafe_allow_html=True)
                
            with kpi_cols[4]:
                st.markdown(f'''<div class="kpi-card-exact">
<div style="color: #64748b; font-size: 11px; font-weight: 600; letter-spacing: 1.5px; text-transform: uppercase;">TRADES EJECUTADOS</div>
<div style="color: #00d2ff; font-size: 26px; font-weight: 700; margin: 0;">{total_trades}</div>
<div style="color: #94a3b8; font-size: 11px;">Volumen total</div>
</div>''', unsafe_allow_html=True)

            # ==========================================
            # SECCIÓN: MATRIZ CUÁNTICA DE RIESGO (DESPLEGABLE)
            # ==========================================
            st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
            with st.expander("🛡️ MATRIZ CUÁNTICA DE RIESGO & GESTIÓN DE RUINA", expanded=False):
                st.markdown('<p style="color: #00d2ff; font-size: 12px; font-weight: 700; letter-spacing: 1.5px; margin-bottom: 12px; text-shadow: 0 0 10px rgba(0,210,255,0.3);">⚡ AUDITORÍA ESTADÍSTICA Y CONTROL CUANTITATIVO DE RUINA</p>', unsafe_allow_html=True)
                
                exp_color = "#00ffa3" if expectancy > 0 else ("#ff3366" if expectancy < 0 else "#94a3b8")
                exp_sign = "+" if expectancy > 0 else ""
                sort_color = "#00ffa3" if sortino_ratio >= 1.5 else ("#00d2ff" if sortino_ratio > 0.5 else "#ff3366")
                calm_color = "#00ffa3" if calmar_ratio >= 2.0 else ("#00d2ff" if calmar_ratio >= 1.0 else "#ff3366")
                pf_clean_color = "#00ffa3" if pf_clean >= 1.2 else ("#ffb800" if pf_clean >= 1.0 else "#ff3366")
                streak_color = "#ff3366" if max_loss_streak >= 4 else ("#ffb800" if max_loss_streak == 3 else "#00ffa3")
                kelly_color = "#00ffa3" if half_kelly_pct > 0 else "#ff3366"

                r_cols = st.columns(6)
                with r_cols[0]:
                    st.markdown(f'''<div class="risk-kpi-card">
<div style="color: #64748b; font-size: 10px; font-weight: 700; letter-spacing: 0.8px; text-transform: uppercase;">ESPERANZA (EV)</div>
<div style="color: {exp_color}; font-size: 19px; font-weight: 800; margin: 3px 0;">{exp_sign}{curr_symbol}{expectancy:,.2f}</div>
<div style="color: #94a3b8; font-size: 10px;">Retorno por trade</div>
</div>''', unsafe_allow_html=True)
                    
                with r_cols[1]:
                    st.markdown(f'''<div class="risk-kpi-card">
<div style="color: #64748b; font-size: 10px; font-weight: 700; letter-spacing: 0.8px; text-transform: uppercase;">RATIO SORTINO</div>
<div style="color: {sort_color}; font-size: 19px; font-weight: 800; margin: 3px 0;">{sortino_ratio:.2f}</div>
<div style="color: #94a3b8; font-size: 10px;">Riesgo a la baja</div>
</div>''', unsafe_allow_html=True)

                with r_cols[2]:
                    st.markdown(f'''<div class="risk-kpi-card">
<div style="color: #64748b; font-size: 10px; font-weight: 700; letter-spacing: 0.8px; text-transform: uppercase;">RATIO CALMAR</div>
<div style="color: {calm_color}; font-size: 19px; font-weight: 800; margin: 3px 0;">{calmar_ratio:.2f}</div>
<div style="color: #94a3b8; font-size: 10px;">Beneficio / Max DD</div>
</div>''', unsafe_allow_html=True)

                with r_cols[3]:
                    st.markdown(f'''<div class="risk-kpi-card">
<div style="color: #64748b; font-size: 10px; font-weight: 700; letter-spacing: 0.8px; text-transform: uppercase;">PF SIN OUTLIERS</div>
<div style="color: {pf_clean_color}; font-size: 19px; font-weight: 800; margin: 3px 0;">{pf_clean:.2f}</div>
<div style="color: #94a3b8; font-size: 10px;">Sin top 5% ganadas</div>
</div>''', unsafe_allow_html=True)

                with r_cols[4]:
                    st.markdown(f'''<div class="risk-kpi-card">
<div style="color: #64748b; font-size: 10px; font-weight: 700; letter-spacing: 0.8px; text-transform: uppercase;">RACHA MÁX. LOSS</div>
<div style="color: {streak_color}; font-size: 19px; font-weight: 800; margin: 3px 0;">{max_loss_streak} <span style="font-size:11px; color: #94a3b8;">trades</span></div>
<div style="color: #94a3b8; font-size: 10px;">Peor racha seguida</div>
</div>''', unsafe_allow_html=True)

                with r_cols[5]:
                    st.markdown(f'''<div class="risk-kpi-card">
<div style="color: #64748b; font-size: 10px; font-weight: 700; letter-spacing: 0.8px; text-transform: uppercase;">HALF-KELLY SUG.</div>
<div style="color: {kelly_color}; font-size: 19px; font-weight: 800; margin: 3px 0;">{half_kelly_pct:.1f}%</div>
<div style="color: #94a3b8; font-size: 10px;">Riesgo / posición</div>
</div>''', unsafe_allow_html=True)
                
                st.markdown("<div style='margin-bottom: 2px;'></div>", unsafe_allow_html=True)

            # ==========================================
            # SECCIÓN 1: CALENDARIO Y PERFIL
            # ==========================================
            st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
            col_cal, col_prof = st.columns([1.18, 0.82])
            
            with col_cal:
                if "cal_year" not in st.session_state:
                    st.session_state["cal_year"] = datetime.now().year
                if "cal_month" not in st.session_state:
                    st.session_state["cal_month"] = datetime.now().month

                def prev_month():
                    if st.session_state["cal_month"] == 1:
                        st.session_state["cal_month"] = 12
                        st.session_state["cal_year"] -= 1
                    else:
                        st.session_state["cal_month"] -= 1

                def next_month():
                    if st.session_state["cal_month"] == 12:
                        st.session_state["cal_month"] = 1
                        st.session_state["cal_year"] += 1
                    else:
                        st.session_state["cal_month"] += 1

                with st.container(border=True):
                    c_title, c_prev, c_lbl, c_next = st.columns([2.2, 0.6, 2.0, 0.6])
                    with c_title:
                        st.markdown('<div style="font-size: 14px; font-weight: 800; color: #ffffff; padding-top: 6px; display: flex; align-items: center; gap: 6px;"><span>📅</span> Calendario</div>', unsafe_allow_html=True)
                    with c_prev:
                        st.button("◀", on_click=prev_month, key="cal_prev")
                    with c_lbl:
                        meses_map = {1:"ENERO", 2:"FEBRERO", 3:"MARZO", 4:"ABRIL", 5:"MAYO", 6:"JUNIO", 7:"JULIO", 8:"AGOSTO", 9:"SEPTIEMBRE", 10:"OCTUBRE", 11:"NOVIEMBRE", 12:"DICIEMBRE"}
                        m_label = f"{meses_map[st.session_state['cal_month']]} {st.session_state['cal_year']}"
                        st.markdown(f'<div style="color: #00d2ff; font-size: 12px; font-weight: 800; letter-spacing: 1px; text-align: center; padding-top: 7px; white-space: nowrap;">{m_label}</div>', unsafe_allow_html=True)
                    with c_next:
                        st.button("▶", on_click=next_month, key="cal_next")
                    
                    st.markdown(render_calendar(df_trades, curr_symbol, st.session_state["cal_year"], st.session_state["cal_month"]), unsafe_allow_html=True)
                
            with col_prof:
                with st.container(border=True):
                    st.markdown('''<div style="display: flex; justify-content: space-between; align-items: center; padding-bottom: 8px; border-bottom: 1px solid #1e293b; margin-bottom: 8px;">
<div>
<div style="font-size: 14px; font-weight: 800; color: #ffffff; display: flex; align-items: center; gap: 6px;">⚡ Perfil de Trading</div>
<div style="font-size: 10px; color: #64748b;">Métricas Cuánticas de Rendimiento</div>
</div>
<div style="color: #00d2ff; font-size: 14px;">🎯</div>
</div>''', unsafe_allow_html=True)

                    categories = ['Win %', 'Profit Factor', 'Avg Win/Loss', 'Recovery', 'Drawdown', 'Consistency']
                    values = [score_win, score_pf, score_awal, score_rec, score_dd, score_cons]
                    values_loop = values + [values[0]]
                    categories_loop = categories + [categories[0]]
                    
                    fig_radar = go.Figure(data=go.Scatterpolar(
                        r=values_loop, 
                        theta=categories_loop, 
                        fill='toself',
                        fillcolor='rgba(0, 255, 163, 0.22)', 
                        line=dict(color='#00ffa3', width=2.5), 
                        marker=dict(size=5, color='#00ffa3')
                    ))
                    fig_radar.update_layout(
                        polar=dict(
                            radialaxis=dict(visible=False, range=[0, 105]), 
                            angularaxis=dict(
                                color='#94a3b8', 
                                gridcolor='#1e293b', 
                                linecolor='#1e293b', 
                                gridwidth=1,
                                tickfont=dict(size=11, color='#cbd5e1', family='sans-serif')
                            ), 
                            bgcolor='rgba(0,0,0,0)'
                        ),
                        showlegend=False, 
                        paper_bgcolor='rgba(0,0,0,0)', 
                        plot_bgcolor='rgba(0,0,0,0)',
                        margin=dict(l=65, r=65, t=18, b=18), 
                        height=280
                    )
                    st.plotly_chart(fig_radar, width='stretch', config={'displayModeBar': False})

                    st.markdown(f'''<div style="padding-top: 6px; margin-bottom: 4px;">
<div style="display: flex; justify-content: space-between; align-items: flex-end;">
<div style="color: #94a3b8; font-size: 11.5px; font-weight: 600;">Trading Score</div>
<div><span style="color: #00ffa3; font-size: 21px; font-weight: 800; text-shadow: 0 0 10px rgba(0,255,163,0.3);">{overall_score}</span><span style="color: #64748b; font-size: 11px; font-weight: 700;"> / 100</span></div>
</div>
<div class="progress-bar-bg"><div class="progress-bar-fill" style="width: {overall_score}%;"></div></div>
<div style="display: flex; justify-content: space-between; margin-top: 5px;">
<div style="color: #64748b; font-size: 9px; font-weight: 800; letter-spacing: 1px;">NOVATO</div>
<div style="color: #00d2ff; font-size: 9px; font-weight: 800; letter-spacing: 1px;">PRO</div>
</div>
</div>''', unsafe_allow_html=True)

            # ==========================================
            # SECCIÓN: TRADING HEATMAP & TOP TRADES
            # ==========================================
            st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
            col_hm_main, col_top_trades = st.columns([1.18, 0.82])
            
            with col_hm_main:
                h_col_t, h_col_s = st.columns([1.55, 1.45])
                with h_col_t:
                    st.markdown('<div style="font-size: 19px; font-weight: 800; color: #ffffff; padding-top: 5px; display: flex; align-items: center; gap: 8px;"><span>🔥</span> Trading Heatmap</div>', unsafe_allow_html=True)
                with h_col_s:
                    hm_filter = st.selectbox("TEMPORALIDAD HEATMAP:", ["This Month", "This Week", "This Year", "All Time"], label_visibility="collapsed", key="hm_view_filter")
                
                hm_html = render_trading_heatmap(df_trades, curr_symbol, hm_filter, initial_balance)
                st.markdown(hm_html, unsafe_allow_html=True)

            with col_top_trades:
                if "top_trades_mode" not in st.session_state:
                    st.session_state["top_trades_mode"] = "winners"

                is_win_mode = (st.session_state["top_trades_mode"] == "winners")
                btn_win_type = "primary" if is_win_mode else "secondary"
                btn_loss_type = "primary" if not is_win_mode else "secondary"

                with st.container(border=True):
                    st.markdown('<div style="font-size: 19px; font-weight: 800; color: #ffffff; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;"><span>🏆</span> Top Trades</div>', unsafe_allow_html=True)
                    
                    t_col1, t_col2 = st.columns(2)
                    with t_col1:
                        if st.button("Top Winners", key="btn_top_win", use_container_width=True, type=btn_win_type):
                            st.session_state["top_trades_mode"] = "winners"
                            st.rerun()
                    with t_col2:
                        if st.button("Top Losers", key="btn_top_loss", use_container_width=True, type=btn_loss_type):
                            st.session_state["top_trades_mode"] = "losers"
                            st.rerun()
                    
                    st.markdown('<div style="border-top: 1px solid rgba(255, 255, 255, 0.12); margin: 16px 0 8px 0;"></div>', unsafe_allow_html=True)
                    st.markdown(render_top_trades_list(df_trades, curr_symbol, st.session_state["top_trades_mode"]), unsafe_allow_html=True)

            # ==========================================
            # SECCIÓN 2: 4 PANELES DE ESTADO (LIMPIO Y SIN DESBORDAMIENTOS)
            # ==========================================
            st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)
            s_col1, s_col2, s_col3, s_col4 = st.columns(4)
            
            with s_col1:
                emoji_res = "😐"
                label_res = "Neutral"
                if not df_trades.empty and 'emotion' in df_trades.columns:
                    seven_days_ago = datetime.now() - timedelta(days=7)
                    recent_trades = df_trades[df_trades['date_time'] >= seven_days_ago]
                    if not recent_trades.empty and 'emotion' in recent_trades.columns:
                        top_emotion = recent_trades['emotion'].mode()
                        if not top_emotion.empty:
                            full_emo = top_emotion[0]
                            parts = full_emo.split(" ")
                            label_res = parts[0]
                            emoji_res = parts[1] if len(parts) > 1 else "🧠"

                st.markdown(f'''<div class="status-panel-card">
<div class="status-header">
<span>ESTADO EMOCIONAL</span>
<span>🧠</span>
</div>
<div class="status-body-center">
<div style="font-size: 34px; margin-bottom: 2px; filter: drop-shadow(0 0 8px rgba(0,210,255,0.25));">{emoji_res}</div>
<div style="color: #ffffff; font-size: 15px; font-weight: 800; letter-spacing: 0.5px;">{label_res}</div>
</div>
<div style="text-align: center; color: #64748b; font-size: 10px; font-weight: 600; letter-spacing: 0.5px; border-top: 1px solid rgba(30,41,59,0.5); padding-top: 6px;">
PROMEDIO 7 DÍAS
</div>
</div>''', unsafe_allow_html=True)

            with s_col2:
                conf_label = "Alto 🔥"
                conf_color = "#00ffa3"
                if not df_trades.empty and 'confidence' in df_trades.columns:
                    seven_days_ago = datetime.now() - timedelta(days=7)
                    recent_trades = df_trades[df_trades['date_time'] >= seven_days_ago]
                    if not recent_trades.empty:
                        top_conf = recent_trades['confidence'].mode()
                        if not top_conf.empty:
                            conf_label = top_conf[0]
                            if "Alto" in conf_label: conf_color = "#00ffa3"
                            elif "Medio" in conf_label: conf_color = "#ffb800"
                            else: conf_color = "#ff3366"

                st.markdown(f'''<div class="status-panel-card">
<div class="status-header">
<span>NIVEL DE CONFIANZA</span>
<span>🎯</span>
</div>
<div class="status-body-center">
<div style="font-size: 34px; margin-bottom: 2px; filter: drop-shadow(0 0 8px {conf_color}40);">🛡️</div>
<div style="color: {conf_color}; font-size: 15px; font-weight: 800; letter-spacing: 0.5px;">{conf_label}</div>
</div>
<div style="text-align: center; color: #64748b; font-size: 10px; font-weight: 600; letter-spacing: 0.5px; border-top: 1px solid rgba(30,41,59,0.5); padding-top: 6px;">
PSICO-TRADING SCORE
</div>
</div>''', unsafe_allow_html=True)

            with s_col3:
                # CONTROL DE HORARIO: CIERRE VIERNES 17:00 NY -> APERTURA DOMINGO 17:00 NY
                now_utc = datetime.now(timezone.utc)
                now_ny = now_utc.astimezone(timezone(timedelta(hours=-4)))
                ny_weekday = now_ny.weekday() # 4=Viernes, 5=Sábado, 6=Domingo
                ny_hour = now_ny.hour

                is_market_closed_weekend = False
                if ny_weekday == 4 and ny_hour >= 17:
                    is_market_closed_weekend = True
                elif ny_weekday == 5:
                    is_market_closed_weekend = True
                elif ny_weekday == 6 and ny_hour < 17:
                    is_market_closed_weekend = True

                utc_hour = now_utc.hour
                tokyo_active = (0 <= utc_hour < 9) and not is_market_closed_weekend
                london_active = (8 <= utc_hour < 16) and not is_market_closed_weekend
                ny_active = (13 <= utc_hour < 22) and not is_market_closed_weekend

                def build_session_row(name, is_active):
                    cls = "active" if is_active else ""
                    dot = "dot-live" if is_active else "dot-closed"
                    color = "#00ffa3" if is_active else "#64748b"
                    status_text = "ACTIVA" if is_active else "OFF"
                    return f'<div class="session-item-row {cls}"><span style="color: #ffffff; font-size: 11px; font-weight: 700;">{name}</span><span><span class="{dot}"></span> <span style="color: {color}; font-size: 9.5px; font-weight: 800; letter-spacing: 0.5px; margin-left: 3px;">{status_text}</span></span></div>'

                st.markdown(f'''<div class="status-panel-card">
<div class="status-header">
<span>SESIONES DE TRADING</span>
<span>🌐</span>
</div>
<div style="display: flex; flex-direction: column; justify-content: center; flex-grow: 1; padding: 6px 0;">
{build_session_row("Londres", london_active)}
{build_session_row("New York", ny_active)}
{build_session_row("Tokio", tokyo_active)}
</div>
</div>''', unsafe_allow_html=True)

            with s_col4:
                last_obs = "Sin notas recientes registradas."
                if not df_trades.empty and 'observation' in df_trades.columns:
                    valid_obs = df_trades[df_trades['observation'].notnull() & (df_trades['observation'] != '')]
                    if not valid_obs.empty:
                        last_obs = valid_obs.iloc[-1]['observation']

                st.markdown(f'''<div class="status-panel-card">
<div class="status-header">
<span>BITÁCORA CUÁNTICA</span>
<span>📝</span>
</div>
<div style="display: flex; align-items: center; flex-grow: 1; padding: 4px 0;">
<div style="background: rgba(5, 11, 20, 0.7); border: 1px solid #1e293b; border-left: 3px solid #d200ff; border-radius: 10px; padding: 10px 12px; width: 100%; height: 75px; overflow-y: auto; box-shadow: inset 0 2px 6px rgba(0,0,0,0.5);">
<div style="color: #cbd5e1; font-size: 11.5px; font-style: italic; line-height: 1.4;">"{last_obs}"</div>
</div>
</div>
<div style="text-align: right; color: #64748b; font-size: 9.5px; font-weight: 700; letter-spacing: 0.5px;">
ÚLTIMO REGISTRO
</div>
</div>''', unsafe_allow_html=True)

            # ==========================================
            # SECCIÓN 3: GRÁFICOS INFERIORES (BLOQUEADOS Y ESTÁTICOS)
            # ==========================================
            st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
            col_chart1, col_chart2, col_chart3 = st.columns(3)

            with col_chart1:
                with st.container(border=True):
                    pct_growth = (net_profit / initial_balance * 100) if initial_balance > 0 else 0.0
                    sign_growth = "+" if net_profit >= 0 else ""
                    
                    st.markdown(f'''<div style="display: flex; justify-content: space-between; align-items: center; padding-bottom: 8px; border-bottom: 1px solid #1e293b; margin-bottom: 12px;">
<div>
<div style="font-size: 14px; font-weight: bold; color: #ffffff; display: flex; align-items: center; gap: 6px;">📁 Crecimiento Acumulado</div>
<div style="font-size: 10px; color: #64748b;">Curva de Capital Cuántica</div>
</div>
<div style="text-align: right; background: rgba(0, 255, 163, 0.08); border: 1px solid rgba(0, 255, 163, 0.3); padding: 4px 10px; border-radius: 8px;">
<span style="font-size: 14px; font-weight: 800; color: #00ffa3;">{sign_growth}{curr_symbol}{net_profit:,.2f}</span>
<span style="font-size: 10px; font-weight: bold; color: #00d2ff; margin-left: 4px;">{sign_growth}{pct_growth:.1f}%</span>
</div>
</div>''', unsafe_allow_html=True)
                    
                    if total_trades > 0:
                        df_trades['Trade #'] = range(1, len(df_trades) + 1)
                        
                        fig_growth = go.Figure()
                        fig_growth.add_trace(go.Scatter(
                            x=df_trades['Trade #'],
                            y=df_trades['equity'],
                            mode='lines+markers',
                            name='Capital',
                            line=dict(color='#00d2ff', width=3, shape='spline', smoothing=1.3),
                            fill='tozeroy',
                            fillcolor='rgba(0, 210, 255, 0.12)',
                            marker=dict(size=6, color='#00ffa3', line=dict(color='#ffffff', width=1.5)),
                            hovertemplate=f"<b>Trade #%{{x}}</b><br>Capital: <b>%{{y:,.2f}} {curr_symbol}</b><extra></extra>"
                        ))
                        
                        fig_growth.update_layout(
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            font=dict(color='#94a3b8', size=10),
                            margin=dict(l=5, r=5, t=5, b=5),
                            height=205,
                            dragmode=False,
                            xaxis=dict(showgrid=True, gridcolor='#101d36', zeroline=False, showline=True, linecolor='#1e293b', fixedrange=True),
                            yaxis=dict(showgrid=True, gridcolor='#101d36', zeroline=False, showline=True, linecolor='#1e293b', tickprefix=curr_symbol, fixedrange=True),
                            hovermode='x unified'
                        )
                        st.plotly_chart(fig_growth, width='stretch', config={'displayModeBar': False, 'staticPlot': False, 'scrollZoom': False})
                    else:
                        st.markdown('<div style="text-align: center; color: #64748b; padding: 60px;">Sin datos de crecimiento disponibles.</div>', unsafe_allow_html=True)

            with col_chart2:
                with st.container(border=True):
                    green_days_count = 0
                    red_days_count = 0
                    best_day_val = 0.0
                    best_day_date = "N/A"
                    worst_day_val = 0.0
                    worst_day_date = "Sin pérdidas"

                    if total_trades > 0:
                        df_daily = df_trades.copy()
                        df_daily['day_str'] = df_daily['date_time'].dt.strftime('%d %b')
                        df_daily['day_date'] = df_daily['date_time'].dt.date
                        
                        df_grouped = df_daily.groupby(['day_date', 'day_str'], as_index=False)['pnl'].sum()
                        
                        green_days_count = len(df_grouped[df_grouped['pnl'] > 0])
                        red_days_count = len(df_grouped[df_grouped['pnl'] < 0])
                        
                        if not df_grouped.empty:
                            best_row = df_grouped.loc[df_grouped['pnl'].idxmax()]
                            best_day_val = best_row['pnl']
                            best_day_date = best_row['day_date'].strftime('%d %b, %Y')
                            
                            df_negative = df_grouped[df_grouped['pnl'] < 0]
                            if not df_negative.empty:
                                worst_row = df_negative.loc[df_negative['pnl'].idxmin()]
                                worst_day_val = worst_row['pnl']
                                worst_day_date = worst_row['day_date'].strftime('%d %b, %Y')
                            else:
                                worst_day_val = 0.0
                                worst_day_date = "Sin pérdidas"

                    st.markdown(f'''<div style="display: flex; justify-content: space-between; align-items: center; padding-bottom: 8px; border-bottom: 1px solid #1e293b; margin-bottom: 10px;">
<div>
<div style="font-size: 14px; font-weight: bold; color: #ffffff; display: flex; align-items: center; gap: 6px;">📊 P&L Diario</div>
<div style="font-size: 10px; color: #64748b;">Rendimiento Cuántico Diario</div>
</div>
<div style="display: flex; gap: 8px; align-items: center;">
<span style="background: rgba(0, 255, 163, 0.1); border: 1px solid rgba(0, 255, 163, 0.3); color: #00ffa3; font-size: 10px; font-weight: bold; padding: 2px 8px; border-radius: 6px;">🟢 {green_days_count}D</span>
<span style="background: rgba(255, 51, 102, 0.1); border: 1px solid rgba(255, 51, 102, 0.3); color: #ff3366; font-size: 10px; font-weight: bold; padding: 2px 8px; border-radius: 6px;">🔴 {red_days_count}D</span>
</div>
</div>''', unsafe_allow_html=True)

                    if total_trades > 0 and not df_grouped.empty:
                        colors = ['#00ffa3' if val >= 0 else '#ff3366' for val in df_grouped['pnl']]
                        
                        fig_daily = go.Figure(data=[go.Bar(
                            x=df_grouped['day_str'],
                            y=df_grouped['pnl'],
                            marker=dict(color=colors, line=dict(color='rgba(255, 255, 255, 0.25)', width=1.5), opacity=0.92),
                            width=[0.35] * len(df_grouped),
                            hovertemplate=f"<b style='color:#00d2ff;'>%{{x}}</b><br>P&L: <b>%{{y:+,.2f}} {curr_symbol}</b><extra></extra>"
                        )])
                        
                        fig_daily.update_layout(
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            font=dict(color='#94a3b8', size=10),
                            margin=dict(l=5, r=5, t=5, b=0),
                            height=95,
                            dragmode=False,
                            xaxis=dict(type='category', showgrid=False, linecolor='#1e293b', tickfont=dict(color='#94a3b8', size=10), fixedrange=True),
                            yaxis=dict(showgrid=True, gridcolor='#101d36', zeroline=True, zerolinecolor='#334155', zerolinewidth=1.5, linecolor='#1e293b', tickprefix=curr_symbol, tickfont=dict(color='#94a3b8', size=10), fixedrange=True)
                        )
                        st.plotly_chart(fig_daily, width='stretch', config={'displayModeBar': False, 'staticPlot': False, 'scrollZoom': False})
                    else:
                        st.markdown('<div style="text-align: center; color: #64748b; padding: 35px;">Sin datos diarios disponibles.</div>', unsafe_allow_html=True)

                    sub_c1, sub_c2 = st.columns(2)
                    sign_worst = "+" if worst_day_val > 0 else ""
                    color_worst = "#00ffa3" if worst_day_val > 0 else "#ff3366" if worst_day_val < 0 else "#94a3b8"
                    display_worst_val = f"{sign_worst}{curr_symbol}{worst_day_val:,.2f}" if worst_day_val != 0.0 else f"{curr_symbol}0.00"
                    
                    with sub_c1:
                        st.markdown(f'''<div class="best-worst-card best-card">
<div style="font-size: 9px; font-weight: 800; color: #64748b; letter-spacing: 1.5px; text-transform: uppercase;">MEJOR DÍA</div>
<div style="font-size: 15px; font-weight: 800; color: #00ffa3; margin-top: 2px;">+{curr_symbol}{best_day_val:,.2f}</div>
<div style="font-size: 9px; color: #94a3b8; margin-top: 1px;">{best_day_date}</div>
</div>''', unsafe_allow_html=True)
                    with sub_c2:
                        st.markdown(f'''<div class="best-worst-card worst-card">
<div style="font-size: 9px; font-weight: 800; color: #64748b; letter-spacing: 1.5px; text-transform: uppercase;">PEOR DÍA</div>
<div style="font-size: 15px; font-weight: 800; color: {color_worst}; margin-top: 2px;">{display_worst_val}</div>
<div style="font-size: 9px; color: #94a3b8; margin-top: 1px;">{worst_day_date}</div>
</div>''', unsafe_allow_html=True)
                    
                    st.markdown("<div style='margin-bottom: 6px;'></div>", unsafe_allow_html=True)

            with col_chart3:
                with st.container(border=True):
                    st.markdown('''<div style="display: flex; justify-content: space-between; align-items: center; padding-bottom: 8px; border-bottom: 1px solid #1e293b; margin-bottom: 6px;">
<div>
<div style="font-size: 14px; font-weight: bold; color: #ffffff; display: flex; align-items: center; gap: 6px;">🍩 Ratio de Impacto P&L</div>
<div style="font-size: 10px; color: #64748b;">Ganadas vs Pérdidas</div>
</div>
</div>''', unsafe_allow_html=True)

                    if total_trades > 0:
                        gross_win = float(df_trades[df_trades['pnl'] > 0]['pnl'].sum())
                        gross_loss = float(abs(df_trades[df_trades['pnl'] < 0]['pnl'].sum()))

                        labels = ['Ganadas', 'Pérdidas']
                        values = [gross_win, gross_loss]
                        colors = ['#00ffa3', '#ff3366']

                        net_color = "#00ffa3" if net_profit >= 0 else "#ff3366"
                        sign_net = "+" if net_profit >= 0 else ""

                        fig_donut = go.Figure(data=[go.Pie(
                            labels=labels,
                            values=values,
                            hole=0.68,
                            sort=False,
                            direction='clockwise',
                            marker=dict(colors=colors, line=dict(color='#070d19', width=2.5)),
                            textinfo='percent',
                            textposition='outside',
                            textfont=dict(color='#cbd5e1', size=11, family='sans-serif'),
                            hovertemplate=f"<b>%{{label}}</b><br>Monto: <b>{curr_symbol}%{{value:,.2f}}</b><br>Ratio: <b>%{{percent}}</b><extra></extra>",
                            domain=dict(x=[0.05, 0.95], y=[0.16, 0.98])
                        )])

                        fig_donut.update_layout(
                            showlegend=True,
                            legend=dict(orientation="h", yanchor="top", y=-0.02, xanchor="center", x=0.5, font=dict(color="#cbd5e1", size=11)),
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            margin=dict(l=30, r=30, t=10, b=30),
                            height=210,
                            annotations=[dict(
                                text=f"<b style='color:{net_color}; font-size:10px; text-shadow:0 0 6px rgba(0,255,163,0.3);'>{sign_net}{curr_symbol}{net_profit:,.2f}</b><br><span style='color:#64748b; font-size:8px; font-weight:700; letter-spacing:1px;'>NETO</span>",
                                x=0.5, y=0.57, showarrow=False, font=dict(size=10, color="#ffffff")
                            )]
                        )
                        st.plotly_chart(fig_donut, width='stretch', config={'displayModeBar': False, 'staticPlot': False, 'scrollZoom': False})
                    else:
                        st.markdown('<div style="text-align: center; color: #64748b; padding: 60px;">Sin datos de ratio disponibles.</div>', unsafe_allow_html=True)
                    
                    st.markdown("<div style='margin-bottom: 6px;'></div>", unsafe_allow_html=True)

            # ==========================================
            # REGISTRO DE OPERACIONES Y FORMULARIO
            # ==========================================
            st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
            with st.expander("⚡ REGISTRAR NUEVO TRADE", expanded=True):
                st.markdown(f'<p style="color: #00d2ff; font-size: 12px; font-weight: 700; letter-spacing: 1.5px; margin-bottom: 20px; text-shadow: 0 0 10px rgba(0,210,255,0.3);">⚡ MÓDULO DE EJECUCIÓN CUÁNTICA (Moneda: {account_currency})</p>', unsafe_allow_html=True)
                
                default_trade_amt = 50000.0 if "COL$" in curr_symbol else 10.0
                step_trade_amt = 1000.0 if "COL$" in curr_symbol else 1.0
                fmt_trade_amt = "%.0f" if "COL$" in curr_symbol else "%.2f"

                with st.form("trade_form", clear_on_submit=True):
                    c1, c2, c3, c4 = st.columns(4)
                    with c1:
                        market = st.selectbox("🌐 Mercado", ["Opciones Binarias", "Forex"])
                        asset = st.text_input("💎 Activo (Ej. EURUSD)").upper()
                        session = st.selectbox("🌍 Sesión", ["New York", "Londres", "Sídney", "Tokio"])
                    with c2:
                        direction = st.selectbox("📈 Dirección", ["CALL / BUY 🟢", "PUT / SELL 🔴"])
                        amount = st.number_input(f"💵 Inversión / Lote ({curr_symbol})", min_value=0.1, value=default_trade_amt, step=step_trade_amt, format=fmt_trade_amt)
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
                            active_conn = get_active_connection()
                            with active_conn.cursor() as cur:
                                cur.execute('''INSERT INTO trades (account_id, date_time, market, asset, direction, amount, result, pnl, emotion, confidence, session, observation) 
                                             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''', 
                                          (selected_acc_id, dt_string, market, asset, direction, amount, result, pnl_calc, emotion, confidence, session, observation))
                                active_conn.commit()
                            st.success(f"✅ Trade registrado con éxito! PnL: {pnl_calc:+,.2f} {curr_symbol}")
                            time.sleep(0.5)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error guardando en la BD: {e}")

            # ==========================================
            # HISTORIAL DE OPERACIONES
            # ==========================================
            st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
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
                    
                    st.markdown('<div style="color: #ffffff; font-size: 16px; font-weight: bold; margin-bottom: 12px;">📊 Tabla Analítica General</div>', unsafe_allow_html=True)
                    st.markdown(render_analytics_table(df_filtered, curr_symbol), unsafe_allow_html=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    st.markdown('<div style="color: #ffffff; font-size: 16px; font-weight: bold; margin-bottom: 12px;">🔍 Detallado Cuántico de Ejecuciones</div>', unsafe_allow_html=True)
                    if not df_filtered.empty:
                        for idx, row in df_filtered.iterrows():
                            pnl_val = float(row['pnl'])
                            res_color = "#00ffa3" if pnl_val > 0 else "#ff3366" if pnl_val < 0 else "#64748b"
                            border_color = "#00ffa3" if pnl_val > 0 else "#ff3366" if pnl_val < 0 else "#64748b"
                            sign_pnl = "+" if pnl_val > 0 else ""
                            obs_text = row.get('observation', '')
                            amt_val = row['amount']
                            res_val = row['result']
                            date_str = pd.to_datetime(row['date_time']).strftime('%Y-%m-%d %H:%M:%S')
                            
                            obs_html = f'<div style="margin-top: 6px; color: #d200ff; font-size: 13px; font-style: italic;">📝 Nota: {obs_text}</div>' if obs_text else ''
                            
                            card_html = f'<div class="trade-quantum-card" style="border-left: 4px solid {border_color};"><div style="flex-grow: 1;"><div style="display: flex; align-items: center; gap: 10px; margin-bottom: 2px;"><span style="color: #00d2ff; font-size: 16px; font-weight: 800; letter-spacing: 0.5px;">💎 {row["asset"]}</span><span style="color: #64748b; font-size: 13px; font-weight: bold;">|</span><span style="color: #e2e8f0; font-size: 14px; font-weight: 600;">{row["market"]}</span><span style="color: #64748b; font-size: 12px; margin-left: 6px;">📅 {date_str}</span></div><div style="flex-wrap: wrap; gap: 8px; margin-top: 6px; align-items: center; display: flex;"><span class="trade-badge">Dir: <b style="color:#ffffff;">{row["direction"]}</b></span><span class="trade-badge">Sesión: <b style="color:#ffffff;">{row.get("session", "N/A")}</b></span><span class="trade-badge">Confianza: <b style="color:#ffffff;">{row.get("confidence", "N/A")}</b></span><span class="trade-badge">Op: <b style="color:#ffffff;">{row.get("emotion", "N/A")}</b></span></div>{obs_html}</div><div style="text-align: right; min-width: 140px; margin-left: 15px;"><div style="color: {res_color}; font-size: 20px; font-weight: 800; text-shadow: 0 0 10px {res_color}40;">{sign_pnl}{curr_symbol}{pnl_val:,.2f}</div><div style="color: #94a3b8; font-size: 12.5px; font-weight: 600; margin-top: 2px;">Inv: {curr_symbol}{amt_val:,.2f} | <span style="color: {res_color};">{res_val}</span></div></div></div>'
                            
                            st.markdown(card_html, unsafe_allow_html=True)
                    else:
                        st.markdown('<div style="color: #64748b; padding: 15px; text-align: center;">Sin registros detallados para mostrar.</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div style="text-align: center; color: #64748b; padding: 30px;">No hay operaciones registradas en esta cuenta.</div>', unsafe_allow_html=True)
