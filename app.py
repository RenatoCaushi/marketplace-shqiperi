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

# Krijimi/Lidhja me bazën e të dhënave SQLite
conn = sqlite3.connect("njoftime.db", check_same_thread=False)
cursor = conn.cursor()

# Sigurohemi që tabela ekziston
cursor.execute("""
    CREATE TABLE IF NOT EXISTS njoftime (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulli TEXT,
        pershkrimi TEXT,
        kategoria TEXT,
        qyteti TEXT,
        cmimi REAL,
        kontakti TEXT
    )
""")
conn.commit()

# --- STILIZIMI I AVANCUAR CSS ---
st.markdown(
    """
    <style>
        .stApp {
            background-color: #f8fafc;
        }
        .hero-section {
            background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
            padding: 40px 30px;
            border-radius: 16px;
            color: white;
            box-shadow: 0 10px 25px -5px rgba(30, 58, 138, 0.3);
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .hero-title {
            font-size: 2.5rem;
            font-weight: 800;
            margin: 0;
            letter-spacing: -0.5px;
        }
        .hero-subtitle {
            font-size: 1.1rem;
            margin-top: 8px;
            opacity: 0.85;
        }
        .njoftim-card {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            padding: 24px;
            border-radius: 14px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            transition: all 0.3s ease;
        }
        .njoftim-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 20px -3px rgba(0, 0, 0, 0.08);
            border-color: #cbd5e1;
        }
        .card-title {
            color: #0f172a;
            font-size: 1.35rem;
            font-weight: 700;
            margin: 0 0 10px 0;
        }
        .card-desc {
            color: #475569;
            font-size: 0.98rem;
            line-height: 1.5;
            margin-bottom: 16px;
        }
        .badge-kategoria {
            background-color: #eff6ff;
            color: #2563eb;
            padding: 6px 14px;
            border-radius: 30px;
            font-size: 0.82rem;
            font-weight: 600;
        }
        .price-display {
            color: #16a34a;
            font-size: 1.4rem;
            font-weight: 800;
        }
        .footer-box {
            background-color: #0f172a;
            color: #94a3b8;
            padding: 50px 40px 30px 40px;
            border-radius: 16px;
            margin-top: 60px;
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 30px;
        }
        .footer-col {
            flex: 1;
            min-width: 260px;
        }
        .footer-col h3 {
            color: white;
            font-size: 1.15rem;
            font-weight: 700;
            margin-bottom: 18px;
            border-bottom: 2px solid #2563eb;
            display: inline-block;
            padding-bottom: 4px;
        }
        .footer-col p, .footer-col ul {
            font-size: 0.92rem;
            line-height: 1.7;
            margin: 0;
            list-style: none;
            padding: 0;
        }
        .footer-col li {
            margin-bottom: 10px;
        }
    </style>
    
    <div class="hero-section">
        <div>
            <div class="hero-title">🛒 Marketplace Shqipëri</div>
            <div class="hero-subtitle">Destinacioni kryesor, më i shpejtë dhe i besueshëm për njoftimet tuaja në Shqipëri.</div>
        </div>
    </div>
""",
    unsafe_allow_html=True,
)

# --- STATISTIKA TË SHPEJTA ---
cursor.execute("SELECT COUNT(*) FROM njoftime")
total_njoftime = cursor.fetchone()[0]

col_m1, col_m2, col_m3, col_m4 = st.columns(4)
with col_m1:
    st.metric(label="📊 Njoftime Aktive", value=f"{total_njoftime} Njoftime")
with col_m2:
    st.metric(label="🏙️ Qytete Kryesore", value="6 Qytete")
with col_m3:
    st.metric(label="🔒 Besueshmëria", value="100%")
with col_m4:
    st.metric(label="⚡ Shpejtësia", value="24/7")

st.markdown("<br>", unsafe_allow_html=True)

# --- SHIRITI ANËSOR (SIDEBAR) PËR FILTRAT ---
st.sidebar.markdown("## 🔍 Kërkimi & Filtrimi")
kerko_tekst = st.sidebar.text_input(
    "Kërko me fjalë kyçe", placeholder="P.sh. iPhone, BMW..."
)

qytetet = [
    "Të gjitha",
    "Tiranë",
    "Durrës",
    "Vlorë",
    "Shkodër",
    "Elbasan",
    "Fier",
]
zgjidh_qytetin = st.sidebar.selectbox("📍 Filtro sipas Qytetit", qytetet)

kategorite = [
    "Të gjitha",
    "Puna / Vende Lirë",
    "Automjete",
    "Prona / Qira",
    "Elektronikë",
    "Të Tjera",
]
zgjidh_kategorine = st.sidebar.selectbox("🏷️ Filtro sipas Kategorisë", kategorite)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📍 Qendrat Kryesore në Hartë")
df_hartë = pd.DataFrame({
    "lat": [41.3275, 41.3246, 40.465, 42.0683, 41.1125, 40.7239],
    "lon": [19.8187, 19.4565, 19.4913, 19.5126, 20.0822, 19.5561],
})
st.sidebar.map(df_hartë, zoom=5, use_container_width=True)


# --- TABS (Shtuar edhe Paneli i Adminit) ---
tab1, tab2, tab3 = st.tabs(
    [
        "📋 Shiko Njoftimet Aktive",
        "➕ Shto Njoftim të Ri",
        "⚙️ Paneli i Adminit",
    ]
)

with tab1:
    st.subheader("Njoftimet e Publikuara në Platformë")

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
    cursor.execute(query, params)
    rezultatet = cursor.fetchall()

    if rezultatet:
        st.markdown(
            f"<p style='color: #64748b; font-size: 0.9rem;'>U gjetën <b>{len(rezultatet)}</b> njoftime aktive.</p>",
            unsafe_allow_html=True,
        )
        for rresht in rezultatet:
            st.markdown(
                f"""
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
            """,
                unsafe_allow_html=True,
            )
    else:
        st.info(
            "📭 Nuk u gjet asnjë njoftim që përkon me kriteret tuaja. Mund të kaloni te skeda tjetër për të shtuar njoftimin tuaj të parë!"
        )

with tab2:
    st.subheader("Krijo Njoftim të Ri")
    st.markdown(
        "<p style='color: #475569;'>Plotësoni të dhënat e mëposhtme për të shfaqur njoftimin tuaj menjëherë në faqe.</p>",
        unsafe_allow_html=True,
    )

    with st.form("formular_njoftimi", clear_on_submit=True):
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            titulli = st.text_input(
                "Titulli i Njoftimit *",
                placeholder="P.sh. Shitet Audi A3 Sedan",
            )
            kategoria = st.selectbox("Kategoria *", kategorite[1:])
            cmimi = st.number_input(
                "Çmimi (€) *", min_value=0.0, format="%.2f", value=0.0
            )
        with col_f2:
            qyteti = st.selectbox("Qyteti *", qytetet[1:])
            kontakti = st.text_input(
                "Numri i Telefonit / Email *", placeholder="+355 68..."
            )

        pershkrimi = st.text_area(
            "Përshkrimi i Detajuar *",
            placeholder="Shkruani detajet kryesore të produktit, gjendjen, kushtet...",
        )

        st.markdown("<br>", unsafe_allow_html=True)
        submit = st.form_submit_button(
            "🚀 Publiko Njoftimin Tani", use_container_width=True
        )

        if submit:
            if titulli and pershkrimi and kontakti:
                cursor.execute(
                    """
                    INSERT INTO njoftime (titulli, pershkrimi, kategoria, qyteti, cmimi, kontakti)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (titulli, pershkrimi, kategoria, qyteti, cmimi, kontakti),
                )
                conn.commit()
                st.success(
                    "🎉 Njoftimi u publikua me sukses! Klikoni te skeda e parë për ta parë."
                )
            else:
                st.error(
                    "⚠️ Ju lutemi plotësoni fushat e detyrueshme (Titulli, Përshkrimi, Kontakti)."
                )

with tab3:
    st.subheader("⚙️ Paneli i Menaxhimit të Administratorit")
    st.markdown(
        "Këtu mund të shihni listën e plotë të njoftimeve dhe të fshini çdo njoftim që nuk është i përshtatshëm."
    )

    cursor.execute("SELECT id, titulli, kategoria, qyteti, cmimi FROM njoftime")
    admin_rezultate = cursor.fetchall()

    if admin_rezultate:
        for item in admin_rezultate:
            col_a1, col_a2 = st.columns([4, 1])
            with col_a1:
                st.write(
                    f"**ID: {item[0]}** | 📌 {item[1]} | 🏷️ {item[2]} | 📍 {item[3]} | 💰 {item[4]}€"
                )
            with col_a2:
                if st.button("Fshi", key=f"fshi_{item[0]}"):
                    cursor.execute(
                        "DELETE FROM njoftime WHERE id = ?", (item[0],)
                    )
                    conn.commit()
                    st.success(f"Njoftimi me ID {item[0]} u fshi!")
                    st.rerun()
    else:
        st.info("Nuk ka asnjë njoftim për të menaxhuar në databazë.")

# --- FOOTER ---
st.markdown(
    """
    <div class="footer-box">
        <div class="footer-col">
            <h3>Rreth Marketplace Shqipëri</h3>
            <p>Platforma juaj e besuar për blerjen, shitjen dhe dhënien me qira të automjeteve, pasurive të paluajtshme, pajisjeve elektronike dhe shërbimeve në të gjithë territorin e Shqipërisë.</p>
        </div>
        <div class="footer-col">
            <h3>Kategoritë Kryesore</h3>
            <ul>
                <li>🚗 Automjete & Pjesë Këmbimi</li>
                <li>🏠 Pasuri të Paluajtshme</li>
                <li>💻 Elektronikë & Teknologji</li>
                <li>🛠️ Punë & Shërbime Profesionale</li>
            </ul>
        </div>
        <div class="footer-col">
            <h3>Na Kontaktoni</h3>
            <ul>
                <li>📍 Tiranë, Shqipëri</li>
                <li>✉️ info@marketplace.al</li>
                <li>📞 +355 68 46 60 741</li>
            </ul>
        </div>
    </div>
""",
    unsafe_allow_html=True,
)