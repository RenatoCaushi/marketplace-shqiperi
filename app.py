import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime
from PIL import Image

# Konfigurimi i folderit të fotove
UPLOAD_DIR = "uploaded_images"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Konfigurimi i faqes dhe CSS i avancuar për UI/UX premium
st.set_page_config(
    page_title="Marketplace Shqipëri",
    page_icon="💼",
    layout="wide"
)

st.markdown("""
    <style>
    /* Stili i Përgjithshëm */
    .hero-container {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        padding: 30px;
        border-radius: 16px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.3);
    }
    .hero-title {
        font-size: 36px;
        font-weight: 800;
        margin-bottom: 5px;
    }
    .hero-subtitle {
        font-size: 16px;
        opacity: 0.9;
    }
    
    /* Kartat moderne me efekt Hover */
    .card-box {
        background-color: #ffffff;
        border: 1px solid #E5E7EB;
        padding: 20px;
        border-radius: 14px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.04);
        margin-bottom: 20px;
        height: 100%;
        transition: all 0.3s ease;
    }
    .card-box:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 20px -3px rgba(0, 0, 0, 0.08);
        border-color: #3B82F6;
    }
    
    /* Badges për kategoritë */
    .badge-punë { background-color: #DBEAFE; color: #1E40AF; padding: 4px 10px; border-radius: 20px; font-weight: 600; font-size: 12px; }
    .badge-makina { background-color: #FEF3C7; color: #92400E; padding: 4px 10px; border-radius: 20px; font-weight: 600; font-size: 12px; }
    .badge-shtëpi { background-color: #D1FAE5; color: #065F46; padding: 4px 10px; border-radius: 20px; font-weight: 600; font-size: 12px; }
    .badge-tjetër { background-color: #F3F4F6; color: #374151; padding: 4px 10px; border-radius: 20px; font-weight: 600; font-size: 12px; }
    </style>
""", unsafe_allow_html=True)

# Krijimi/Lidhja me bazën e të dhënave SQLite
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
            foto_path TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def shto_njoftim(kategoria, titulli, pershkrimi, cmimi, kontakti, lokacioni, detaje_specifike, foto_path):
    conn = sqlite3.connect('njoftime.db')
    cursor = conn.cursor()
    data_aktuale = datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute('''
        INSERT INTO njoftime (kategoria, titulli, pershkrimi, cmimi, kontakti, lokacioni, detaje_specifike, data, foto_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (kategoria, titulli, pershkrimi, cmimi, kontakti, lokacioni, detaje_specifike, data_aktuale, foto_path))
    conn.commit()
    conn.close()

def fshi_njoftimin(njoftim_id, foto_path):
    conn = sqlite3.connect('njoftime.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM njoftime WHERE id = ?", (njoftim_id,))
    conn.commit()
    conn.close()
    
    if foto_path and os.path.exists(foto_path):
        try:
            os.remove(foto_path)
        except:
            pass

def merr_njoftimet():
    conn = sqlite3.connect('njoftime.db')
    df = pd.read_sql_query("SELECT * FROM njoftime ORDER BY id DESC", conn)
    conn.close()
    return df

# Header i pastër
st.markdown("""
    <div class="hero-container">
        <div class="hero-title">Marketplace Shqipëri</div>
        <div class="hero-subtitle">Platforma më e shpejtë për të blerë, shitur dhe gjetur shërbime apo mundësi punësimi.</div>
    </div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["Shiko Njoftimet", "Posto Njoftim të Ri"])

with tab1:
    df = merr_njoftimet()
    
    if not df.empty:
        # Statistikat lart
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Gjithsej Njoftime Aktive", len(df))
        col_m2.metric("Makina & Shtëpi", len(df[df['kategoria'].isin(['Makina', 'Shtëpi & Pasuri të Paluajtshme'])]))
        col_m3.metric("Mundësi Punësimi", len(df[df['kategoria'] == 'Punë']))
        st.divider()
        
        # Paneli anësor për filtrat
        st.sidebar.header("Filtrimi i Njoftimeve")
        
        kategorite = ["Të gjitha"] + list(df['kategoria'].unique())
        zgjidh_kategori = st.sidebar.selectbox("Kategoria", kategorite)
        
        lokacionet = ["Të gjitha"] + list(df['lokacioni'].dropna().unique())
        zgjidh_lokacion = st.sidebar.selectbox("Lokacioni", lokacionet)
        
        search_query = st.sidebar.text_input("Kërko fjalë kyçe")
        renditja = st.sidebar.selectbox("Renditja", ["Të rejat fillimisht", "Çmimi: Më i lirë -> Më i shtrenjtë", "Çmimi: Më i shtrenjtë -> Më i lirë"])
        
        filtered_df = df.copy()
        
        if zgjidh_kategori != "Të gjitha":
            filtered_df = filtered_df[filtered_df['kategoria'] == zgjidh_kategori]
        if zgjidh_lokacion != "Të gjitha":
            filtered_df = filtered_df[filtered_df['lokacioni'] == zgjidh_lokacion]
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
        
        # Shfaqja në formë Grid me 2 kolona
        njoftime_list = filtered_df.to_dict('records')
        for i in range(0, len(njoftime_list), 2):
            col_grid1, col_grid2 = st.columns(2)
            
            # Kolona 1
            with col_grid1:
                row = njoftime_list[i]
                st.markdown('<div class="card-box">', unsafe_allow_html=True)
                
                if row['foto_path'] and os.path.exists(row['foto_path']):
                    try:
                        img = Image.open(row['foto_path'])
                        st.image(img, use_container_width=True)
                    except:
                        st.info("[Pa foto]")
                else:
                    st.info("[Pa foto]")
                    
                cat = row['kategoria']
                badge_class = "badge-tjetër"
                if cat == "Punë": badge_class = "badge-punë"
                elif cat == "Makina": badge_class = "badge-makina"
                elif "Shtëpi" in cat: badge_class = "badge-shtëpi"
                
                st.markdown(f'<span class="{badge_class}">{cat}</span>', unsafe_allow_html=True)
                st.markdown(f"### {row['titulli']}")
                st.write(row['pershkrimi'])
                
                if row['detaje_specifike']:
                    st.markdown(f"Info: `{row['detaje_specifike']}`")
                st.caption(f"Lokacioni: {row['lokacioni']} | Telefoni: {row['kontakti']} | Data: {row['data']}")
                
                if pd.notna(row['cmimi']) and row['cmimi'] > 0:
                    st.success(f"Çmimi: {row['cmimi']} €")
                else:
                    st.info("Çmimi: Me Marrëveshje")
                    
                telefon = str(row['kontakti']).strip()
                if telefon.isdigit() or telefon.startswith("+"):
                    w_link = f"https://wa.me/{telefon.replace('+', '')}?text=Përshëndetje, jam i interesuar për: {row['titulli']}"
                    b1, b2 = st.columns(2)
                    b1.markdown(f"[WhatsApp]({w_link})", unsafe_allow_html=True)
                    b2.markdown(f"[Telefono](tel:{telefon})", unsafe_allow_html=True)
                
                if st.button("Fshi Njoftimin", key=f"fshi_{row['id']}"):
                    fshi_njoftimin(row['id'], row['foto_path'])
                    st.success("U fshi!")
                    st.rerun()
                    
                st.markdown('</div>', unsafe_allow_html=True)
                
            # Kolona 2
            if i + 1 < len(njoftime_list):
                with col_grid2:
                    row2 = njoftime_list[i + 1]
                    st.markdown('<div class="card-box">', unsafe_allow_html=True)
                    
                    if row2['foto_path'] and os.path.exists(row2['foto_path']):
                        try:
                            img2 = Image.open(row2['foto_path'])
                            st.image(img2, use_container_width=True)
                        except:
                            st.info("[Pa foto]")
                    else:
                        st.info("[Pa foto]")
                        
                    cat2 = row2['kategoria']
                    badge_class2 = "badge-tjetër"
                    if cat2 == "Punë": badge_class2 = "badge-punë"
                    elif cat2 == "Makina": badge_class2 = "badge-makina"
                    elif "Shtëpi" in cat2: badge_class2 = "badge-shtëpi"
                    
                    st.markdown(f'<span class="{badge_class2}">{cat2}</span>', unsafe_allow_html=True)
                    st.markdown(f"### {row2['titulli']}")
                    st.write(row2['pershkrimi'])
                    
                    if row2['detaje_specifike']:
                        st.markdown(f"Info: `{row2['detaje_specifike']}`")
                    st.caption(f"Lokacioni: {row2['lokacioni']} | Telefoni: {row2['kontakti']} | Data: {row2['data']}")
                    
                    if pd.notna(row2['cmimi']) and row2['cmimi'] > 0:
                        st.success(f"Çmimi: {row2['cmimi']} €")
                    else:
                        st.info("Çmimi: Me Marrëveshje")
                        
                    telefon2 = str(row2['kontakti']).strip()
                    if telefon2.isdigit() or telefon2.startswith("+"):
                        w_link2 = f"https://wa.me/{telefon2.replace('+', '')}?text=Përshëndetje, jam i interesuar për: {row2['titulli']}"
                        bx1, bx2 = st.columns(2)
                        bx1.markdown(f"[WhatsApp]({w_link2})", unsafe_allow_html=True)
                        bx2.markdown(f"[Telefono](tel:{telefon2})", unsafe_allow_html=True)
                    
                    if st.button("Fshi Njoftimin", key=f"fshi_{row2['id']}"):
                        fshi_njoftimin(row2['id'], row2['foto_path'])
                        st.success("U fshi!")
                        st.rerun()
                        
                    st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Nuk ka asnjë njoftim të postuar ende. Kaloni te skeda e dytë për të postuar të parin!")

with tab2:
    st.subheader("Shto Njoftim të Ri në Platformë")
    
    with st.form("formular_njoftimi", clear_on_submit=True):
        kategoria = st.selectbox("Kategoria e Njoftimit", ["Punë", "Makina", "Shtëpi & Pasuri të Paluajtshme", "Elektronikë", "Shërbime Të Tjera"])
        titulli = st.text_input("Titulli i Njoftimit (p.sh. Shitet Audi A4 / Inxhinier Software)")
        pershkrimi = st.text_area("Përshkrimi i detajuar")
        
        detaje_specifike = ""
        if kategoria == "Makina":
            col_m1, col_m2 = st.columns(2)
            vit_prodhimi = col_m1.text_input("Viti i Prodhimit (p.sh. 2018)")
            km = col_m2.text_input("Kilometrazhi (p.sh. 150000 km)")
            detaje_specifike = f"Viti: {vit_prodhimi} | KM: {km}"
        elif kategoria == "Shtëpi & Pasuri të Paluajtshme":
            col_s1, col_s2 = st.columns(2)
            sipfaqja = col_s1.text_input("Sipërfaqja (p.sh. 85 m²)")
            dhoma = col_s2.text_input("Kategoria/Dhomat (p.sh. 2+1)")
            detaje_specifike = f"Sipërfaqja: {sipfaqja} | Dhomat: {dhoma}"
        elif kategoria == "Punë":
            lloji_punes = st.selectbox("Lloji i Orarit", ["Full-time", "Part-time", "Remote / Online"])
            detaje_specifike = f"Orari: {lloji_punes}"

        c_p1, c_p2 = st.columns(2)
        with c_p1:
            cmimi_input = st.number_input("Çmimi në Euro (€) (Lëre 0 nëse s'ka çmim)", min_value=0.0, step=10.0)
        with c_p2:
            lokacioni = st.selectbox("Lokacioni (Qyteti)", ["Tiranë", "Durrës", "Vlorë", "Shkodër", "Elbasan", "Fier", "Korçë", "Gjirokastër", "Tjetër"])
            
        kontakti = st.text_input("Numri i Telefonit (p.sh. 069XXXXXXX)")
        uploaded_file = st.file_uploader("Ngarko foto (Opsionale)", type=["jpg", "jpeg", "png"])
        
        submit_button = st.form_submit_button(label="Publiko Njoftimin Tani")
        
        if submit_button:
            if titulli and pershkrimi and kontakti:
                foto_path = None
                if uploaded_file is not None:
                    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{timestamp_str}_{uploaded_file.name}"
                    foto_path = os.path.join(UPLOAD_DIR, filename)
                    
                    with open(foto_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                
                shto_njoftim(kategoria, titulli, pershkrimi, cmimi_input, kontakti, lokacioni, detaje_specifike, foto_path)
                st.success("Njoftimi u publikua me sukses!")
            else:
                st.error("Ju lutem plotësoni Titullin, Përshkrimin dhe Kontaktin.")

# Footer i faqes
st.markdown("""
    <hr style="margin-top: 40px; margin-bottom: 20px;">
    <div style="text-align: center; color: #6B7280; font-size: 14px; padding-bottom: 20px;">
        <p><b>Marketplace Shqipëri</b> &copy; 2026 | Të gjitha të drejtat e rezervuara.</p>
        <p>Ndërtuar me Python & Streamlit 🚀</p>
    </div>
""", unsafe_allow_html=True)