import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime
from PIL import Image

UPLOAD_DIR = "uploaded_images"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

st.set_page_config(
    page_title="Marketplace Shqipëri",
    page_icon="🛍️",
    layout="wide"
)

def init_db():
    conn = sqlite3.connect('njoftime.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS njoftime (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            perdoruesi TEXT,
            kategoria TEXT,
            titulli TEXT,
            pershkrimi TEXT,
            cmimi REAL,
            kontakti TEXT,
            lokacioni TEXT,
            detaje_specifike TEXT,
            data TEXT,
            foto_paths TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS perdoruesit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            email TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

if 'user_logged_in' not in st.session_state:
    st.session_state['user_logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ""
if 'admin_logged_in' not in st.session_state:
    st.session_state['admin_logged_in'] = False

def regjistro_user(username, password, email):
    try:
        conn = sqlite3.connect('njoftime.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO perdoruesit (username, password, email) VALUES (?, ?, ?)", (username, password, email))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def verifiko_user(username, password):
    conn = sqlite3.connect('njoftime.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM perdoruesit WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None

def shto_njoftim(perdoruesi, kategoria, titulli, pershkrimi, cmimi, kontakti, lokacioni, detaje_specifike, foto_paths_str):
    conn = sqlite3.connect('njoftime.db')
    cursor = conn.cursor()
    data_aktuale = datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute('''
        INSERT INTO njoftime (perdoruesi, kategoria, titulli, pershkrimi, cmimi, kontakti, lokacioni, detaje_specifike, data, foto_paths)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (perdoruesi, kategoria, titulli, pershkrimi, cmimi, kontakti, lokacioni, detaje_specifike, data_aktuale, foto_paths_str))
    conn.commit()
    conn.close()

def fshi_njoftimin(njoftim_id, foto_paths_str):
    conn = sqlite3.connect('njoftime.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM njoftime WHERE id = ?", (njoftim_id,))
    conn.commit()
    conn.close()
    if foto_paths_str:
        for path in foto_paths_str.split(","):
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except:
                    pass

def merr_njoftimet():
    conn = sqlite3.connect('njoftime.db')
    df = pd.read_sql_query("SELECT * FROM njoftime ORDER BY id DESC", conn)
    conn.close()
    if not df.empty and 'cmimi' in df.columns:
        df['cmimi'] = pd.to_numeric(df['cmimi'], errors='coerce').fillna(0.0)
    return df

st.title("🛍️ Marketplace Shqipëri")
st.write("Destinacioni kryesor për njoftimet tuaja në Shqipëri")

query_params = st.query_params
is_admin_route = query_params.get("page") == "admin"

if is_admin_route:
    st.subheader("🔐 Paneli i Administrimit")
    if not st.session_state['admin_logged_in']:
        with st.form("admin_login"):
            a_user = st.text_input("Username")
            a_pass = st.text_input("Password", type="password")
            if st.form_submit_button("Hyr"):
                if a_user == "admin" and a_pass == "12345":
                    st.session_state['admin_logged_in'] = True
                    st.rerun()
                else:
                    st.error("Gabim!")
    else:
        st.success("Admin i kyçur.")
        if st.button("Dil"):
            st.session_state['admin_logged_in'] = False
            st.rerun()
        df_all = merr_njoftimet()
        st.dataframe(df_all)
        for idx, row in df_all.iterrows():
            if st.button(f"Fshi njoftimin #{row['id']}", key=f"del_{row['id']}"):
                fshi_njoftimin(row['id'], row['foto_paths'])
                st.rerun()
else:
    if not st.session_state['user_logged_in']:
        with st.expander("🔑 Kyçu ose Regjistrohu", expanded=True):
            t1, t2 = st.tabs(["Kyçu", "Regjistrohu"])
            with t1:
                with st.form("l_form"):
                    u = st.text_input("Username")
                    p = st.text_input("Password", type="password")
                    if st.form_submit_button("Hyr"):
                        if verifiko_user(u, p):
                            st.session_state['user_logged_in'] = True
                            st.session_state['username'] = u
                            st.rerun()
                        else:
                            st.error("Gabim!")
            with t2:
                with st.form("r_form"):
                    ru = st.text_input("Username i ri")
                    re = st.text_input("Email")
                    rp = st.text_input("Password i ri", type="password")
                    if st.form_submit_button("Regjistrohu"):
                        if regjistro_user(ru, rp, re):
                            st.success("Sukses! Tani kyçu.")
                        else:
                            st.error("Ekziston!")
    else:
        st.success(ikt := f"Përshëndetje, {st.session_state['username']}!")
        if st.button("Dil nga Llogaria"):
            st.session_state['user_logged_in'] = False
            st.session_state['username'] = ""
            st.rerun()

    st.divider()
    tab1, tab2 = st.tabs(["Shiko Njoftimet", "Posto Njoftim"])

    with tab1:
        df = merr_njoftimet()
        if not df.empty:
            st.sidebar.header("Filtrat")
            kat = ["Të gjitha"] + list(df['kategoria'].unique())
            zkat = st.sidebar.selectbox("Kategoria", kat)
            
            lok = ["Të gjitha"] + list(df['lokacioni'].dropna().unique())
            zlok = st.sidebar.selectbox("Qyteti", lok)
            
            f_df = df.copy()
            if zkat != "Të gjitha":
                f_df = f_df[f_df['kategoria'] == zkat]
            if zlok != "Të gjitha":
                f_df = f_df[f_df['lokacioni'] == zlok]
                
            for _, row in f_df.iterrows():
                st.markdown(f"### {row['titulli']}")
                st.write(row['pershkrimi'])
                st.info(f"Kategoria: {row['kategoria']} | Çmimi: {row['cmimi']} € | Lokacioni: {row['lokacioni']} | Tel: {row['kontakti']}")
                if row['detaje_specifike']:
                    st.caption(f"Specifikat: {row['detaje_specifike']}")
                if st.session_state['user_logged_in'] and st.session_state['username'] == row['perdoruesi']:
                    if st.button("Fshi njoftimin tim", key=f"f_{row['id']}"):
                        fshi_njoftimin(row['id'], row['foto_paths'])
                        st.rerun()
                st.divider()
        else:
            st.info("Nuk ka njoftime.")

    with tab2:
        if not st.session_state['user_logged_in']:
            st.warning("Duhet të kyçesh për të postuar!")
        else:
            kategoria = st.selectbox("Kategoria", ["Automjete", "Pasuri të Paluajtshme", "Elektronikë", "Të Tjera"])
            with st.form("post_form", clear_on_submit=True):
                titulli = st.text_input("Titulli")
                pershkrimi = st.text_area("Përshkrimi")
                
                detaje = ""
                if kategoria == "Automjete":
                    viti = st.text_input("Viti")
                    km = st.text_input("Kilometrazhi")
                    kambio = st.selectbox("Kambio", ["Automatike", "Manuale"])
                    detaje = f"Viti: {viti} | KM: {km} | Kambio: {kambio}"
                elif kategoria == "Pasuri të Paluajtshme":
                    sip = st.text_input("Sipërfaqja (m²)")
                    dhoma = st.text_input("Dhoma / Kati")
                    detaje = f"Sipërfaqja: {sip} | Detaje: {dhoma}"
                    
                cmimi = st.number_input("Çmimi (€)", min_value=0.0)
                lokacioni = st.selectbox("Qyteti", ["Tiranë", "Durrës", "Vlorë", "Shkodër", "Tjetër"])
                kontakti = st.text_input("Telefoni")
                
                if st.form_submit_button("Publiko"):
                    if titulli and pershkrimi and kontakti:
                        shto_njoftim(st.session_state['username'], kategoria, titulli, pershkrimi, cmimi, kontakti, lokacioni, detaje, "")
                        st.success("U publikua!")
                    else:
                        st.error("Plotësoni fushat kryesore!")