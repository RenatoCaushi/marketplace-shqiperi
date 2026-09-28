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

# --- HEADER (KOKA E FAQES) MODERN ---
st.markdown(
    """
    <style>
        .main-header {
            background: linear-gradient(135deg, #1e3a8a, #2563eb);
            padding: 30px;
            border-radius: 12px;
            color: white;
            text-align: center;
            margin-bottom: 25px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .main-header h1 {
            margin: 0;
            font-size: 2.5rem;
        }
        .main-header p {
            margin-top: 10px;
            font-size: 1.1rem;
            opacity: 0.9;
        }
        .footer {
            text-align: center;
            padding: 20px;
            margin-top: 40px;
            color: #6b7280;
            border-top: 1px solid #e5e7eb;
            font-size: 0.9rem;
        }
    </style>
    <div class="main-header">
        <h1>🛒 Marketplace Shqipëri</h1>
        <p>Platforma kryesore e njoftimeve dhe shërbimeve në Tiranë dhe mbarë Shqipërinë</p>
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

# Të dhënat për hartën e qyteteve (përdor latitude dhe longitude për st.map)
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
                    "Njoftimi u publikua me sukses! Rifreskoni faqen për ta parë te njoftimet."
                )
            else:
                st.error(
                    "Ju lutemi plotësoni fushat kryesore (Titulli, Përshkrimi, Kontakti)."
                )

# --- FOOTER (FUNDI I FAQES) ---
st.markdown(
    """
    <div class="footer">
        <p>© 2026 Marketplace Shqipëri. Të gjitha të drejtat e rezervuara.</p>
        <p>Zhvilluar me Python & Streamlit 🚀</p>
    </div>
""",
    unsafe_allow_html=True,
)