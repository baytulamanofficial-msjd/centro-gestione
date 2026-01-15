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
            st.session_state["num_figli"] = 1
            st.session_state["pagina"] = "menu"
            st.rerun()
        st.title("Nuova Registrazione")
        
        try:
            sheet = get_sheet()
            lista_mesi = ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", 
                          "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]

            # Contenitore per i nomi degli alunni (fuori dal form per permettere il "+" dinamico)
            with st.container():
                nomi_alunni = []
                col_nome, col_piu = st.columns([0.9, 0.1])
                with col_nome:
                    nomi_alunni.append(st.text_input("Nome Alunno 1", key="alunno_1"))
                with col_piu:
                    st.write(" ")
                    st.write(" ")
                    if st.button("➕", help="Aggiungi un altro figlio"):
                        if st.session_state["num_figli"] < 7:
                            st.session_state["num_figli"] += 1
                            st.rerun()
                
                for i in range(2, st.session_state["num_figli"] + 1):
                    nomi_alunni.append(st.text_input(f"Nome Alunno {i}", key=f"alunno_{i}"))

            # Form per il resto dei dati
            with st.form("modulo_dati_completo"):
                nome_genitore = st.text_input("Nome Genitore")
                telefono = st.text_input("Telefono")
                email = st.text_input("Email")
                
                tipo_pagamento = st.radio("Seleziona modalità pagamento:", ["Un mese", "Più mesi"], horizontal=True)
                
                # Sezione Mesi Dinamica
                mese_da, mese_a, mese_selezione = None, None, None
                
                # Usiamo un contenitore vuoto per far apparire i campi giusti
                if tipo_pagamento == "Un mese":
                    mese_selezione = st.selectbox("Seleziona il mese:", [""] + lista_mesi)
                else:
                    col_m1, col_m2 = st.columns(2)
                    with col_m1:
                        mese_da = st.selectbox("Da:", [""] + lista_mesi)
                    with col_m2:
                        mese_a = st.selectbox("A:", [""] + lista_mesi)
                
                col_a, col_b = st.columns(2)
                with col_a:
                    importo = st.number_input("Importo (€):", min_value=0, value=0)
                with col_b:
                    data_pagamento = st.date_input("Data pagamento:", datetime.now())

                responsabile = st.text_input("Responsabile:", value="Sheikh Mahdy Hasan")
                
                submit = st.form_submit_button("Salva Tutti")
                
                if submit:
                    errori = []
                    if not nomi_alunni[0]: errori.append("Nome Alunno")
                    if not nome_genitore: errori.append("Nome Genitore")
                    if not email: errori.append("Email")
                    if importo <= 0: errori.append("Importo")
                    
                    if tipo_pagamento == "Un mese" and not mese_selezione: errori.append("Mese")
                    if tipo_pagamento == "Più mesi" and (not mese_da or not mese_a): errori.append("Mesi (Da/A)")

                    if errori:
                        st.error(f"⚠️ Per favore, compila i seguenti campi mancanti: {', '.join(errori)}")
                    else:
                        # CONTROLLO ESISTENZA
                        nomi_esistenti = sheet.col_values(2)
                        nomi_esistenti = [n.strip().lower() for n in nomi_esistenti]
                        
                        prossimo_id = len([x for x in sheet.col_values(1) if x])
                        registrati = 0
                        
                        mese_testo = mese_selezione if tipo_pagamento == "Un mese" else f"{mese_da}-{mese_a}"
                        
                        for nome in nomi_alunni:
                            if nome and nome.strip():
                                if nome.strip().lower() in nomi_esistenti:
                                    st.warning(f"⚠️ L'alunno '{nome}' è già nel database. Salto riga.")
                                else:
                                    nuova_riga = [prossimo_id + registrati, nome, nome_genitore, telefono, email, importo, str(data_pagamento), responsabile, mese_testo]
                                    sheet.append_row(nuova_riga)
                                    registrati += 1
                        
                        if registrati > 0:
                            st.success(f"Registrato con successo {registrati} alunni! ❤️")
                            st.balloons()
                            st.session_state["num_figli"] = 1
                            st.rerun()
                        
        except Exception as e:
            st.error(f"Errore tecnico: {e}")

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
