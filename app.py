import streamlit as st
import streamlit.components.v1 as components
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

# Skript që fshin çdo element, badge ose logo të Streamlit Cloud në kohë reale
components.html("""
    <script>
    function removeElements() {
        const doc = window.parent.document;
        const selectors = [
            '#MainMenu', 'header', 'footer', 
            '[data-testid="stStatusWidget"]', 
            '[data-testid="stToolbar"]', 
            '[data-testid="stDecoration"]',
            'div[class*="viewerBadge"]',
            '.stAppToolbar',
            'a[href*="streamlit.cloud"]',
            'div:has(> a[href*="streamlit.cloud"])'
        ];
        selectors.forEach(selector => {
            doc.querySelectorAll(selector).forEach(el => el.remove());
        });
    }
    setInterval(removeElements, 100);
    </script>
""", height=0, width=0)

st.markdown("""
    <style>
    #MainMenu, header, footer, 
    [data-testid="stStatusWidget"], 
    [data-testid="stToolbar"], 
    [data-testid="stDecoration"],
    div[class*="viewerBadge"],
    .stAppToolbar {
        visibility: hidden !important;
        display: none !important;
    }
    .site-header {
        background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 100%);
        padding: 20px 30px;
        border-radius: 14px;
        color: white;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 25px;
        box-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.25);
    }
    .header-logo {
        font-size: 26px;
        font-weight: 800;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .header-tagline {
        font-size: 14px;
        opacity: 0.85;
    }
    .card-box {
        background-color: #ffffff;
        border: 1px solid #E2E8F0;
        padding: 20px;
        border-radius: 14px;
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
    .badge-automjete { background-color: #EFF6FF; color: #1D4ED8; padding: 4px 10px; border-radius: 20px; font-weight: 600; font-size: 12px; border: 1px solid #BFDBFE; }
    .badge-pasuri { background-color: #F0FDF4; color: #15803D; padding: 4px 10px; border-radius: 20px; font-weight: 600; font-size: 12px; border: 1px solid #BBF7D0; }
    .badge-elektronikë { background-color: #FAF5FF; color: #7E22CE; padding: 4px 10px; border-radius: 20px; font-weight: 600; font-size: 12px; border: 1px solid #E9D5FF; }
    .badge-punë { background-color: #FEF2F2; color: #B91C1C; padding: 4px 10px; border-radius: 20px; font-weight: 600; font-size: 12px; border: 1px solid #FECACA; }
    .badge-tjetër { background-color: #F8FAFC; color: #475569; padding: 4px 10px; border-radius: 20px; font-weight: 600; font-size: 12px; border: 1px solid #E2E8F0; }
    .site-footer {
        background-color: #0F172A;
        color: #94A3B8;
        padding: 40px 30px 20px 30px;
        border-radius: 14px;
        margin-top: 50px;
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
    
    # Krijimi i tabelës kryesore nëse nuk ekziston
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
    
    # Kontrollojmë dhe shtojmë secilën kolonë nëse mungon në tabelën ekzistuese
    cursor.execute("PRAGMA table_info(njoftime)")
    kolonat_ekzistuese = [col[1] for col in cursor.fetchall()]
    
    kolonat_nevojshme = {
        "perdoruesi": "TEXT",
        "kategoria": "TEXT",
        "titulli": "TEXT",
        "pershkrimi": "TEXT",
        "cmimi": "REAL",
        "kontakti": "TEXT",
        "lokacioni": "TEXT",
        "detaje_specifike": "TEXT",
        "data": "TEXT",
        "foto_paths": "TEXT"
    }
    
    for kolona, tipi in kolonat_nevojshme.items():
        if kolona not in kolonat_ekzistuese:
            try:
                cursor.execute(f"ALTER TABLE njoftime ADD COLUMN {kolona} {tipi}")
            except:
                pass

    # Krijimi i tabelës së përdoruesve
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS perdoruesit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            email TEXT
        )
    ''')
    
    cursor.execute("PRAGMA table_info(perdoruesit)")
    kolonat_user = [col[1] for col in cursor.fetchall()]
    if "email" not in kolonat_user:
        try:
            cursor.execute("ALTER TABLE perdoruesit ADD COLUMN email TEXT")
        except:
            pass
        
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
    return df

def merr_perdoruesit():
    conn = sqlite3.connect('njoftime.db')
    df = pd.read_sql_query("SELECT id, username, email FROM perdoruesit", conn)
    conn.close()
    return df

query_params = st.query_params
is_admin_route = query_params.get("page") == "admin"

# --- HEADER I FAQES ---
st.markdown("""
    <div class="site-header">
        <div>
            <div class="header-logo">🛍️ Marketplace Shqipëri</div>
            <div class="header-tagline">Destinacioni kryesor për njoftimet tuaja në Shqipëri</div>
        </div>
        <div style="text-align: right; font-size: 13px; opacity: 0.9;">
            <b>Qytetet kryesore:</b> Tiranë, Durrës, Vlorë, Shkodër...
        </div>
    </div>
""", unsafe_allow_html=True)

if is_admin_route:
    st.title("🔐 Paneli i Administrimit (Admin Login)")
    
    if not st.session_state['admin_logged_in']:
        with st.form("admin_login_form"):
            a_user = st.text_input("Admin Username")
            a_pass = st.text_input("Admin Password", type="password")
            a_submit = st.form_submit_button("Hyr në Admin")
            if a_submit:
                if a_user == "admin" and a_pass == "12345":
                    st.session_state['admin_logged_in'] = True
                    st.success("U kyçët si Administrator!")
                    st.rerun()
                else:
                    st.error("Kredenciale të gabuara për admin!")
    else:
        st.success("Jeni i kyçur si Administrator i Sistemit.")
        if st.button("Dil nga Admini"):
            st.session_state['admin_logged_in'] = False
            st.rerun()
            
        st.divider()
        st.subheader("📊 Menaxhimi i Përgjithshëm i Platformës")
        df_users = merr_perdoruesit()
        df_all_njoftime = merr_njoftimet()
        
        col_a1, col_a2 = st.columns(2)
        col_a1.metric("Përdorues të Regjistruar", len(df_users))
        col_a2.metric("Gjithsej Njoftime", len(df_all_njoftime))
        st.divider()
        
        st.write("### Lista e Përdoruesve & Email-ve")
        st.dataframe(df_users, use_container_width=True)
        
        st.write("### Menaxhimi i Njoftimeve (Mund të fshish çdo njoftim)")
        for idx, row in df_all_njoftime.iterrows():
            col_info1, col_info2 = st.columns([4, 1])
            with col_info1:
                st.write(f"**ID:** {row['id']} | **{row['titulli']}** — *Postuar nga: {row['perdoruesi']}* ({row['data']})")
            with col_info2:
                if st.button("Fshi", key=f"admin_fshi_{row['id']}"):
                    fshi_njoftimin(row['id'], row['foto_paths'])
                    st.success(f"Njoftimi #{row['id']} u fshi!")
                    st.rerun()

else:
    # --- MENAXHIMI I LLOGARISË NË KRYE (I dukshëm në celular) ---
    st.markdown("---")
    col_stat1, col_stat2 = st.columns([2, 3])
    with col_stat1:
        if st.session_state['user_logged_in']:
            st.success(f"Përshëndetje, **{st.session_state['username']}**! 🎉")
        else:
            st.info("Nuk je i kyçur. Mund të hysh ose të regjistrohesh më poshtë 👇")
    with col_stat2:
        if st.session_state['user_logged_in']:
            if st.button("Dil nga Llogaria (Logout)"):
                st.session_state['user_logged_in'] = False
                st.session_state['username'] = ""
                st.rerun()

    if not st.session_state['user_logged_in']:
        with st.expander("🔑 Kliko këtu për t'u Kyçur ose Regjistruar në Llogarinë Tende", expanded=True):
            auth_tab1, auth_tab2 = st.tabs(["Kyçu (Login)", "Regjistrohu (Register)"])
            
            with auth_tab1:
                with st.form("login_form_main"):
                    l_user = st.text_input("Username")
                    l_pass = st.text_input("Fjalëkalimi", type="password")
                    l_submit = st.form_submit_button("Hyr në llogari")
                    if l_submit:
                        if verifiko_user(l_user, l_pass):
                            st.session_state['user_logged_in'] = True
                            st.session_state['username'] = l_user
                            st.success("U kyçët me sukses!")
                            st.rerun()
                        else:
                            st.error("Username ose fjalëkalim i gabuar!")
                            
            with auth_tab2:
                with st.form("register_form_main"):
                    r_user = st.text_input("Krijo Username *")
                    r_email = st.text_input("Adresa Email *")
                    r_pass = st.text_input("Krijo Fjalëkalim *", type="password")
                    r_submit = st.form_submit_button("Krijo Llogari të Re")
                    if r_submit:
                        if r_user and r_email and r_pass:
                            if regjistro_user(r_user, r_pass, r_email):
                                st.success("Regjistrimi u krye me sukses! Tani mund të kyçesh tek skeda 'Kyçu'.")
                            else:
                                st.error("Ky username ose email ekziston tashmë!")
                        else:
                            st.error("Ju lutem plotësoni të gjitha fushat e detyrueshme (*).")

    st.markdown("---")
    tab1, tab2 = st.tabs(["Shiko Njoftimet", "Posto Njoftim të Ri"])

    with tab1:
        df = merr_njoftimet()
        if not df.empty:
            col_m1, col_m2 = st.columns(2)
            col_m1.metric("Gjithsej Njoftime Aktive", len(df))
            col_m2.metric("Qytete të Përfshira", df['lokacioni'].nunique() if 'lokacioni' in df else 0)
            st.divider()
            
            st.sidebar.header("Filtrimi i Njoftimeve")
            kategorite = ["Të gjitha"] + list(df['kategoria'].unique())
            zgjidh_kategori = st.sidebar.selectbox("Kategoria", kategorite)
            
            lokacionet = ["Të gjitha"] + list(df['lokacioni'].dropna().unique())
            zgjidh_lokacion = st.sidebar.selectbox("Qyteti / Lokacioni", lokacionet)
            
            max_cmimi_db = float(df['cmimi'].max()) if not df['cmimi'].dropna().empty else 10000.0
            min_c, max_c = st.sidebar.slider("Filtro sipas Çmimit (€)", 0.0, max(max_cmimi_db, 1000.0), (0.0, max(max_cmimi_db, 1000.0)))
            
            search_query = st.sidebar.text_input("Kërko fjalë kyçe")
            renditja = st.sidebar.selectbox("Renditja", ["Të rejat fillimisht", "Çmimi: Më i lirë -> Më i shtrenjtë", "Çmimi: Më i shtrenjtë -> Më i lirë"])
            
            filtered_df = df.copy()
            if zgjidh_kategori != "Të gjitha":
                filtered_df = filtered_df[filtered_df['kategoria'] == zgjidh_kategori]
            if zgjidh_lokacion != "Të gjitha":
                filtered_df = filtered_df[filtered_df['lokacioni'] == zgjidh_lokacion]
            
            filtered_df = filtered_df[(filtered_df['cmimi'] >= min_c) & (filtered_df['cmimi'] <= max_c)]
            
            if search_query:
                filtered_df = filtered_df[
                    filtered_df['titulli'].str.contains(search_query, case=False, na=False) |
                    filtered_df['pershkrimi'].str.contains(search_query, case=False, na=False)
                ]
            if renditja == "Çmimi: Më i lirë -> Më i shtrenjtë":
                filtered_df = filtered_df.sort_values(by='cmimi', ascending=True, na_position='last')
            elif renditja == "Çmimi: Më i shtrenjtë -> Më i lirë":
                filtered_df = filtered_df.sort_values(by='cmimi', ascending=False, na_position='last')
                
            st.markdown(f"**Njoftime të shfaqura:** {len(filtered_df)}")
            st.write("")
            
            njoftime_list = filtered_df.to_dict('records')
            for i in range(0, len(njoftime_list), 2):
                col_grid1, col_grid2 = st.columns(2)
                with col_grid1:
                    row = njoftime_list[i]
                    st.markdown('<div class="card-box">', unsafe_allow_html=True)
                    
                    foto_paths = row['foto_paths'].split(",") if row['foto_paths'] else []
                    valid_fotos = [p for p in foto_paths if p and os.path.exists(p)]
                    if valid_fotos:
                        selected_img_path = st.selectbox("Foto", valid_fotos, key=f"img_sel_{row['id']}")
                        try:
                            st.image(Image.open(selected_img_path), use_container_width=True)
                        except:
                            st.info("[Gabim në ngarkimin e fotos]")
                    else:
                        st.info("[Pa foto]")
                    
                    cat = row['kategoria']
                    badge_class = "badge-tjetër"
                    if cat == "Automjete": badge_class = "badge-automjete"
                    elif cat == "Pasuri të Paluajtshme": badge_class = "badge-pasuri"
                    elif cat == "Elektronikë": badge_class = "badge-elektronikë"
                    elif cat == "Punë & Shërbime": badge_class = "badge-punë"
                    
                    st.markdown(f'<span class="{badge_class}">{cat}</span>', unsafe_allow_html=True)
                    st.markdown(f"### {row['titulli']}")
                    p_shkurtër = row['pershkrimi'][:110] + "..." if len(row['pershkrimi']) > 110 else row['pershkrimi']
                    st.write(p_shkurtër)
                    
                    if pd.notna(row['cmimi']) and row['cmimi'] > 0:
                        st.success(f"Çmimi: {row['cmimi']} €")
                    else:
                        st.info("Çmimi: Me Marrëveshje")
                        
                    with st.expander("Shiko Detajet e Plota & Kontaktin"):
                        st.write(f"**Përshkrimi i plotë:** {row['pershkrimi']}")
                        if row['detaje_specifike']:
                            st.markdown(f"**Specifikat:** `{row['detaje_specifike']}`")
                        st.caption(f"Postuar nga: {row['perdoruesi']} | Lokacioni: {row['lokacioni']} | Telefoni: {row['kontakti']} | Data: {row['data']}")
                        telefon = str(row['kontakti']).strip()
                        if telefon.isdigit() or telefon.startswith("+"):
                            w_link = f"https://wa.me/{telefon.replace('+', '')}?text=Përshëndetje, jam i interesuar për njoftimin: {row['titulli']}"
                            b1, b2 = st.columns(2)
                            b1.markdown(f"[WhatsApp]({w_link})", unsafe_allow_html=True)
                            b2.markdown(f"[Telefono](tel:{telefon})", unsafe_allow_html=True)
                    
                    if st.session_state['user_logged_in'] and st.session_state['username'] == row['perdoruesi']:
                        if st.button("Fshi Njoftimin Tim", key=f"fshi_{row['id']}"):
                            fshi_njoftimin(row['id'], row['foto_paths'])
                            st.success("U fshi!")
                            st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                if i + 1 < len(njoftime_list):
                    with col_grid2:
                        row2 = njoftime_list[i + 1]
                        st.markdown('<div class="card-box">', unsafe_allow_html=True)
                        
                        foto_paths2 = row2['foto_paths'].split(",") if row2['foto_paths'] else []
                        valid_fotos2 = [p for p in foto_paths2 if p and os.path.exists(p)]
                        if valid_fotos2:
                            selected_img_path2 = st.selectbox("Foto", valid_fotos2, key=f"img_sel2_{row2['id']}")
                            try:
                                st.image(Image.open(selected_img_path2), use_container_width=True)
                            except:
                                st.info("[Gabim në ngarkimin e fotos]")
                        else:
                            st.info("[Pa foto]")
                            
                        cat2 = row2['kategoria']
                        badge_class2 = "badge-tjetër"
                        if cat2 == "Automjete": badge_class2 = "badge-automjete"
                        elif cat2 == "Pasuri të Paluajtshme": badge_class2 = "badge-pasuri"
                        elif cat2 == "Elektronikë": badge_class2 = "badge-elektronikë"
                        elif cat2 == "Punë & Shërbime": badge_class2 = "badge-punë"
                        
                        st.markdown(f'<span class="{badge_class2}">{cat2}</span>', unsafe_allow_html=True)
                        st.markdown(f"### {row2['titulli']}")
                        p_shkurtër2 = row2['pershkrimi'][:110] + "..." if len(row2['pershkrimi']) > 110 else row2['pershkrimi']
                        st.write(p_shkurtër2)
                        
                        if pd.notna(row2['cmimi']) and row2['cmimi'] > 0:
                            st.success(f"Çmimi: {row2['cmimi']} €")
                        else:
                            st.info("Çmimi: Me Marrëveshje")
                            
                        with st.expander("Shiko Detajet e Plota & Kontaktin"):
                            st.write(f"**Përshkrimi i plotë:** {row2['pershkrimi']}")
                            if row2['detaje_specifike']:
                                st.markdown(f"**Specifikat:** `{row2['detaje_specifike']}`")
                            st.caption(f"Postuar nga: {row2['perdoruesi']} | Lokacioni: {row2['lokacioni']} | Telefoni: {row2['kontakti']} | Data: {row2['data']}")
                            telefon2 = str(row2['kontakti']).strip()
                            if telefon2.isdigit() or telefon2.startswith("+"):
                                w_link2 = f"https://wa.me/{telefon2.replace('+', '')}?text=Përshëndetje, jam i interesuar për njoftimin: {row2['titulli']}"
                                bx1, bx2 = st.columns(2)
                                bx1.markdown(f"[WhatsApp]({w_link2})", unsafe_allow_html=True)
                                bx2.markdown(f"[Telefono](tel:{telefon2})", unsafe_allow_html=True)
                        
                        if st.session_state['user_logged_in'] and st.session_state['username'] == row2['perdoruesi']:
                            if st.button("Fshi Njoftimin Tim", key=f"fshi_{row2['id']}"):
                                fshi_njoftimin(row2['id'], row2['foto_paths'])
                                st.success("U fshi!")
                                st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Nuk ka asnjë njoftim të postuar ende.")

    with tab2:
        st.subheader("Shto Njoftim të Ri në Platformë")
        if not st.session_state['user_logged_in']:
            st.warning("Ju lutem kyçuni (login) tek seksioni lart në faqe për të postuar një njoftim të ri!")
        else:
            with st.form("formular_njoftimi", clear_on_submit=True):
                kategoria = st.selectbox("Kategoria e Njoftimit", ["Automjete", "Pasuri të Paluajtshme", "Elektronikë", "Punë & Shërbime", "Shtëpi & Kopsht", "Të Tjera"])
                titulli = st.text_input("Titulli i Njoftimit (p.sh. Shitet Audi A4 / Apartament 2+1)")
                pershkrimi = st.text_area("Përshkrimi i detajuar")
                
                detaje_specifike = ""
                if kategoria == "Automjete":
                    col_m1, col_m2, col_m3 = st.columns(3)
                    vit_prodhimi = col_m1.text_input("Viti i Prodhimit (p.sh. 2018)")
                    km = col_m2.text_input("Kilometrazhi (p.sh. 150000 km)")
                    kambio = col_m3.selectbox("Kambio", ["Automatike", "Manuale"])
                    detaje_specifike = f"Viti: {vit_prodhimi} | KM: {km} | Kambio: {kambio}"
                elif kategoria == "Pasuri të Paluajtshme":
                    col_s1, col_s2 = st.columns(2)
                    sipfaqja = col_s1.text_input("Sipërfaqja (p.sh. 85 m²)")
                    dhoma = col_s2.text_input("Kategoria/Dhomat (p.sh. 2+1)")
                    detaje_specifike = f"Sipërfaqja: {sipfaqja} | Dhomat: {dhoma}"
                elif kategoria == "Punë & Shërbime":
                    lloji_punes = st.selectbox("Lloji i Orarit", ["Full-time", "Part-time", "Freelance / Shërbim"])
                    detaje_specifike = f"Orari: {lloji_punes}"

                c_p1, c_p2 = st.columns(2)
                with c_p1:
                    cmimi_input = st.number_input("Çmimi në Euro (€) (Lëre 0 nëse s'ka çmim)", min_value=0.0, step=10.0)
                with c_p2:
                    lokacioni = st.selectbox("Lokacioni (Qyteti)", ["Tiranë", "Durrës", "Vlorë", "Shkodër", "Elbasan", "Fier", "Korçë", "Gjirokastër", "Tjetër"])
                    
                kontakti = st.text_input("Numri i Telefonit (p.sh. 069XXXXXXX)")
                uploaded_files = st.file_uploader("Ngarko foto (Mund të zgjedhësh disa njëkohësisht)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
                
                submit_button = st.form_submit_button(label="Publiko Njoftimin Tani")
                
                if submit_button:
                    if titulli and pershkrimi and kontakti:
                        foto_paths_list = []
                        if uploaded_files:
                            for uploaded_file in uploaded_files:
                                timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                                filename = f"{timestamp_str}_{uploaded_file.name}"
                                f_path = os.path.join(UPLOAD_DIR, filename)
                                with open(f_path, "wb") as f:
                                    f.write(uploaded_file.getbuffer())
                                foto_paths_list.append(f_path)
                        
                        foto_paths_str = ",".join(foto_paths_list)
                        shto_njoftim(st.session_state['username'], kategoria, titulli, pershkrimi, cmimi_input, kontakti, lokacioni, detaje_specifike, foto_paths_str)
                        st.success("Njoftimi u publikua me sukses!")
                    else:
                        st.error("Ju lutem plotësoni Titullin, Përshkrimin dhe Kontaktin.")

# --- FOOTER I FAQES ---
st.markdown("""
    <div class="site-footer">
        <div style="display: flex; justify-content: space-between; flex-wrap: wrap; gap: 30px;">
            <div style="flex: 2; min-width: 250px;">
                <div class="footer-title">Rreth Marketplace Shqipëri</div>
                <div class="footer-text">
                    Platforma juaj e besuar për blerjen, shitjen dhe dhënien me qira të automjeteve, pasurive të paluajtshme, pajisjeve elektronike dhe shërbimeve në të gjithë Shqipërinë.
                </div>
            </div>
            <div style="flex: 1; min-width: 150px;">
                <div class="footer-title">Kategoritë</div>
                <div class="footer-text">
                    🚗 Automjete<br>
                    🏠 Pasuri të Paluajtshme<br>
                    💻 Elektronikë<br>
                    🛠️ Punë & Shërbime
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