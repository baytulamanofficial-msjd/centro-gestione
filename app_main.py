import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# Configurazione della pagina
st.set_page_config(page_title="Baytul Aman Monza", page_icon="📖")

# --- CONNESSIONE AL DATABASE ---
def get_gspread_client():
    scope = ["https://www.googleapis.com/auth/spreadsheets"]
    # Carica le credenziali dal file secrets.toml
    creds = Credentials.from_service_account_info(st.secrets["gspread"], scopes=scope)
    return gspread.authorize(creds)

# --- FUNZIONE LOGIN ---
def check_password():
    if "password_correct" not in st.session_state:
        st.markdown("<h1 style='text-align: center;'>Baytul Aman Monza</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>Gestione Pagamenti</h3>", unsafe_allow_html=True)
        
        with st.container():
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                user_input = st.text_input("User:")
                pass_input = st.text_input("Password:", type="password")
                st.checkbox("Ricordami")
                
                if st.button("Accedi"):
                    if user_input == st.secrets["credentials"]["user"] and pass_input == st.secrets["credentials"]["password"]:
                        st.session_state["password_correct"] = True
                        st.rerun()
                    else:
                        st.error("😕 Credenziali errate")
        return False
    return True

# --- INTERFACCIA PRINCIPALE ---
if check_password():
    try:
        # Mi collego al foglio specifico
        gc = get_gspread_client()
        # Apre il file "Database_pagamenti" e il foglio "2026"
        sh = gc.open("Database_pagamenti").worksheet("2026")
        
        st.title("Gestione Dati Alunni")
        st.write("Compila i campi sottostanti per l'alunno:")

        # Creazione del modulo richiesto
        with st.form("modulo_dati"):
            nome_alunno = st.text_input("Nome Alunno")
            nome_genitore = st.text_input("Nome Genitore")
            telefono = st.text_input("Telefono")
            email = st.text_input("Email")
            
            submit_button = st.form_submit_button(label="Registra Dati")
            
            if submit_button:
                # Logica per aggiungere i dati al foglio (Passo successivo)
                st.success(f"Dati di {nome_alunno} pronti per essere salvati!")

    except Exception as e:
        st.error(f"Errore di connessione al database: {e}")
        st.info("Assicurati di aver condiviso il foglio con l'email del Service Account!")
