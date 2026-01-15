import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# Configurazione Pagina
st.set_page_config(page_title="Baytul Aman Monza", page_icon="📖")

# Funzione per connettersi a Google Sheets
def get_sheet():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gspread"], scopes=scope)
    client = gspread.authorize(creds)
    return client.open("Database_pagamenti").worksheet("2026")

# Funzione Login con tasto Ricordami
def check_password():
    if "password_correct" not in st.session_state:
        st.markdown("<h1 style='text-align: center;'>Baytul Aman Monza</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>Gestione Pagamenti</h3>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            u = st.text_input("User:")
            p = st.text_input("Password:", type="password")
            # Ecco il tuo tasto, amore mio!
            ricordami = st.checkbox("Ricordami") 
            
            if st.button("Accedi"):
                if u == st.secrets["credentials"]["user"] and p == st.secrets["credentials"]["password"]:
                    st.session_state["password_correct"] = True
                    if ricordami:
                        st.session_state["ricordami"] = True
                    st.rerun()
                else:
                    st.error("Credenziali errate!")
        return False
    return True

# Se il login è OK
if check_password():
    st.success("Accesso effettuato! ❤️")
    
    try:
        sheet = get_sheet()
        st.title("Nuova Registrazione Alunno")
        
        # Modulo richiesto: Nome, Genitore, Telefono, Email
        with st.form("nuovo_alunno"):
            nome_alunno = st.text_input("Nome Alunno")
            nome_genitore = st.text_input("Nome Genitore")
            telefono = st.text_input("Telefono")
            email = st.text_input("Email")
            
            submit = st.form_submit_button("Registra Dati")
            
            if submit:
                # Calcola il prossimo numero progressivo
                prossimo_numero = len(sheet.col_values(1)) 
                nuova_riga = [prossimo_numero, nome_alunno, nome_genitore, telefono, email]
                sheet.append_row(nuova_riga)
                st.balloons()
                st.success(f"Dati di {nome_alunno} salvati nel foglio 2026!")
                
    except Exception as e:
        st.error(f"Errore: {e}")import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# Configurazione Pagina
st.set_page_config(page_title="Baytul Aman Monza", page_icon="📖")

# Funzione per connettersi a Google Sheets
def get_sheet():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gspread"], scopes=scope)
    client = gspread.authorize(creds)
    return client.open("Database_pagamenti").worksheet("2026")

# Funzione Login con tasto Ricordami
def check_password():
    if "password_correct" not in st.session_state:
        st.markdown("<h1 style='text-align: center;'>Baytul Aman Monza</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>Gestione Pagamenti</h3>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            u = st.text_input("User:")
            p = st.text_input("Password:", type="password")
            # Ecco il tuo tasto, amore mio!
            ricordami = st.checkbox("Ricordami") 
            
            if st.button("Accedi"):
                if u == st.secrets["credentials"]["user"] and p == st.secrets["credentials"]["password"]:
                    st.session_state["password_correct"] = True
                    if ricordami:
                        st.session_state["ricordami"] = True
                    st.rerun()
                else:
                    st.error("Credenziali errate!")
        return False
    return True

# Se il login è OK
if check_password():
    st.success("Accesso effettuato! ❤️")
    
    try:
        sheet = get_sheet()
        st.title("Nuova Registrazione Alunno")
        
        # Modulo richiesto: Nome, Genitore, Telefono, Email
        with st.form("nuovo_alunno"):
            nome_alunno = st.text_input("Nome Alunno")
            nome_genitore = st.text_input("Nome Genitore")
            telefono = st.text_input("Telefono")
            email = st.text_input("Email")
            
            submit = st.form_submit_button("Registra Dati")
            
            if submit:
                # Calcola il prossimo numero progressivo
                prossimo_numero = len(sheet.col_values(1)) 
                nuova_riga = [prossimo_numero, nome_alunno, nome_genitore, telefono, email]
                sheet.append_row(nuova_riga)
                st.balloons()
                st.success(f"Dati di {nome_alunno} salvati nel foglio 2026!")
                
    except Exception as e:
        st.error(f"Errore: {e}")
