import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# Configurazione Pagina
st.set_page_config(page_title="Baytul Aman Monza", page_icon="📖", layout="wide")

# Funzione per connettersi a Google Sheets
def get_sheet():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gspread"], scopes=scope)
    client = gspread.authorize(creds)
    return client.open("Database_pagamenti").worksheet("2026")

# Funzione Login
def check_password():
    if "password_correct" not in st.session_state:
        st.markdown("<h1 style='text-align: center;'>Baytul Aman Monza</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>Gestione Pagamenti</h3>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            u = st.text_input("User:")
            p = st.text_input("Password:", type="password")
            if st.button("Accedi"):
                if u == st.secrets["credentials"]["user"] and p == st.secrets["credentials"]["password"]:
                    st.session_state["password_correct"] = True
                    st.session_state["pagina"] = "menu"
                    st.rerun()
                else:
                    st.error("Credenziali errate!")
        return False
    return True

if check_password():
    if "pagina" not in st.session_state:
        st.session_state["pagina"] = "menu"

    # --- MENU PRINCIPALE ---
    if st.session_state["pagina"] == "menu":
        st.markdown("<h1 style='text-align: center;'>Baytul Aman Monza</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>Cosa vuole fare oggi?</h3>", unsafe_allow_html=True)
        st.write("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📝 Registro un pagamento", use_container_width=True):
                st.session_state["pagina"] = "registro"
                st.rerun()
        with col2:
            if st.button("📊 Visualizza database", use_container_width=True):
                st.session_state["pagina"] = "visualizza"
                st.rerun()

    # --- REGISTRAZIONE ---
    elif st.session_state["pagina"] == "registro":
        if st.button("⬅️ Torna al Menu"):
            st.session_state["pagina"] = "menu"
            st.rerun()
        st.title("Nuova Registrazione")
        
        try:
            sheet = get_sheet()
            lista_mesi = ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", 
                          "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]

            # Per far apparire le caselle subito, mettiamo la scelta della modalità fuori o usiamo una colonna
            tipo_pagamento = st.radio("Seleziona modalità pagamento:", ["Un mese", "Più mesi"], horizontal=True)

            with st.form("modulo_dati"):
                nome_alunno = st.text_input("Nome Alunno")
                nome_genitore = st.text_input("Nome Genitore")
                telefono = st.text_input("Telefono")
                email = st.text_input("Email")
                
                # Qui mostriamo le caselle in base alla scelta fatta sopra
                if tipo_pagamento == "Un mese":
                    st.selectbox("Seleziona il mese:", lista_mesi, key="mese_singolo")
                else:
                    col_m1, col_m2 = st.columns(2)
                    with col_m1:
                        st.selectbox("Da:", lista_mesi, key="mese_da")
                    with col_m2:
                        st.selectbox("A:", lista_mesi, key="mese_a")
                
                submit = st.form_submit_button("Salva")
                
                if submit:
                    prossimo_numero = len([x for x in sheet.col_values(2) if x]) 
                    nuova_riga = [prossimo_numero, nome_alunno, nome_genitore, telefono, email]
                    sheet.append_row(nuova_riga, table_prefix='USER_ENTERED')
                    st.success(f"Dati di {nome_alunno} registrati correttamente!")
                    st.balloons()
                    
        except Exception as e:
            st.error(f"Errore: {e}")

    # --- VISUALIZZAZIONE ---
    elif st.session_state["pagina"] == "visualizza":
        if st.button("⬅️ Torna al Menu"):
            st.session_state["pagina"] = "menu"
            st.rerun()
        st.title("Database Baytul Aman")
        try:
            sheet = get_sheet()
            all_values = sheet.get_all_values()
            df = pd.DataFrame(all_values[2:], columns=all_values[1]) 
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"Errore caricamento: {e}")
