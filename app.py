import sqlite3
import streamlit as st
import pandas as pd

# Konfigurimi i faqes
st.set_page_config(
    page_title="Marketplace Shqipëri", page_icon="🛒", layout="wide"
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

# --- STILIZIMET CSS PËR PAMJE PROFESIONALE ---
st.markdown(
    """
    <style>
        .main-header {
            background: linear-gradient(135deg, #1e3a8a, #2563eb);
            padding: 30px;
            border-radius: 12px;
            color: white;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(37, 99, 235, 0.2);
        }
        .main-header h1 {
            margin: 0;
            font-size: 2.2rem;
        }
        .main-header p {
            margin: 5px 0 0 0;
            font-size: 1rem;
            opacity: 0.9;
        }
        .header-right {
            text-align: right;
            font-size: 0.9rem;
            opacity: 0.9;
        }
        /* Kartat e njoftimeve */
        .njoftim-card {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .njoftim-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.05);
        }
        .badge {
            background-color: #eff6ff;
            color: #1d4ed8;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        .price-tag {
            color: #16a34a;
            font-size: 1.2rem;
            font-weight: bold;
        }
        .footer-box {
            background-color: #0f172a;
            color: #94a3b8;
            padding: 40px 30px 20px 30px;
            border-radius: 12px;
            margin-top: 50px;
            display: flex;
            justify-content: space-wrap;
            flex-wrap: wrap;
            gap: 20px;
        }
        .footer-col {
            flex: 1;
            min-width: 250px;
        }
        .footer-col h3 {
            color: white;
            font-size: 1.1rem;
            margin-bottom: 15px;
        }
        .footer-col p, .footer-col ul {
            font-size: 0.9rem;
            line-height: 1.6;
            margin: 0;
            list-style: none;
            padding: 0;
        }
        .footer-col li {
            margin-bottom: 8px;
        }
    </style>
    <div class="main-header">
        <div>
            <h1>🛒 Marketplace Shqipëri</h1>
            <p>Destinacioni kryesor për njoftimet tuaja në Shqipëri</p>
        </div>
        <div class="header-right">
            <span>📍 Tiranë, Durrës, Vlorë, Shkodër...</span>
        </div>
    </div>
""",
    unsafe_allow_html=True,
)

# --- STATISTIKA TË SHPEJTA NË KRYE ---
cursor.execute("SELECT COUNT(*) FROM njoftime")
total_njoftime = cursor.fetchone()[0]

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(
        label="📊 Njoftime Aktive", value=f"{total_njoftime} njoftime"
    )
with col2:
    st.metric(label="🏙️ Qytete të Përfshira", value="6 Qytete")
with col3:
    st.metric(label="🔒 Siguria", value="100% e Verifikuar")

st.markdown("---")

# --- SHIRITI ANËSOR (SIDEBAR) PËR FILTRAT DHE HARTËN ---
st.sidebar.markdown("## 🔍 Kërkimi & Filtrimi")

# Fushë kërkimi me tekst
kerko_tekst = st.sidebar.text_input(
    "Kërko me fjalë kyçe", placeholder="p.sh. iPhone, BMW..."
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
zgjidh_qytetin = st.sidebar.selectbox("Filtro sipas Qytetit", qytetet)

kategorite = [
    "Të gjitha",
    "Puna / Vende Lirë",
    "Automjete",
    "Prona / Qira",
    "Elektronikë",
    "Të Tjera",
]
zgjidh_kategorine = st.sidebar.selectbox("Filtro sipas Kategorisë", kategorite)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📍 Harta e Qendrave")

df_hartë = pd.DataFrame({
    "lat": [41.3275, 41.3246, 40.465, 42.0683, 41.1125, 40.7239],
    "lon": [19.8187, 19.4565, 19.4913, 19.5126, 20.0822, 19.5561],
})
st.sidebar.map(df_hartë, zoom=6, use_container_width=True)


# --- FAQJA KRYESORE (TABS) ---
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

    cursor.execute(query, params)
    rezultatet = cursor.fetchall()

    if rezultatet:
        for rresht in rezultatet:
            # Përdorimi i një dizajni kartë moderne me HTML/CSS
            st.markdown(
                f"""
                <div class="njoftim-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <h3 style="margin: 0; color: #1e293b; font-size: 1.25rem;">📌 {rresht[1]}</h3>
                        <span class="price-tag">{rresht[5]} €</span>
                    </div>
                    <p style="color: #475569; font-size: 0.95rem; margin-bottom: 12px;">{rresht[2]}</p>
                    <div style="display: flex; gap: 10px; font-size: 0.85rem; color: #64748b;">
                        <span class="badge">🏷️ {rresht[3]}</span>
                        <span>📍 <b>{rresht[4]}</b></span>
                        <span>📞 <b>{rresht[6]}</b></span>
                    </div>
                </div>
            """,
                unsafe_allow_html=True,
            )
    else:
        st.warning(
            "Nuk u gjet asnjë njoftim me këto filtra ose fjalë kërkimi. Provoni të shtoni një të ri!"
        )

with tab2:
    st.subheader("Krijo Njoftim të Ri")
    st.write(
        "Plotësoni formën e mëposhtme për të publikuar njoftimin tuaj në platformë."
    )

    with st.form("formular_njoftimi", clear_on_submit=True):
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            titulli = st.text_input(
                "Titulli i Njoftimit", placeholder="P.sh. Shitet iPhone 14 Pro"
            )
            kategoria = st.selectbox("Kategoria", kategorite[1:])
            cmimi = st.number_input(
                "Çmimi (€)", min_value=0.0, format="%.2f", value=0.0
            )
        with col_f2:
            qyteti = st.selectbox("Qyteti", qytetet[1:])
            kontakti = st.text_input(
                "Numri i Telefonit / Email", placeholder="+355 68..."
            )

        pershkrimi = st.text_area(
            "Përshkrimi i Detajuar",
            placeholder="Shkruani detajet e produktit ose shërbimit...",
        )

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
                    "Njoftimi u publikua me sukses! Klikoni te skeda e parë për ta parë."
                )
            else:
                st.error(
                    "Ju lutemi plotësoni fushat kryesore (Titulli, Përshkrimi, Kontakti)."
                )

# --- FOOTER ---
st.markdown(
    """
    <div class="footer-box">
        <div class="footer-col">
            <h3>Rreth Marketplace Shqipëri</h3>
            <p>Platforma juaj e besuar për blerjen, shitjen dhe dhënien me qira të automjeteve, pasurive të paluajtshme, pajisjeve elektronike dhe shërbimeve në të gjithë Shqipërinë.</p>
        </div>
        <div class="footer-col">
            <h3>Kategoritë</h3>
            <ul>
                <li>🚗 Automjete</li>
                <li>🏠 Pasuri të Paluajtshme</li>
                <li>💻 Elektronikë</li>
                <li>🛠️ Punë & Shërbime</li>
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