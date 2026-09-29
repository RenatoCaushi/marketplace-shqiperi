import os
import sqlite3
import streamlit as st
import pandas as pd

# Konfigurimi i faqes
st.set_page_config(
    page_title="Marketplace Shqipëri",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Përcaktojmë rrugën absolute të databazës
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "marketplace.db")

def init_database():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS perdoruesit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emri TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            fjalekalimi TEXT,
            data_regjistrimit TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("PRAGMA table_info(perdoruesit)")
    columns_p = [col[1] for col in cursor.fetchall()]
    if "fjalekalimi" not in columns_p:
        cursor.execute("ALTER TABLE perdoruesit ADD COLUMN fjalekalimi TEXT")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS njoftime (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulli TEXT NOT NULL,
            pershkrimi TEXT,
            kategoria TEXT,
            qyteti TEXT,
            cmimi TEXT,
            kontakti TEXT,
            foto TEXT,
            detaje_specifike TEXT,
            perdorues_id INTEGER,
            FOREIGN KEY (perdorues_id) REFERENCES perdoruesit(id)
        )
    """)
    
    cursor.execute("PRAGMA table_info(njoftime)")
    columns_n = [col[1] for col in cursor.fetchall()]
    if "foto" not in columns_n:
        cursor.execute("ALTER TABLE njoftime ADD COLUMN foto TEXT")
    if "detaje_specifike" not in columns_n:
        cursor.execute("ALTER TABLE njoftime ADD COLUMN detaje_specifike TEXT")
    
    conn.commit()
    conn.close()

init_database()

def run_query(query, params=(), fetch_all=True, commit=False):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        if commit:
            conn.commit()
        result = cursor.fetchall() if fetch_all else cursor.fetchone()
    except Exception as e:
        result = None
        st.error(f"Gabim në databazë: {e}")
    finally:
        conn.close()
    return result

# --- STILIZIMI I PROFESIONALIZUAR CSS ---
st.markdown("""
    <style>
        .stApp { background-color: #f8fafc; font-family: 'Inter', sans-serif; }
        .card-title { color: #0f172a; font-size: 1.3rem; font-weight: 700; margin: 0 0 8px 0; }
        .card-desc { color: #475569; font-size: 0.95rem; line-height: 1.5; margin-bottom: 12px; }
        .spec-box { background-color: #f8fafc; border-left: 3px solid #2563eb; padding: 8px 12px; font-size: 0.85rem; color: #334155; margin-bottom: 12px; border-radius: 4px; }
        .badge-kategoria { background-color: #eff6ff; color: #2563eb; padding: 6px 14px; border-radius: 30px; font-size: 0.8rem; font-weight: 600; }
        .badge-qyteti { background-color: #f1f5f9; color: #475569; padding: 6px 14px; border-radius: 30px; font-size: 0.8rem; font-weight: 600; }
        .price-display { color: #16a34a; font-size: 1.35rem; font-weight: 800; }
        .map-container { background: #ffffff; border: 1px solid #e2e8f0; padding: 25px; border-radius: 16px; margin-bottom: 30px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02); }
        .footer-container { background-color: #0f172a; color: #94a3b8; padding: 50px 40px; border-radius: 20px; margin-top: 60px; display: flex; justify-content: space-between; flex-wrap: wrap; gap: 30px; border-top: 4px solid #2563eb; }
        .footer-col { flex: 1; min-width: 250px; }
        .footer-col h4 { color: white; font-size: 1.1rem; font-weight: 700; margin-bottom: 15px; }
        .footer-col p, .footer-col ul { font-size: 0.9rem; line-height: 1.7; margin: 0; color: #94a3b8; list-style: none; padding: 0; }
        .footer-col li { margin-bottom: 8px; }
        .footer-bottom { width: 100%; text-align: center; border-top: 1px solid #1e293b; padding-top: 20px; margin-top: 20px; font-size: 0.85rem; color: #64748b; }
    </style>
""", unsafe_allow_html=True)

# Menaxhimi i sesionit dhe persistenca përmes URL Query Params
query_params = st.query_params
is_admin_page = query_params.get("page") == "admin"

if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = (query_params.get("auth") == "true_selected_admin")

if 'user_logged_in' not in st.session_state:
    st.session_state.user_logged_in = False
    st.session_state.user_email = None
    st.session_state.user_name = None
    st.session_state.user_id = None

# Rikupero nga URL nëse ka mbetur i kyçur
if not st.session_state.user_logged_in and "uid" in query_params:
    try:
        saved_uid = int(query_params["uid"])
        res_user = run_query("SELECT id, emri, email FROM perdoruesit WHERE id = ?", (saved_uid,), fetch_all=False)
        if res_user:
            st.session_state.user_logged_in = True
            st.session_state.user_id = res_user[0]
            st.session_state.user_name = res_user[1]
            st.session_state.user_email = res_user[2]
    except Exception:
        pass

if 'selected_qyteti_filter' not in st.session_state:
    st.session_state.selected_qyteti_filter = "Të gjitha"

# --- NAVBAR LART ---
nav_col1, nav_col2, nav_col3, nav_col4 = st.columns([3, 2, 2, 2])
with nav_col1:
    st.markdown("### 🛒 Marketplace Shqipëri")

if 'menu_page' not in st.session_state:
    st.session_state.menu_page = "Kreu"

with nav_col2:
    if st.button("🏠 Kreu", use_container_width=True):
        st.session_state.menu_page = "Kreu"
        st.rerun()
with nav_col3:
    if st.button("➕ Shto Njoftim", use_container_width=True):
        st.session_state.menu_page = "Shto Njoftim"
        st.rerun()
with nav_col4:
    if not st.session_state.user_logged_in:
        if st.button("👤 Kyçu / Regjistrohu", use_container_width=True):
            st.session_state.menu_page = "Auth"
            st.rerun()
    else:
        if st.button(f"👤 {st.session_state.user_name} (Dil)", use_container_width=True):
            st.session_state.user_logged_in = False
            st.session_state.user_email = None
            st.session_state.user_name = None
            st.session_state.user_id = None
            if "uid" in query_params:
                del query_params["uid"]
            st.success("U çkyçët me sukses!")
            st.rerun()

st.markdown("---")

qytetet_lista = ["Të gjitha", "Tiranë", "Durrës", "Vlorë", "Shkodër", "Elbasan", "Fier", "Korçë", "Sarandë", "Gjirokastër", "Berat", "Lushnjë"]
kategorite_lista = ["Të gjitha", "Pasuri e Paluajtshme", "Automjete", "Elektronikë", "Vend Pune", "Të Tjera"]

if is_admin_page:
    st.title("🔒 Paneli i Administrimit")
    if not st.session_state.admin_logged_in:
        with st.form("form_login_admin"):
            username_input = st.text_input("Admin Username")
            password_input = st.text_input("Admin Password", type="password")
            submit_login = st.form_submit_button("Hyr në Admin")
            if submit_login:
                if username_input == "admin" and password_input == "12345":
                    st.session_state.admin_logged_in = True
                    st.query_params["page"] = "admin"
                    st.query_params["auth"] = "true_selected_admin"
                    st.success("Hyrja u krye!")
                    st.rerun()
                else:
                    st.error("Kredenciale të gabuara!")
    else:
        st.success("Jeni i kyçur si Administrator.")
        if st.button("Dil nga Admini"):
            st.session_state.admin_logged_in = False
            st.query_params.clear()
            st.rerun()
            
        st.subheader("📊 Menaxhimi i Sistemit")
        p_count = run_query("SELECT COUNT(*) FROM perdoruesit", fetch_all=False)[0]
        n_count = run_query("SELECT COUNT(*) FROM njoftime", fetch_all=False)[0]
        c1, c2 = st.columns(2)
        c1.metric("Përdorues", p_count)
        c2.metric("Njoftime", n_count)
        
        st.markdown("---")
        st.subheader("📋 Të gjitha Njoftimet")
        njoftimet_all = run_query("SELECT id, titulli, qyteti, cmimi FROM njoftime")
        if njoftimet_all:
            for nj in njoftimet_all:
                col_a, col_b = st.columns([4, 1])
                col_a.write(f"**ID: {nj[0]}** | {nj[1]} | 📍 {nj[2]} | 💰 {nj[3]}")
                if col_b.button("Fshi", key=f"fshi_admin_{nj[0]}"):
                    run_query("DELETE FROM njoftime WHERE id = ?", (nj[0],), commit=True)
                    st.success("Njoftimi u fshi!")
                    st.rerun()

elif st.session_state.menu_page == "Auth":
    st.subheader("Autentikimi në Platformë")
    tab_l, tab_r = st.tabs(["🔑 Kyçu (Login)", "📝 Regjistrohu (Register)"])
    
    with tab_l:
        with st.form("form_login_user"):
            email_l = st.text_input("Email")
            pass_l = st.text_input("Fjalëkalimi", type="password")
            submit_l = st.form_submit_button("Kyçu")
            if submit_l:
                res = run_query("SELECT id, emri, email FROM perdoruesit WHERE email = ?", (email_l,), fetch_all=False)
                if res:
                    st.session_state.user_logged_in = True
                    st.session_state.user_id = res[0]
                    st.session_state.user_name = res[1]
                    st.session_state.user_email = res[2]
                    # Ruajmë ID në URL query params që të mos humbasë gjatë refresh
                    st.query_params["uid"] = str(res[0])
                    st.session_state.menu_page = "Kreu"
                    st.success(f"Mirë se erdhe, {res[1]}!")
                    st.rerun()
                else:
                    st.error("Email i gabuar ose nuk ekziston.")
                    
    with tab_r:
        with st.form("form_register_user"):
            emri_r = st.text_input("Emri Mbiemri")
            email_r = st.text_input("Email Adresa")
            pass_r = st.text_input("Fjalëkalimi", type="password")
            submit_r = st.form_submit_button("Regjistrohu Tani")
            if submit_r:
                if emri_r and email_r:
                    try:
                        run_query("INSERT INTO perdoruesit (emri, email, fjalekalimi) VALUES (?, ?, ?)", (emri_r, email_r, pass_r), commit=True)
                        st.success("Llogaria u krijua me sukses! Tani mund të kyçeni.")
                    except Exception as e:
                        st.error(f"Ky email ekziston tashmë ose pati një gabim: {e}")
                else:
                    st.error("Plotësoni të gjitha fushat.")

elif st.session_state.menu_page == "Shto Njoftim":
    st.subheader("➕ Krijo një Njoftim të Ri me Fusha Specifike")
    if not st.session_state.user_logged_in:
        st.warning("⚠️ Duhet të kyçeni paraprakisht për të postuar një njoftim!")
    else:
        with st.form("form_shto_njoftim", clear_on_submit=True):
            kategoria = st.selectbox("Zgjidh Kategorinë *", kategorite_lista[1:])
            titulli = st.text_input("Titulli i Njoftimit *", placeholder="P.sh. Shitet Apartament 2+1 / Audi A3 / iPhone 15")
            qyteti = st.selectbox("Qyteti *", qytetet_lista[1:])
            cmimi = st.text_input("Çmimi *", placeholder="P.sh. 120,000€, 500 Lekë/dita, Me marrëveshje")
            
            specifike_rez = ""
            st.markdown("---")
            st.markdown(f"#### Detajet Specifike për: **{kategoria}**")
            
            if kategoria == "Pasuri e Paluajtshme":
                c1, c2 = st.columns(2)
                lloji_prones = c1.selectbox("Lloji i Pronës", ["Apartament", "Shtëpi / Vila", "Truall / Tokë", "Dyqan / Ambient Biznesi", "Garazh"])
                siperfaqja = c2.text_input("Sipërfaqja (m²)", placeholder="P.sh. 85 m²")
                
                c3, c4 = st.columns(2)
                dhomat = c3.selectbox("Numri i Dhomave", ["1+1", "2+1", "3+1", "Ambiente Open Space", "Vila e plotë"])
                kati = c4.text_input("Kati", placeholder="P.sh. Kati 3 (me ashensor)")
                specifike_rez = f"Lloji: {lloji_prones} | Sipërfaqja: {siperfaqja} | Dhomat: {dhomat} | Kati: {kati}"
                
            elif kategoria == "Automjete":
                c1, c2, c3 = st.columns(3)
                marka = c1.text_input("Marka", placeholder="P.sh. Audi, Mercedes, BMW")
                modeli = c2.text_input("Modeli", placeholder="P.sh. A3, C-Class, X5")
                viti = c3.text_input("Viti i Prodhimit", placeholder="P.sh. 2018")
                
                c4, c5 = st.columns(2)
                karburanti = c4.selectbox("Karburanti", ["Naftë", "Benzinë", "Hibrid", "Elektrik", "Benzinë + Gaz"])
                kambio = c5.selectbox("Kambio", ["Automatike", "Manuale"])
                kilometrazhi = st.text_input("Kilometrazhi", placeholder="P.sh. 140,000 km")
                specifike_rez = f"Marka/Modeli: {marka} {modeli} | Viti: {viti} | Karburanti: {karburanti} | Kambio: {kambio} | Km: {kilometrazhi}"
                
            elif kategoria == "Elektronikë":
                c1, c2 = st.columns(2)
                pajisja = c1.text_input("Lloji i Pajisjes", placeholder="P.sh. Smartphone, Laptop, TV")
                gjendja = c2.selectbox("Gjendja", ["E re (Kuti)", "E përdorur (Shumë e mirë)", "E përdorur (Me shenja përdorimi)"])
                specifikat = st.text_input("Specifikat Kryesore", placeholder="P.sh. 256GB, 8GB RAM, Ngjyra E zezë")
                specifike_rez = f"Pajisja: {pajisja} | Gjendja: {gjendja} | Specifikat: {specifikat}"
                
            elif kategoria == "Vend Pune":
                c1, c2 = st.columns(2)
                orari = c1.selectbox("Lloji i Kontratës / Orari", ["Full-time", "Part-time", "Sezonale", "Nga shtëpia (Remote)"])
                paga = c2.text_input("Paga (Opsionale)", placeholder="P.sh. 80,000 Lekë ose Komisione")
                kriteret = st.text_input("Kërkesat Kryesore", placeholder="P.sh. Eksperience 2 vjeçare, Gjuha Angleze")
                specifike_rez = f"Orari: {orari} | Paga: {paga} | Kërkesa: {kriteret}"
                
            else:
                specifike_rez = "Njoftim i Përgjithshëm"

            st.markdown("---")
            kontakti = st.text_input("Numri i Telefonit / Kontakti *", placeholder="+355 68...")
            foto_uploaded = st.file_uploader("Ngarko Foto Përfaqësuese (Opsionale)", type=["jpg", "jpeg", "png"])
            pershkrimi = st.text_area("Përshkrimi i Detajuar i Njoftimit *", placeholder="Shkruani informacione shtesë për blerësit ose të interesuarit...")
            
            submit_njoftim = st.form_submit_button("Publiko Njoftimin Tani", use_container_width=True)
            if submit_njoftim:
                if titulli and pershkrimi and kontakti and cmimi:
                    foto_path_str = ""
                    if foto_uploaded is not None:
                        os.makedirs("uploads", exist_ok=True)
                        foto_path_str = os.path.join("uploads", foto_uploaded.name)
                        with open(foto_path_str, "wb") as f:
                            f.write(foto_uploaded.getbuffer())

                    run_query("""
                        INSERT INTO njoftime (titulli, pershkrimi, kategoria, qyteti, cmimi, kontakti, foto, detaje_specifike, perdorues_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (titulli, pershkrimi, kategoria, qyteti, cmimi, kontakti, foto_path_str, specifike_rez, st.session_state.user_id), commit=True)
                    
                    st.success("🎉 Njoftimi u publikua me sukses!")
                    st.session_state.menu_page = "Kreu"
                    st.rerun()
                else:
                    st.error("Ju lutemi plotësoni të gjitha fushat e detyrueshme (Titull, Çmim, Kontakt, Përshkrim).")

else:
    # --- FAQJA KRYESORE (KREU) ---
    st.markdown("""
        <div class="map-container">
            <h3 style="margin-top:0; color: #0f172a;">🗺️ Harta Interaktive e Qyteteve në Shqipëri</h3>
            <p style="color: #475569; font-size: 0.95rem;">Kliko mbi një qytet më poshtë për të filtruar njoftimet në kohë reale:</p>
        </div>
    """, unsafe_allow_html=True)

    qytetet_per_harten = ["Të gjitha", "Tiranë", "Durrës", "Vlorë", "Shkodër", "Elbasan", "Fier", "Korçë", "Sarandë"]
    cols_map = st.columns(5)
    
    for idx, qyt in enumerate(qytetet_per_harten):
        col_target = cols_map[idx % 5]
        with col_target:
            is_active = (st.session_state.selected_qyteti_filter == qyt)
            btn_label = f"📍 {qyt}" if not is_active else f"✅ {qyt}"
            if st.button(btn_label, key=f"map_qyt_{qyt}", use_container_width=True):
                st.session_state.selected_qyteti_filter = qyt
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Sidebar për filtra
    st.sidebar.markdown("## 🔍 Filtrimi i Njoftimeve")
    kerko_tekst = st.sidebar.text_input("Kërko fjalë kyçe", placeholder="P.sh. Audi, iPhone, 2+1...")
    
    zgjidh_kategorine = st.sidebar.selectbox("🏷️ Kategoria", kategorite_lista)
    
    zgjidh_qytetin = st.sidebar.selectbox(
        "📍 Qyteti", 
        qytetet_per_harten, 
        index=qytetet_per_harten.index(st.session_state.selected_qyteti_filter) if st.session_state.selected_qyteti_filter in qytetet_per_harten else 0
    )
    if zgjidh_qytetin != st.session_state.selected_qyteti_filter:
        st.session_state.selected_qyteti_filter = zgjidh_qytetin

    st.subheader(f"📋 Njoftimet e Publikuara {f'(Qyteti: {st.session_state.selected_qyteti_filter})' if st.session_state.selected_qyteti_filter != 'Të gjitha' else ''}")

    query = "SELECT * FROM njoftime WHERE 1=1"
    params = []
    
    if st.session_state.selected_qyteti_filter != "Të gjitha":
        query += " AND qyteti = ?"
        params.append(st.session_state.selected_qyteti_filter)
        
    if zgjidh_kategorine != "Të gjitha":
        query += " AND kategoria = ?"
        params.append(zgjidh_kategorine)
        
    if kerko_tekst:
        query += " AND (titulli LIKE ? OR pershkrimi LIKE ?)"
        params.extend([f"%{kerko_tekst}%", f"%{kerko_tekst}%"])
        
    query += " ORDER BY id DESC"
    rezultatet = run_query(query, params)
    
    if rezultatet:
        for rresht in rezultatet:
            col_img, col_content = st.columns([1, 3])
            
            with col_img:
                if len(rresht) > 7 and rresht[7] and os.path.exists(rresht[7]):
                    st.image(rresht[7], use_column_width=True)
                else:
                    st.markdown("🖼️ *Pa foto*")
                    
            with col_content:
                specifike_html = ""
                if len(rresht) > 8 and rresht[8]:
                    specifike_html = f'<div class="spec-box">⚙️ <b>Detajet:</b> {rresht[8]}</div>'

                st.markdown(f"""
                    <div style="background-color: #ffffff; border: 1px solid #e2e8f0; padding: 20px; border-radius: 12px; margin-bottom: 15px;">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px;">
                            <h3 class="card-title" style="margin:0;">📌 {rresht[1]}</h3>
                            <span class="price-display">{rresht[5]}</span>
                        </div>
                        {specifike_html}
                        <p class="card-desc">{rresht[2]}</p>
                        <div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap; font-size: 0.9rem; border-top: 1px solid #f1f5f9; padding-top: 10px;">
                            <span class="badge-kategoria">🏷️ {rresht[3]}</span>
                            <span class="badge-qyteti">📍 {rresht[4]}</span>
                            <span style="margin-left: auto; color: #1e3a8a;">📞 <b>{rresht[6]}</b></span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("📭 Nuk u gjet asnjë njoftim për këtë qytet ose filtër.")

# --- FOOTER PROFESIONAL ---
st.markdown("""
    <div class="footer-container">
        <div class="footer-col">
            <h4>🛒 Rreth Nesh</h4>
            <p>Marketplace Shqipëri është platforma juaj lider për njoftimet e klasifikuara, pasuritë e paluajtshme, automjetet dhe vendet e punës në çdo qytet.</p>
        </div>
        <div class="footer-col">
            <h4>🏷️ Kategoritë Kryesore</h4>
            <ul>
                <li>• Pasuri e Paluajtshme</li>
                <li>• Automjete & Pjesë Këmbimi</li>
                <li>• Elektronikë & Pajisje</li>
                <li>• Vend Pune</li>
            </ul>
        </div>
        <div class="footer-col">
            <h4>📞 Na Kontaktoni</h4>
            <p>📍 Tiranë, Shqipëri<br>📞 +355 68 46 60 741<br>✉️ info@marketplaceshqiperi.al</p>
        </div>
        <div class="footer-bottom">
            © 2026 Marketplace Shqipëri. Të gjitha të drejtat e rezervuara.
        </div>
    </div>
""", unsafe_allow_html=True)