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

# --- HEADER STILIZUAR ---
st.markdown(
    """
    <style>
        .main-header {
            background: linear-gradient(135deg, #1e3a8a, #2563eb);
            padding: 25px 30px;
            border-radius: 12px;
            color: white;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 25px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
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
            font-size: 0.95rem;
            opacity: 0.9;
        }
        .footer-box {
            background-color: #0f172a;
            color: #94a3b8;
            padding: 40px 30px 20px 30px;
            border-radius: 12px;
            margin-top: 50px;
            display: flex;
            justify-content: space-between;
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
            <span>Qytetet kryesore: Tiranë, Durrës, Vlorë, Shkodër...</span>
        </div>
    </div>
""",
    unsafe_allow_html=True,
)

# --- SHIRITI ANËSOR (SIDEBAR) PËR FILTRAT DHE HARTËN ---
st.sidebar.markdown("## 🔍 Filtrimi i Njoftimeve")

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

    cursor.execute(query, params)
    rezultatet = cursor.fetchall()

    if rezultatet:
        for rresht in rezultatet:
            with st.container():
                st.markdown(f"### 📌 {rresht[1]}")
                st.write(f"**Përshkrimi:** {rresht[2]}")
                st.info(
                    f"🏷️ **Kategoria:** {rresht[3]} | 📍 **Qyteti:** {rresht[4]} | 💰 **Çmimi:** {rresht[5]} € | 📞 **Kontakti:** {rresht[6]}"
                )
                st.markdown("---")
    else:
        st.warning(
            "Nuk u gjet asnjë njoftim me këto filtra. Provoni të shtoni një të ri!"
        )

with tab2:
    st.subheader("Krijo Njoftim të Ri")

    with st.form("formular_njoftimi", clear_on_submit=True):
        titulli = st.text_input("Titulli i Njoftimit")
        pershkrimi = st.text_area("Përshkrimi i Detajuar")
        kategoria = st.selectbox("Kategoria", kategorite[1:])
        qyteti = st.selectbox("Qyteti", qytetet[1:])
        cmimi = st.number_input("Çmimi (€)", min_value=0.0, format="%.2f")
        kontakti = st.text_input("Numri i Telefonit ose Email")

        submit = st.form_submit_button("Publiko Njoftimin")

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
                    "Njoftimi u publikua me sukses! Rifreskoni faqen për ta parë."
                )
            else:
                st.error(
                    "Ju lutemi plotësoni fushat kryesore (Titulli, Përshkrimi, Kontakti)."
                )

# --- FOOTER ME 3 KOLONA DHE NUMRIN E RI ---
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