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

# --- DIZAJNI DHE STILIZIMI (CSS) ---
st.markdown("""
    <style>
    .site-header {
        background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 100%);
        padding: 25px 30px;
        border-radius: 16px;
        color: white;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 25px;
        box-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.25);
    }
    .header-logo {
        font-size: 28px;
        font-weight: 800;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .header-tagline {
        font-size: 14px;
        opacity: 0.9;
        margin-top: 5px;
    }
    .card-box {
        background-color: #ffffff;
        border: 1px solid #E2E8F0;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
        margin-bottom: 24px;
        height: 100%;
        transition: all 0.2s ease-in-out;
    }
    .card-box:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 20px -3px rgba(37, 99, 235, 0.1);
        border-color: #93C5FD;
    }
    .badge-automjete { background-color: #EFF6FF; color: #1D4ED8; padding: 4px 10px; border-radius: 20px; font-weight: 600; font-size: 12px; border: 1px solid #BFDBFE; display: inline-block; margin-bottom: 8px;}
    .badge-pasuri { background-color: #F0FDF4; color: #15803D; padding: 4px 10px; border-radius: 20px; font-weight: 600; font-size: 12px; border: 1px solid #BBF7D0; display: inline-block; margin-bottom: 8px;}
    .badge-elektronikë { background-color: #FAF5FF; color: #7E22CE; padding: 4px 10px; border-radius: 20px; font-weight: 600; font-size: 12px; border: 1px solid #E9D5FF; display: inline-block; margin-bottom: 8px;}
    .badge-tjetër { background-color: #F8FAFC; color: #475569; padding: 4px 10px; border-radius: 20px; font-weight: 600; font-size: 12px; border: 1px solid #E2E8F0; display: inline-block; margin-bottom: 8px;}
    
    .site-footer {
        background-color: #0F172A;
        color: #94A3B8;
        padding: 40px 30px 20px 30px;
        border-radius: 16px;
        margin-top: 60px;
    }
    .footer-title {
        color: #FFFFFF;
        font-size: 16px;
        font-weight: 700;
        margin-bottom: 12px;
    }
    .footer-text {
        font-size: 13px;
        line-height: 1.6;
    }
    .footer-bottom {
        border-top: 1px solid #1E293B;
        margin-top: 30px;
        padding-top: 15px;
        text-align: center;
        font-size: 13px;
        color: #64748B;
    }
    </style>
""", unsafe_allow_html=True)

def init_db():
    conn = sqlite3.connect('njoftime.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS perdoruesit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            email TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS njoftime (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            perdoruesi TEXT,
            kategoria TEXT,
            titulli TEXT,
            pershkrimi TEXT,
            cmimi REAL,
            kontakti TEXT,
            lokacioni TEXT,
            detaje_specifike TEXT,
            data TEXT,
            foto_paths TEXT,
            FOREIGN KEY(user_id) REFERENCES perdoruesit(id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- SESSION STATES ---
if 'user_logged_in' not in st.session_state:
    st.session_state['user_logged_in'] = False
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = None
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
    cursor.execute("SELECT id, username FROM perdoruesit WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    if user:
        return user[0], user[1]
    return None, None

def shto_njoftim(user_id, perdoruesi, kategoria, titulli, pershkrimi, cmimi, kontakti, lokacioni, detaje_specifike, foto_paths_str):
    conn = sqlite3.connect('njoftime.db')
    cursor = conn.cursor()
    data_aktuale = datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute('''
        INSERT INTO njoftime (user_id, perdoruesi, kategoria, titulli, pershkrimi, cmimi, kontakti, lokacioni, detaje_specifike, data, foto_paths)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, perdoruesi, kategoria, titulli, pershkrimi, cmimi, kontakti, lokacioni, detaje_specifike, data_aktuale, foto_paths_str))
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

def merr_perdoruesit():
    conn = sqlite3.connect('njoftime.db')
    df = pd.read_sql_query("SELECT id, username, email FROM perdoruesit ORDER BY id DESC", conn)
    conn.close()
    return df

def merr_njoftimet_dhe_perdoruesit():
    conn = sqlite3.connect('njoftime.db')
    query = '''
        SELECT 
            n.id AS njoftim_id,
            p.id AS perdorues_id_db,
            p.username AS emri_perdoruesit,
            p.email AS email_perdoruesi,
            n.kategoria,
            n.titulli,
            n.cmimi,
            n.lokacioni,
            n.data
        FROM njoftime n
        LEFT JOIN perdoruesit p ON n.user_id = p.id
        ORDER BY n.id DESC
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

query_params = st.query_params
is_admin_route = query_params.get("page") == "admin"

# --- HEADER I BUKUR DHE PROFESIONAL ---
st.markdown("""
    <div class="site-header">
        <div>
            <div class="header-logo">🛍️ Marketplace Shqipëri</div>
            <div class="header-tagline">Destinacioni kryesor për njoftimet tuaja në Tiranë dhe mbarë Shqipërinë</div>
        </div>
        <div style="text-align: right; font-size: 13px; opacity: 0.9;">
            <b>Qytetet:</b> Tiranë, Durrës, Vlorë, Shkodër...
        </div>
    </div>
""", unsafe_allow_html=True)

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
                    st.error("Kredenciale të gabuara!")
    else:
        st.success("Admin i kyçur me sukses.")
        if st.button("Dil nga Admini"):
            st.session_state['admin_logged_in'] = False
            st.rerun()
            
        st.divider()
        
        # 1. Shfaqja e të gjithë përdoruesve të regjistruar
        st.write("### 👤 Përdoruesit e Regjistruar në Platformë")
        df_perdoruesit = merr_perdoruesit()
        if not df_perdoruesit.empty:
            st.dataframe(df_perdoruesit, use_container_width=True)
        else:
            st.info("Nuk ka ende përdorues të regjistruar.")
            
        st.divider()
        
        # 2. Shfaqja e njoftimeve dhe përdoruesve me JOIN
        st.write("### 📋 Njoftimet dhe Përdoruesit që i kanë postuar")
        df_kombinuar = merr_njoftimet_dhe_perdoruesit()
        if not df_kombinuar.empty:
            st.dataframe(df_kombinuar, use_container_width=True)
        else:
            st.info("Nuk ka ende njoftime të postuara.")
            
        st.divider()
        st.subheader("Fshij Njoftimet Sipas ID-së")
        df_all = merr_njoftimet()
        for idx, row in df_all.iterrows():
            if st.button(f"Fshi njoftimin #{row['id']} - {row['titulli']}", key=f"del_{row['id']}"):
                fshi_njoftimin(row['id'], row['foto_paths'])
                st.success(f"Njoftimi #{row['id']} u fshi me sukses!")
                st.rerun()
else:
    # --- MENAXHIMI I LLOGARISË ---
    col_stat1, col_stat2 = st.columns([3, 2])
    with col_stat1:
        if st.session_state['user_logged_in']:
            st.success(f"Mirë se vajte, **{st.session_state['username']}**! 🎉")
        else:
            st.info("Nuk je i kyçur. Hyr në llogari ose regjistrohu për të postuar njoftime.")
    with col_stat2:
        if st.session_state['user_logged_in']:
            if st.button("Dil nga Llogaria (Logout)"):
                st.session_state['user_logged_in'] = False
                st.session_state['user_id'] = None
                st.session_state['username'] = ""
                st.rerun()

    if not st.session_state['user_logged_in']:
        with st.expander("🔑 Kliko këtu për të hyrë ose krijuar llogari", expanded=False):
            t1, t2 = st.tabs(["Kyçu (Login)", "Regjistrohu (Register)"])
            with t1:
                with st.form("l_form"):
                    u = st.text_input("Username")
                    p = st.text_input("Password", type="password")
                    if st.form_submit_button("Hyr në llogari"):
                        u_id, u_name = verifiko_user(u, p)
                        if u_id is not None:
                            st.session_state['user_logged_in'] = True
                            st.session_state['user_id'] = u_id
                            st.session_state['username'] = u_name
                            st.rerun()
                        else:
                            st.error("Username ose fjalëkalim i gabuar!")
            with t2:
                with st.form("r_form"):
                    ru = st.text_input("Username i ri")
                    re = st.text_input("Email")
                    rp = st.text_input("Fjalëkalim i ri", type="password")
                    if st.form_submit_button("Krijo llogari"):
                        if regjistro_user(ru, rp, re):
                            st.success("Regjistrimi u krye me sukses! Tani mund të kyçesh tek tab-i tjetër.")
                        else:
                            st.error("Ky username ose email ekziston tashmë!")

    st.divider()
    tab1, tab2 = st.tabs(["📋 Shiko Njoftimet Aktive", "➕ Shto Njoftim të Ri"])

    with tab1:
        df = merr_njoftimet()
        if not df.empty:
            st.sidebar.header("🔍 Filtrat e Kërkimit")
            kat = ["Të gjitha"] + list(df['kategoria'].dropna().unique())
            zkat = st.sidebar.selectbox("Kategoria", kat)
            
            lok = ["Të gjitha"] + list(df['lokacioni'].dropna().unique())
            zlok = st.sidebar.selectbox("Qyteti", lok)
            
            max_c_db = float(df['cmimi'].max()) if not df['cmimi'].dropna().empty else 10000.0
            min_val, max_val = st.sidebar.slider("Filtro sipas Çmimit (€)", 0.0, max(max_c_db, 1000.0), (0.0, max(max_c_db, 1000.0)))
            
            fjalet = st.sidebar.text_input("Kërko fjalë kyçe")
            
            f_df = df.copy()
            if zkat != "Të gjitha":
                f_df = f_df[f_df['kategoria'] == zkat]
            if zlok != "Të gjitha":
                f_df = f_df[f_df['lokacioni'] == zlok]
                
            f_df = f_df[(f_df['cmimi'] >= min_val) & (f_df['cmimi'] <= max_val)]
            
            if fjalet:
                f_df = f_df[
                    f_df['titulli'].str.contains(fjalet, case=False, na=False) |
                    f_df['pershkrimi'].str.contains(fjalet, case=False, na=False)
                ]
                
            st.write(f"**Gjithsej njoftime të gjetura:** {len(f_df)}")
            st.write("")
            
            njoftime_list = f_df.to_dict('records')
            for i in range(0, len(njoftime_list), 2):
                col1, col2 = st.columns(2)
                
                with col1:
                    row = njoftime_list[i]
                    st.markdown('<div class="card-box">', unsafe_allow_html=True)
                    
                    foto_paths = row['foto_paths'].split(",") if row['foto_paths'] else []
                    valid_fotos = [p for p in foto_paths if p and os.path.exists(p)]
                    if valid_fotos:
                        sel_img = st.selectbox("Foto", valid_fotos, key=f"img_{row['id']}")
                        try:
                            st.image(Image.open(sel_img), use_container_width=True)
                        except:
                            st.info("[Foto nuk u ngarkua dot]")
                    else:
                        st.info("🖼️ Pa foto")
                        
                    cat = row['kategoria']
                    badge_cls = "badge-tjetër"
                    if cat == "Automjete": badge_cls = "badge-automjete"
                    elif cat == "Pasuri të Paluajtshme": badge_cls = "badge-pasuri"
                    elif cat == "Elektronikë": badge_cls = "badge-elektronikë"
                    
                    st.markdown(f'<span class="{badge_cls}">{cat}</span>', unsafe_allow_html=True)
                    st.markdown(f"### {row['titulli']}")
                    st.write(row['pershkrimi'][:100] + "..." if len(row['pershkrimi']) > 100 else row['pershkrimi'])
                    
                    if row['cmimi'] > 0:
                        st.success(f"Çmimi: {row['cmimi']} €")
                    else:
                        st.info("Çmimi: Me Marrëveshje")
                        
                    with st.expander("📞 Shiko Kontaktin & Detajet"):
                        st.write(f"**Përshkrimi i plotë:** {row['pershkrimi']}")
                        if row['detaje_specifike']:
                            st.info(f"**Specifikat:** {row['detaje_specifike']}")
                        st.caption(f"Lokacioni: {row['lokacioni']} | Tel: {row['kontakti']} | Postuar nga: {row['perdoruesi']}")
                        tel = str(row['kontakti']).strip()
                        if tel.isdigit() or tel.startswith("+"):
                            st.markdown(f"[📱 Shkruaj në WhatsApp](https://wa.me/{tel.replace('+', '')}?text=Përshëndetje, jam i interesuar për: {row['titulli']})", unsafe_allow_html=True)
                            
                    if st.session_state['user_logged_in'] and st.session_state['username'] == row['perdoruesi']:
                        if st.button("Fshi Njoftimin Tim", key=f"f_{row['id']}"):
                            fshi_njoftimin(row['id'], row['foto_paths'])
                            st.success("U fshi!")
                            st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                if i + 1 < len(njoftime_list):
                    with col2:
                        row2 = njoftime_list[i + 1]
                        st.markdown('<div class="card-box">', unsafe_allow_html=True)
                        
                        foto_paths2 = row2['foto_paths'].split(",") if row2['foto_paths'] else []
                        valid_fotos2 = [p for p in foto_paths2 if p and os.path.exists(p)]
                        if valid_fotos2:
                            sel_img2 = st.selectbox("Foto", valid_fotos2, key=f"img2_{row2['id']}")
                            try:
                                st.image(Image.open(sel_img2), use_container_width=True)
                            except:
                                st.info("[Foto nuk u ngarkua dot]")
                        else:
                            st.info("🖼️ Pa foto")
                            
                        cat2 = row2['kategoria']
                        badge_cls2 = "badge-tjetër"
                        if cat2 == "Automjete": badge_cls2 = "badge-automjete"
                        elif cat2 == "Pasuri të Paluajtshme": badge_cls2 = "badge-pasuri"
                        elif cat2 == "Elektronikë": badge_cls2 = "badge-elektronikë"
                        
                        st.markdown(f'<span class="{badge_cls2}">{cat2}</span>', unsafe_allow_html=True)
                        st.markdown(f"### {row2['titulli']}")
                        st.write(row2['pershkrimi'][:100] + "..." if len(row2['pershkrimi']) > 100 else row2['pershkrimi'])
                        
                        if row2['cmimi'] > 0:
                            st.success(f"Çmimi: {row2['cmimi']} €")
                        else:
                            st.info("Çmimi: Me Marrëveshje")
                            
                        with st.expander("📞 Shiko Kontaktin & Detajet"):
                            st.write(f"**Përshkrimi i plotë:** {row2['pershkrimi']}")
                            if row2['detaje_specifike']:
                                st.info(f"**Specifikat:** {row2['detaje_specifike']}")
                            st.caption(f"Lokacioni: {row2['lokacioni']} | Tel: {row2['kontakti']} | Postuar nga: {row2['perdoruesi']}")
                            tel2 = str(row2['kontakti']).strip()
                            if tel2.isdigit() or tel2.startswith("+"):
                                st.markdown(f"[📱 Shkruaj në WhatsApp](https://wa.me/{tel2.replace('+', '')}?text=Përshëndetje, jam i interesuar për: {row2['titulli']})", unsafe_allow_html=True)
                                
                        if st.session_state['user_logged_in'] and st.session_state['username'] == row2['perdoruesi']:
                            if st.button("Fshi Njoftimin Tim", key=f"f_{row2['id']}"):
                                fshi_njoftimin(row2['id'], row2['foto_paths'])
                                st.success("U fshi!")
                                st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Nuk ka asnjë njoftim të publikuar ende.")

    with tab2:
        st.subheader("Krijo Njoftim të Ri")
        if not st.session_state['user_logged_in']:
            st.warning("⚠️ Duhet të kyçesh në llogarinë tënde për të postuar një njoftim!")
        else:
            kategoria = st.selectbox("Zgjidh Kategorinë", ["Automjete", "Pasuri të Paluajtshme", "Elektronikë", "Të Tjera"])
            
            with st.form("post_form", clear_on_submit=True):
                titulli = st.text_input("Titulli i Njoftimit (p.sh. Shitet Audi A3 / Shitet Apartament 2+1)")
                pershkrimi = st.text_area("Përshkrimi i detajuar")
                
                detaje_specifike = ""
                if kategoria == "Automjete":
                    c1, c2, c3 = st.columns(3)
                    viti = c1.text_input("Viti i Prodhimit")
                    km = c2.text_input("Kilometrazhi (km)")
                    kambio = c3.selectbox("Kambio", ["Automatike", "Manuale"])
                    detaje_specifike = f"Viti: {viti} | KM: {km} | Kambio: {kambio}"
                elif kategoria == "Pasuri të Paluajtshme":
                    c1, c2 = st.columns(2)
                    sip = c1.text_input("Sipërfaqja (m²)")
                    dhoma = c2.text_input("Dhoma / Kati")
                    detaje_specifike = f"Sipërfaqja: {sip} | Detaje: {dhoma}"
                elif kategoria == "Elektronikë":
                    gjendja = st.selectbox("Gjendja", ["E re (Kuti)", "E përdorur - Shumë e mirë", "E përdorur"])
                    detaje_specifike = f"Gjendja: {gjendja}"
                    
                c_p1, c_p2 = st.columns(2)
                with c_p1:
                    cmimi = st.number_input("Çmimi (€) (Lëre 0 për Me Marrëveshje)", min_value=0.0, step=10.0)
                with c_p2:
                    lokacioni = st.selectbox("Qyteti", ["Tiranë", "Durrës", "Vlorë", "Shkodër", "Fier", "Elbasan", "Korçë", "Tjetër"])
                    
                kontakti = st.text_input("Numri i Telefonit (p.sh. 069XXXXXXX)")
                fotos = st.file_uploader("Ngarko Foton/Fotot", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
                
                if st.form_submit_button("Publiko Njoftimin Tani"):
                    if titulli and pershkrimi and kontakti:
                        foto_paths_list = []
                        if fotos:
                            for f in fotos:
                                t_str = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                                f_name = f"{t_str}_{f.name}"
                                f_path = os.path.join(UPLOAD_DIR, f_name)
                                with open(f_path, "wb") as file_out:
                                    file_out.write(f.getbuffer())
                                foto_paths_list.append(f_path)
                        
                        foto_str = ",".join(foto_paths_list)
                        shto_njoftim(
                            user_id=st.session_state['user_id'],
                            perdoruesi=st.session_state['username'],
                            kategoria=kategoria,
                            titulli=titulli,
                            pershkrimi=pershkrimi,
                            cmimi=cmimi,
                            kontakti=kontakti,
                            lokacioni=lokacioni,
                            detaje_specifike=detaje_specifike,
                            foto_paths_str=foto_str
                        )
                        st.success("Njoftimi u publikua me sukses!")
                    else:
                        st.error("Ju lutem plotësoni Titullin, Përshkrimin dhe Kontaktin.")

# --- FOOTER I BUKUR ---
st.markdown("""
    <div class="site-footer">
        <div style="display: flex; justify-content: space-between; flex-wrap: wrap; gap: 30px;">
            <div style="flex: 2; min-width: 250px;">
                <div class="footer-title">Rreth Marketplace Shqipëri</div>
                <div class="footer-text">
                    Destinacioni kryesor për njoftimet tuaja në Tiranë dhe mbarë Shqipërinë. Posto lehtësisht dhe lidhu drejtpërdrejt me blerësit ose shitësit.
                </div>
            </div>
            <div style="flex: 1; min-width: 150px;">
                <div class="footer-title">Kategoritë Kryesore</div>
                <div class="footer-text">
                    🚗 Automjete<br>
                    🏠 Pasuri të Paluajtshme<br>
                    💻 Elektronikë<br>
                    🛠️ Të Tjera
                </div>
            </div>
            <div style="flex: 1; min-width: 150px;">
                <div class="footer-title">Na Kontaktoni</div>
                <div class="footer-text">
                    📍 Tiranë, Shqipëri<br>
                    📧 info@marketplace.al<br>
                    📞 +355 69 XX XX XXX
                </div>
            </div>
        </div>
        <div class="footer-bottom">
            <b>Marketplace Shqipëri</b> &copy; 2026 | Të gjitha të drejtat e rezervuara.
        </div>
    </div>
""", unsafe_allow_html=True)