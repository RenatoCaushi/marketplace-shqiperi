import os
import sqlite3
import streamlit as st
import pandas as pd

# Konfigurimi i faqes
st.set_page_config(
    page_title="Marketplace Shqipëri",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Përcaktojmë rrugën absolute të databazës
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "marketplace.db")

# 1. INITIALIZIMI I DATABAZËS
def init_database():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS perdoruesit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emri TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            data_regjistrimit TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS njoftime (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulli TEXT NOT NULL,
            pershkrimi TEXT,
            kategoria TEXT,
            qyteti TEXT,
            cmimi REAL,
            kontakti TEXT,
            perdorues_id INTEGER,
            FOREIGN KEY (perdorues_id) REFERENCES perdoruesit(id)
        )
    """)
    
    conn.commit()
    conn.close()

init_database()

# Funksion i sigurt për queries
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

# --- STILIZIMI I AVANCUAR CSS (MODERN & CLEAN) ---
st.markdown("""
    <style>
        .stApp { background-color: #f8fafc; font-family: 'Inter', sans-serif; }
        
        /* Navbar / Header Modern */
        .main-header {
            background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
            padding: 35px 40px;
            border-radius: 20px;
            color: white;
            box-shadow: 0 10px 25px -5px rgba(30, 58, 138, 0.2);
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header-title { font-size: 2.2rem; font-weight: 800; margin: 0; color: #ffffff; }
        .header-subtitle { font-size: 1.05rem; margin-top: 5px; color: #93c5fd; }
        
        /* Kartat e Njoftimeve */
        .njoftim-card {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            padding: 24px;
            border-radius: 16px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .njoftim-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
        }
        .card-title { color: #0f172a; font-size: 1.3rem; font-weight: 700; margin: 0 0 8px 0; }
        .card-desc { color: #475569; font-size: 0.95rem; line-height: 1.5; margin-bottom: 16px; }
        .badge-kategoria { background-color: #eff6ff; color: #2563eb; padding: 6px 14px; border-radius: 30px; font-size: 0.8rem; font-weight: 600; }
        .badge-qyteti { background-color: #f1f5f9; color: #475569; padding: 6px 14px; border-radius: 30px; font-size: 0.8rem; font-weight: 600; }
        .price-display { color: #16a34a; font-size: 1.35rem; font-weight: 800; }

        /* Seksioni i Hartës Shqipëri / Qytetet */
        .albania-map-box {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            padding: 24px;
            border-radius: 16px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
            margin-bottom: 25px;
        }
        .city-tag {
            display: inline-block;
            background: #f8fafc;
            border: 1px solid #cbd5e1;
            padding: 6px 14px;
            border-radius: 8px;
            font-size: 0.85rem;
            font-weight: 600;
            color: #334155;
            margin: 4px;
        }

        /* Footer i Ri Profesional */
        .footer-container {
            background-color: #0f172a;
            color: #94a3b8;
            padding: 45px 40px;
            border-radius: 20px;
            margin-top: 60px;
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 30px;
            border-top: 4px solid #2563eb;
        }
        .footer-col { flex: 1; min-width: 250px; }
        .footer-col h4 { color: white; font-size: 1.1rem; font-weight: 700; margin-bottom: 15px; }
        .footer-col p { font-size: 0.9rem; line-height: 1.6; margin: 0; color: #94a3b8; }
        .footer-bottom {
            width: 100%;
            text-align: center;
            border-top: 1px solid #1e293b;
            padding-top: 20px;
            margin-top: 20px;
            font-size: 0.85rem;
            color: #64748b;
        }
    </style>
""", unsafe_allow_html=True)

# Menaxhimi i sesionit të Adminit
query_params = st.query_params
is_admin_page = query_params.get("page") == "admin"

if 'admin_logged_in' not in st.session_state:
    if query_params.get("auth") == "true_secure_admin":
        st.session_state.admin_logged_in = True
    else:
        st.session_state.admin_logged_in = False

if is_admin_page:
    st.markdown("""
        <div class="main-header">
            <div>
                <div class="header-title">🔒 Paneli i Administrimit</div>
                <div class="header-subtitle">Menaxhimi i platformës Marketplace Shqipëri</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.admin_logged_in:
        with st.form("form_login_admin"):
            username_input = st.text_input("Admin Username")
            password_input = st.text_input("Admin Password", type="password")
            submit_login = st.form_submit_button("Hyr në Admin")
            
            if submit_login:
                if username_input == "admin" and password_input == "12345":
                    st.session_state.admin_logged_in = True
                    st.query_params["page"] = "admin"
                    st.query_params["auth"] = "true_secure_admin"
                    st.success("Hyrja u krye me sukses!")
                    st.rerun()
                else:
                    st.error("Kredenciale të gabuara për admin!")
    else:
        st.success("Jeni i kyçur si Administrator i Sistemit.")
        
        if st.button("Dil nga Admini"):
            st.session_state.admin_logged_in = False
            st.query_params.clear()
            st.rerun()
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("📊 Statistikat Kryesore")
        
        total_perd_res = run_query("SELECT COUNT(*) FROM perdoruesit", fetch_all=False)
        total_perdorues = total_perd_res[0] if total_perd_res else 0

        total_njof_res = run_query("SELECT COUNT(*) FROM njoftime", fetch_all=False)
        total_njoftime = total_njof_res[0] if total_njof_res else 0
        
        col_stat1, col_stat2 = st.columns(2)
        with col_stat1: st.metric(label="Përdorues të Regjistruar", value=f"{total_perdorues}")
        with col_stat2: st.metric(label="Gjithsej Njoftime", value=f"{total_njoftime}")
            
        st.markdown("---")
        st.subheader("👥 Përdoruesit e Regjistruar")
        perdoruesit_list = run_query("SELECT id, emri, email, data_regjistrimit FROM perdoruesit")
        
        if perdoruesit_list:
            for p in perdoruesit_list:
                st.markdown(f"""
                    <div style="background: #ffffff; padding: 12px 18px; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 8px; font-size: 0.9rem;">
                        <b>ID: {p[0]}</b> | 👤 <b>{p[1]}</b> | ✉️ {p[2]} | 📅 {p[3]}
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Nuk ka përdorues të regjistruar.")

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("📋 Njoftimet e Postuara")
        
        admin_rezultate = run_query("""
            SELECT n.id, n.titulli, n.kategoria, n.qyteti, n.cmimi, p.emri 
            FROM njoftime n 
            LEFT JOIN perdoruesit p ON n.perdorues_id = p.id
        """)
        
        if admin_rezultate:
            for item in admin_rezultate:
                autori = item[5] if item[5] else "I panjohur"
                col_a1, col_a2 = st.columns([4, 1])
                with col_a1:
                    st.write(f"**ID: {item[0]}** | 📌 {item[1]} | 🏷️ {item[2]} | 📍 {item[3]} | 💰 {item[4]}€ | 👤 {autori}")
                with col_a2:
                    if st.button("Fshi", key=f"fshi_{item[0]}"):
                        run_query("DELETE FROM njoftime WHERE id = ?", (item[0],), fetch_all=False, commit=True)
                        st.success(f"Njoftimi u fshi!")
                        st.rerun()
        else:
            st.info("Nuk ka njoftime.")

else:
    # --- FAQJA KRYESORE ---
    st.markdown("""
        <div class="main-header">
            <div>
                <div class="header-title">🛒 Marketplace Shqipëri</div>
                <div class="header-subtitle">Platforma më e besuar për njoftimet dhe shërbimet në Shqipëri</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    total_res = run_query("SELECT COUNT(*) FROM njoftime", fetch_all=False)
    total_njoftime = total_res[0] if total_res else 0

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1: st.metric(label="📊 Njoftime Aktive", value=f"{total_njoftime}")
    with col_m2: st.metric(label="🏙️ Mbulimi", value="Gjithë Shqipëria")
    with col_m3: st.metric(label="🔒 Siguria", value="100% e Verifikuar")
    with col_m4: st.metric(label="⚡ Suporti", value="24/7")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- SIDEBAR MODERN ---
    st.sidebar.markdown("## 🔍 Filtrimi i Njoftimeve")
    kerko_tekst = st.sidebar.text_input("Kërko fjalë kyçe", placeholder="P.sh. iPhone, Audi...")

    qytetet = ["Të gjitha", "Tiranë", "Durrës", "Vlorë", "Shkodër", "Elbasan", "Fier", "Korçë"]
    zgjidh_qytetin = st.sidebar.selectbox("📍 Qyteti", qytetet)

    kategorite = ["Të gjitha", "Puna / Vende Lirë", "Automjete", "Prona / Qira", "Elektronikë", "Të Tjera"]
    zgjidh_kategorine = st.sidebar.selectbox("🏷️ Kategoria", kategorite)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🗺️ Territori i Shqipërisë")
    st.sidebar.markdown("""
        <div style="font-size: 0.85rem; color: #475569; line-height: 1.5;">
            Platforma jonë përfshin të gjitha qarqet kryesore të vendit, duke ju lidhur direkt me blerës dhe shitës lokalë.
        </div>
    """, unsafe_allow_html=True)
    
    # Harta e pastër e fokusuar vetëm në Shqipëri
    df_albania = pd.DataFrame({
        "lat": [41.3275, 41.3246, 40.465, 42.0683, 41.1125, 40.7239, 40.6186],
        "lon": [19.8187, 19.4565, 19.4913, 19.5126, 20.0822, 19.5561, 20.7812],
    })
    st.sidebar.map(df_albania, zoom=6, use_container_width=True)

    tab1, tab2, tab3 = st.tabs(["📋 Shiko Njoftimet", "➕ Shto Njoftim", "👤 Regjistrohu"])

    with tab1:
        st.subheader("Njoftimet e Publikuara")
        
        query = "SELECT * FROM njoftime WHERE 1=1"
        params = []
        
        if zgjidh_qytetin != "Të gjitha":
            query += " AND qyteti = ?"
            params.append(zgjidh_qytetin)
            
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
                st.markdown(f"""
                    <div class="njoftim-card">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px;">
                            <h3 class="card-title">📌 {rresht[1]}</h3>
                            <span class="price-display">{rresht[5]:,.0f} €</span>
                        </div>
                        <p class="card-desc">{rresht[2]}</p>
                        <div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap; font-size: 0.9rem; border-top: 1px solid #f1f5f9; padding-top: 12px;">
                            <span class="badge-kategoria">🏷️ {rresht[3]}</span>
                            <span class="badge-qyteti">📍 {rresht[4]}</span>
                            <span style="margin-left: auto; color: #1e3a8a;">📞 <b>{rresht[6]}</b></span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("📭 Nuk u gjet asnjë njoftim sipas filtrave tuaj.")

    with tab2:
        st.subheader("Krijo Njoftim të Ri")
        
        perdorues_options = run_query("SELECT id, emri FROM perdoruesit")
        perd_dict = {f"{p[1]} (ID: {p[0]})": p[0] for p in perdorues_options} if perdoruesit_options else {}
        
        with st.form("formular_njoftimi", clear_on_submit=True):
            if perd_dict:
                zgjidh_perd_label = st.selectbox("Zgjidh Përdoruesin Që Poston *", list(perd_dict.keys()))
            else:
                st.warning("⚠️ Kujdes: Nuk keni regjistruar asnjë përdorues! Ju lutemi regjistrohuni te skeda e tretë më parë.")
                
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                titulli = st.text_input("Titulli i Njoftimit *", placeholder="P.sh. Shitet Audi A3")
                kategoria = st.selectbox("Kategoria *", kategorite[1:])
                cmimi = st.number_input("Çmimi (€) *", min_value=0.0, format="%.2f", value=0.0)
            with col_f2:
                qyteti = st.selectbox("Qyteti *", qytetet[1:])
                kontakti = st.text_input("Kontakti (Tel / Email) *", placeholder="+355 68...")
                
            pershkrimi = st.text_area("Përshkrimi i Detajuar *", placeholder="Shkruani detajet...")
            
            submit = st.form_submit_button("🚀 Publiko Njoftimin", use_container_width=True)
            
            if submit:
                if titulli and pershkrimi and kontakti and perd_dict:
                    p_id = perd_dict[zgjidh_perd_label]
                    run_query("""
                        INSERT INTO njoftime (titulli, pershkrimi, kategoria, qyteti, cmimi, kontakti, perdorues_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (titulli, pershkrimi, kategoria, qyteti, cmimi, kontakti, p_id), fetch_all=False, commit=True)
                    st.success("🎉 Njoftimi u publikua me sukses!")
                    st.rerun()
                else:
                    st.error("⚠️ Ju lutemi plotësoni fushat dhe zgjidhni një përdorues.")

    with tab3:
        st.subheader("Regjistrohu si Përdorues")
        with st.form("formular_perdoruesi", clear_on_submit=True):
            emri_reg = st.text_input("Emri dhe Mbiemri *", placeholder="P.sh. Arben Hoxha")
            email_reg = st.text_input("Adresa Email *", placeholder="p.sh. arben@example.com")
            
            submit_reg = st.form_submit_button("💾 Regjistrohu", use_container_width=True)
            
            if submit_reg:
                if emri_reg and email_reg:
                    try:
                        run_query("""
                            INSERT INTO perdoruesit (emri, email) VALUES (?, ?)
                        """, (emri_reg, email_reg), fetch_all=False, commit=True)
                        st.success(f"🎉 Përdoruesi '{emri_reg}' u regjistrua me sukses!")
                        st.rerun()
                    except Exception:
                        st.error("⚠️ Ky Email ekziston tashmë në sistem.")
                else:
                    st.error("⚠️ Plotësoni të gjitha fushat.")

# --- FOOTER PROFESIONAL ---
st.markdown("""
    <div class="footer-container">
        <div class="footer-col">
            <h4>🛒 Marketplace Shqipëri</h4>
            <p>Platforma juaj e preferuar për njoftimet e klasifikuara, pronat, mjetet dhe mundësitë e punës në të gjithë Shqipërinë.</p>
        </div>
        <div class="footer-col">
            <h4>🔗 Lidhje të Shpejta</h4>
            <p>• Shiko Njoftimet<br>• Shto Njoftim të Ri<br>• Regjistrohu si Përdorues</p>
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