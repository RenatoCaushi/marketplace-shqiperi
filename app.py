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

st.markdown("""
    <style>
    .hero-container {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        padding: 35px 30px;
        border-radius: 16px;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.25);
    }
    .hero-title {
        font-size: 38px;
        font-weight: 800;
        margin-bottom: 8px;
        letter-spacing: -0.5px;
    }
    .hero-subtitle {
        font-size: 16px;
        opacity: 0.9;
        font-weight: 400;
    }
    .card-box {
        background-color: #ffffff;
        border: 1px solid #E5E7EB;
        padding: 22px;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03), 0 2px 4px -1px rgba(0, 0, 0, 0.02);
        margin-bottom: 24px;
        height: 100%;
        transition: all 0.25s ease-in-out;
    }
    .card-box:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 24px -4px rgba(59, 130, 246, 0.12);
        border-color: #93C5FD;
    }
    .badge-automjete { background-color: #EFF6FF; color: #1D4ED8; padding: 5px 12px; border-radius: 20px; font-weight: 600; font-size: 12px; border: 1px solid #BFDBFE; }
    .badge-pasuri { background-color: #F0FDF4; color: #15803D; padding: 5px 12px; border-radius: 20px; font-weight: 600; font-size: 12px; border: 1px solid #BBF7D0; }
    .badge-elektronikë { background-color: #FAF5FF; color: #7E22CE; padding: 5px 12px; border-radius: 20px; font-weight: 600; font-size: 12px; border: 1px solid #E9D5FF; }
    .badge-punë { background-color: #FEF2F2; color: #B91C1C; padding: 5px 12px; border-radius: 20px; font-weight: 600; font-size: 12px; border: 1px solid #FECACA; }
    .badge-tjetër { background-color: #F8FAFC; color: #475569; padding: 5px 12px; border-radius: 20px; font-weight: 600; font-size: 12px; border: 1px solid #E2E8F0; }
    </style>
""", unsafe_allow_html=True)

def init_db():
    conn = sqlite3.connect('njoftime.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS njoftime (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    conn.commit()
    conn.close()

init_db()

def shto_njoftim(kategoria, titulli, pershkrimi, cmimi, kontakti, lokacioni, detaje_specifike, foto_paths_str):
    conn = sqlite3.connect('njoftime.db')
    cursor = conn.cursor()
    data_aktuale = datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute('''
        INSERT INTO njoftime (kategoria, titulli, pershkrimi, cmimi, kontakti, lokacioni, detaje_specifike, data, foto_paths)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (kategoria, titulli, pershkrimi, cmimi, kontakti, lokacioni, detaje_specifike, data_aktuale, foto_paths_str))
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

st.markdown("""
    <div class="hero-container">
        <div class="hero-title">Marketplace Shqipëri</div>
        <div class="hero-subtitle">Platforma më e pastër dhe moderne për të shfletuar dhe postuar njoftimet tuaja.</div>
    </div>
""", unsafe_allow_html=True)

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
                    st.caption(f"Lokacioni: {row['lokacioni']} | Telefoni: {row['kontakti']} | Data: {row['data']}")
                    telefon = str(row['kontakti']).strip()
                    if telefon.isdigit() or telefon.startswith("+"):
                        w_link = f"https://wa.me/{telefon.replace('+', '')}?text=Përshëndetje, jam i interesuar për njoftimin: {row['titulli']}"
                        b1, b2 = st.columns(2)
                        b1.markdown(f"[WhatsApp]({w_link})", unsafe_allow_html=True)
                        b2.markdown(f"[Telefono](tel:{telefon})", unsafe_allow_html=True)
                
                if st.button("Fshi Njoftimin", key=f"fshi_{row['id']}"):
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
                        st.caption(f"Lokacioni: {row2['lokacioni']} | Telefoni: {row2['kontakti']} | Data: {row2['data']}")
                        telefon2 = str(row2['kontakti']).strip()
                        if telefon2.isdigit() or telefon2.startswith("+"):
                            w_link2 = f"https://wa.me/{telefon2.replace('+', '')}?text=Përshëndetje, jam i interesuar për njoftimin: {row2['titulli']}"
                            bx1, bx2 = st.columns(2)
                            bx1.markdown(f"[WhatsApp]({w_link2})", unsafe_allow_html=True)
                            bx2.markdown(f"[Telefono](tel:{telefon2})", unsafe_allow_html=True)
                    
                    if st.button("Fshi Njoftimin", key=f"fshi_{row2['id']}"):
                        fshi_njoftimin(row2['id'], row2['foto_paths'])
                        st.success("U fshi!")
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Nuk ka asnjë njoftim të postuar ende.")

with tab2:
    st.subheader("Shto Njoftim të Ri në Platformë")
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
                shto_njoftim(kategoria, titulli, pershkrimi, cmimi_input, kontakti, lokacioni, detaje_specifike, foto_paths_str)
                st.success("Njoftimi u publikua me sukses!")
            else:
                st.error("Ju lutem plotësoni Titullin, Përshkrimin dhe Kontaktin.")

st.markdown("""
    <hr style="margin-top: 40px; margin-bottom: 20px;">
    <div style="text-align: center; color: #64748B; font-size: 14px; padding-bottom: 20px;">
        <p><b>Marketplace Shqipëri</b> &copy; 2026 | Të gjitha të drejtat e rezervuara.</p>
    </div>
""", unsafe_allow_html=True)