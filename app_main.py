import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime

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
    
    # Inizializziamo il numero di figli se non esiste
    if "num_figli" not in st.session_state:
        st.session_state["num_figli"] = 1

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
            st.session_state["num_figli"] = 1 # Reset quando si torna al menu
            st.session_state["pagina"] = "menu"
            st.rerun()
        st.title("Nuova Registrazione")
        
        try:
            sheet = get_sheet()
            lista_mesi = ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", 
                          "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]

            with st.container():
                # Gestione dinamica dei nomi alunni
                nomi_alunni = []
                
                # Prima riga con Nome Alunno e tasto +
                col_nome, col_piu = st.columns([0.9, 0.1])
                with col_nome:
                    nomi_alunni.append(st.text_input("Nome Alunno 1", key="alunno_1"))
                with col_piu:
                    st.write(" ") # Spazio per allineare
                    st.write(" ")
                    if st.button("➕", help="Aggiungi un altro figlio"):
                        if st.session_state["num_figli"] < 7:
                            st.session_state["num_figli"] += 1
                            st.rerun()
                
                # Se ci sono più figli, appaiono le altre caselle sotto
                for i in range(2, st.session_state["num_figli"] + 1):
                    nomi_alunni.append(st.text_input(f"Nome Alunno {i}", key=f"alunno_{i}"))

            with st.form("modulo_dati_fissi"):
                nome_genitore = st.text_input("Nome Genitore")
                telefono = st.text_input("Telefono")
                email = st.text_input("Email")
                
                tipo_pagamento = st.radio("Seleziona modalità pagamento:", ["Un mese", "Più mesi"], horizontal=True)
                
                col_a, col_b = st.columns(2)
                with col_a:
                    importo = st.number_input("Importo (€):", min_value=0, value=50)
                with col_b:
                    data_pagamento = st.date_input("Data pagamento:", datetime.now())

                if tipo_pagamento == "Un mese":
                    mese_selezione = st.selectbox("Seleziona il mese:", lista_mesi)
                else:
                    col_m1, col_m2 = st.columns(2)
                    with col_m1:
                        mese_da = st.selectbox("Da:", lista_mesi)
                    with col_m2:
                        mese_a = st.selectbox("A:", lista_mesi)
                
                responsabile = st.text_input("Responsabile:", value="Sheikh Mahdy Hasan")
                
                submit = st.form_submit_button("Salva Tutti")
                
                if submit:
                    prossimo_numero = len([x for x in sheet.col_values(2) if x])
                    
                    # Ciclo per salvare ogni figlio nel database
                    for i, nome in enumerate(nomi_alunni):
                        if nome: # Salva solo se il campo non è vuoto
                            nuova_riga = [prossimo_numero + i, nome, nome_genitore, telefono, email, importo, str(data_pagamento), responsabile]
                            sheet.append_row(nuova_riga, table_prefix='USER_ENTERED')
                    
                    st.success(f"Registrazione completata per {st.session_state['num_figli']} alunni!")
                    st.balloons()
                    st.session_state["num_figli"] = 1 # Reset dopo il salvataggio
                    
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
