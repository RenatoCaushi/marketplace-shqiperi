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
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "njoftime.db")

# 1. INITIALIZIMI DHE MIGRIMI AUTOMATIK I DATABAZËS
def init_database():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS njoftime (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulli TEXT NOT NULL,
            pershkrimi TEXT,
            kategoria TEXT,
            qyteti TEXT,
            cmimi REAL,
            kontakti TEXT
        )
    """)
    
    cursor.execute("PRAGMA table_info(njoftime)")
    existing_columns = [col[1] for col in cursor.fetchall()]
    
    required_columns = {
        "pershkrimi": "TEXT",
        "kategoria": "TEXT",
        "qyteti": "TEXT",
        "cmimi": "REAL",
        "kontakti": "TEXT"
    }
    
    for col_name, col_type in required_columns.items():
        if col_name not in existing_columns:
            try:
                cursor.execute(f"ALTER TABLE njoftime ADD COLUMN {col_name} {col_type}")
            except Exception:
                pass
                
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

# --- STILIZIMI I AVANCUAR CSS ---
st.markdown("""
    <style>
        .stApp { background-color: #f8fafc; }
        .hero-section {
            background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
            padding: 40px 30px;
            border-radius: 16px;
            color: white;
            box-shadow: 0 10px 25px -5px rgba(30, 58, 138, 0.3);
            margin-bottom: 30px;
        }
        .hero-title { font-size: 2.5rem; font-weight: 800; margin: 0; }
        .hero-subtitle { font-size: 1.1rem; margin-top: 8px; opacity: 0.85; }
        .njoftim-card {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            padding: 24px;
            border-radius: 14px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        }
        .card-title { color: #0f172a; font-size: 1.35rem; font-weight: 700; margin: 0 0 10px 0; }
        .card-desc { color: #475569; font-size: 0.98rem; line-height: 1.5; margin-bottom: 16px; }
        .badge-kategoria { background-color: #eff6ff; color: #2563eb; padding: 6px 14px; border-radius: 30px; font-size: 0.82rem; font-weight: 600; }
        .price-display { color: #16a34a; font-size: 1.4rem; font-weight: 800; }
        .footer-box {
            background-color: #0f172a; color: #94a3b8; padding: 50px 40px 30px 40px;
            border-radius: 16px; margin-top: 60px; display: flex; justify-content: space-between; flex-wrap: wrap; gap: 30px;
        }
        .footer-col { flex: 1; min-width: 260px; }
        .footer-col h3 { color: white; font-size: 1.15rem; font-weight: 700; margin-bottom: 18px; border-bottom: 2px solid #2563eb; display: inline-block; padding-bottom: 4px; }
        .footer-col p, .footer-col ul { font-size: 0.92rem; line-height: 1.7; margin: 0; list-style: none; padding: 0; }
        .footer-col li { margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# Menaxhimi i sesionit për login e adminit
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False

query_params = st.query_params
is_admin_page = query_params.get("page") == "admin"

if is_admin_page:
    st.markdown("""
        <div class="hero-section">
            <div class="hero-title">🔒 Paneli i Administrimit (Admin Login)</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Kontrollojmë nëse admini është i kyçur
    if not st.session_state.admin_logged_in:
        with st.form("form_login_admin"):
            username_input = st.text_input("Admin Username")
            password_input = st.text_input("Admin Password", type="password")
            submit_login = st.form_submit_button("Hyr në Admin")
            
            if submit_login:
                if username_input == "admin" and password_input == "12345":
                    st.session_state.admin_logged_in = True
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
        st.subheader("📊 Menaxhimi i Përgjithshëm i Platformës")
        
        total_res = run_query("SELECT COUNT(*) FROM njoftime", fetch_all=False)
        total_njoftime = total_res[0] if total_res else 0
        
        col_stat1, col_stat2 = st.columns(2)
        with col_stat1:
            st.metric(label="Përdorues të Regjistruar", value="Aktivë")
        with col_stat2:
            st.metric(label="Gjithsej Njoftime", value=f"{total_njoftime} Njoftime")
            
        st.markdown("---")
        st.subheader("Lista e Njoftimeve për Menaxhim / Fshirje")
        
        admin_rezultate = run_query("SELECT id, titulli, kategoria, qyteti, cmimi FROM njoftime")
        
        if admin_rezultate:
            for item in admin_rezultate:
                col_a1, col_a2 = st.columns([4, 1])
                with col_a1:
                    st.write(f"**ID: {item[0]}** | 📌 {item[1]} | 🏷️ {item[2]} | 📍 {item[3]} | 💰 {item[4]}€")
                with col_a2:
                    if st.button("Fshi", key=f"fshi_{item[0]}"):
                        run_query("DELETE FROM njoftime WHERE id = ?", (item[0],), fetch_all=False, commit=True)
                        st.success(f"Njoftimi me ID {item[0]} u fshi!")
                        st.rerun()
        else:
            st.info("Nuk ka asnjë njoftim për të menaxhuar në databazë ose tabela është bosh.")

else:
    # --- FAQJA KRYESORE NORMALE ---
    st.markdown("""
        <div class="hero-section">
            <div class="hero-title">🛒 Marketplace Shqipëri</div>
            <div class="hero-subtitle">Destinacioni kryesor për njoftimet tuaja në Shqipëri</div>
        </div>
    """, unsafe_allow_html=True)

    total_res = run_query("SELECT COUNT(*) FROM njoftime", fetch_all=False)
    total_njoftime = total_res[0] if total_res else 0

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1: st.metric(label="📊 Njoftime Aktive", value=f"{total_njoftime} Njoftime")
    with col_m2: st.metric(label="🏙️ Qytete Kryesore", value="6 Qytete")
    with col_m3: st.metric(label="🔒 Besueshmëria", value="100% e Verifikuar")
    with col_m4: st.metric(label="⚡ Shpejtësia", value="24/7")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- SIDEBAR ---
    st.sidebar.markdown("## 🔍 Kërkimi & Filtrimi")
    kerko_tekst = st.sidebar.text_input("Kërko me fjalë kyçe", placeholder="P.sh. iPhone, BMW...")

    qytetet = ["Të gjitha", "Tiranë", "Durrës", "Vlorë", "Shkodër", "Elbasan", "Fier"]
    zgjidh_qytetin = st.sidebar.selectbox("📍 Filtro sipas Qytetit", qytetet)

    kategorite = ["Të gjitha", "Puna / Vende Lirë", "Automjete", "Prona / Qira", "Elektronikë", "Të Tjera"]
    zgjidh_kategorine = st.sidebar.selectbox("🏷️ Filtro sipas Kategorisë", kategorite)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📍 Qendrat Kryesore në Hartë")
    df_hartë = pd.DataFrame({
        "lat": [41.3275, 41.3246, 40.465, 42.0683, 41.1125, 40.7239],
        "lon": [19.8187, 19.4565, 19.4913, 19.5126, 20.0822, 19.5561],
    })
    st.sidebar.map(df_hartë, zoom=5, use_container_width=True)

    tab1, tab2 = st.tabs(["📋 Shiko Njoftimet Aktive", "➕ Shto Njoftim të Ri"])

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
                        <div style="display: flex; gap: 12px; align-items: center; flex-wrap: wrap; font-size: 0.9rem; color: #475569; border-top: 1px solid #f1f5f9; padding-top: 12px;">
                            <span class="badge-kategoria">🏷️ {rresht[3]}</span>
                            <span>📍 <b>{rresht[4]}</b></span>
                            <span style="margin-left: auto;">📞 Kontakti: <b style="color: #1e3a8a;">{rresht[6]}</b></span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("📭 Nuk u gjet asnjë njoftim me këto filtra ose fjalë kërkimi. Provoni të shtoni një të ri!")

    with tab2:
        st.subheader("Krijo Njoftim të Ri")
        with st.form("formular_njoftimi", clear_on_submit=True):
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                titulli = st.text_input("Titulli i Njoftimit *", placeholder="P.sh. Shitet Audi A3 Sedan")
                kategoria = st.selectbox("Kategoria *", kategorite[1:])
                cmimi = st.number_input("Çmimi (€) *", min_value=0.0, format="%.2f", value=0.0)
            with col_f2:
                qyteti = st.selectbox("Qyteti *", qytetet[1:])
                kontakti = st.text_input("Numri i Telefonit / Email *", placeholder="+355 68...")
                
            pershkrimi = st.text_area("Përshkrimi i Detajuar *", placeholder="Shkruani detajet kryesore...")
            
            submit = st.form_submit_button("🚀 Publiko Njoftimin Tani", use_container_width=True)
            
            if submit:
                if titulli and pershkrimi and kontakti:
                    run_query("""
                        INSERT INTO njoftime (titulli, pershkrimi, kategoria, qyteti, cmimi, kontakti)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (titulli, pershkrimi, kategoria, qyteti, cmimi, kontakti), fetch_all=False, commit=True)
                    st.success("🎉 Njoftimi u publikua me sukses!")
                    st.rerun()
                else:
                    st.error("⚠️ Ju lutemi plotësoni fushat e detyrueshme.")

# --- FOOTER ---
st.markdown("""
    <div class="footer-box">
        <div class="footer-col">
            <h3>Rreth Marketplace Shqipëri</h3>
            <p>Platforma juaj e besuar për njoftimet në Shqipëri.</p>
        </div>
        <div class="footer-col">
            <h3>Na Kontaktoni</h3>
            <p>📍 Tiranë, Shqipëri<br>📞 +355 68 46 60 741</p>
        </div>
    </div>
""", unsafe_allow_html=True)