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
                    st.session_state["pagina"] = "menu" # Imposta la pagina iniziale dopo il login
                    st.rerun()
                else:
                    st.error("Credenziali errate!")
        return False
    return True

# --- LOGICA DELL'APP DOPO IL LOGIN ---
if check_password():
    
    # Inizializziamo la pagina se non esiste
    if "pagina" not in st.session_state:
        st.session_state["pagina"] = "menu"

    # --- INTERFACCIA: MENU PRINCIPALE ---
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

    # --- INTERFACCIA: REGISTRAZIONE DATI ---
    elif st.session_state["pagina"] == "registro":
        if st.button("⬅️ Torna al Menu"):
            st.session_state["pagina"] = "menu"
            st.rerun()
            
        st.title("Nuova Registrazione Pagamento")
        try:
            sheet = get_sheet()
            with st.form("modulo_dati"):
                nome_alunno = st.text_input("Nome Alunno")
                nome_genitore = st.text_input("Nome Genitore")
                telefono = st.text_input("Telefono")
                email = st.text_input("Email")
                submit = st.form_submit_button("Salva nel Database")
                
                if submit:
                    prossimo_numero = len(sheet.col_values(1))
                    nuova_riga = [prossimo_numero, nome_alunno, nome_genitore, telefono, email]
                    sheet.append_row(nuova_riga)
                    st.success(f"Dati di {nome_alunno} registrati!")
                    st.balloons()
        except Exception as e:
            st.error(f"Errore: {e}")

    # --- INTERFACCIA: VISUALIZZAZIONE DATABASE ---
    elif st.session_state["pagina"] == "visualizza":
        if st.button("⬅️ Torna al Menu"):
            st.session_state["pagina"] = "menu"
            st.rerun()
            
        st.title("Visualizzazione Database (Sola Lettura)")
        try:
            sheet = get_sheet()
            data = sheet.get_all_records()
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True) # Mostra la tabella bella ordinata
        except Exception as e:
            st.error(f"Errore nel caricamento dati: {e}")
