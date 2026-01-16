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
            ricordami = st.checkbox("Ricordami")
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
    if st.session_state.get("pagina", "menu") == "menu":
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
    elif st.session_state.get("pagina") == "registro":
        if st.button("⬅️ Torna al Menu"):
            st.session_state["num_figli"] = 1
            st.session_state["pagina"] = "menu"
            st.rerun()

        st.title("Nuova Registrazione")

        try:
            sheet = get_sheet()
            lista_mesi = ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
                          "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]

            # --- Legge dati dal database per completamento automatico ---
            data_sheet = sheet.get_all_values()
            dati_alunni = {}
            lista_alunni = []

            if len(data_sheet) >= 2:
                headers = data_sheet[1]
                rows = data_sheet[2:]
                df_db = pd.DataFrame(rows, columns=headers)

                # Creiamo dizionario per autocompletamento
                for _, r in df_db.iterrows():
                    dati_alunni[r["Nome Alunno"].strip()] = {
                        "Nome Genitore": r.get("Nome Genitore", ""),
                        "Telefono": r.get("Telefono", ""),
                        "Email": r.get("Email", "")
                    }
                lista_alunni = list(dati_alunni.keys())

                        # --- Nomi Alunni con menu a tendina ---
            # Inizializza session_state se non esistono
            if "alunno_1_select" not in st.session_state:
                st.session_state["alunno_1_select"] = ""
            if "genitore_select" not in st.session_state:
                st.session_state["genitore_select"] = ""
            if "telefono_select" not in st.session_state:
                st.session_state["telefono_select"] = ""
            if "email_select" not in st.session_state:
                st.session_state["email_select"] = ""

                        # --- Nome Alunno principale ---
            nomi_alunni = []
            col_nome, col_piu = st.columns([0.9, 0.1])
            with col_nome:
                selezione_alunno = st.selectbox(
                    "Nome Alunno 1",
                    [""] + lista_alunni,
                    key="alunno_1_select"
                )

            with col_piu:
                st.write(" ")
                st.write(" ")
                if st.button("➕"):
                    if st.session_state["num_figli"] < 7:
                        st.session_state["num_figli"] += 1
                        st.rerun()

			# --- Prepara valori autocompilati PRIMA dei selectbox sotto ---
			if selezione_alunno:
				dati = dati_alunni.get(selezione_alunno, {})
				if st.session_state.get("genitore_select") != dati.get("Nome Genitore", ""):
					st.session_state["genitore_select"] = dati.get("Nome Genitore", "")
				if st.session_state.get("telefono_select") != dati.get("Telefono", ""):
					st.session_state["telefono_select"] = dati.get("Telefono", "")
				if st.session_state.get("email_select") != dati.get("Email", ""):
					st.session_state["email_select"] = dati.get("Email", "")

            # --- Altri alunni ---
            for i in range(2, st.session_state["num_figli"] + 1):
                nomi_alunni.append(st.text_input(f"Nome Alunno {i}", key=f"alunno_{i}"))

            st.write("---")

            # --- Liste per menu a tendina ---
            lista_genitori = [d["Nome Genitore"] for d in dati_alunni.values() if d.get("Nome Genitore")]
            lista_email = [d["Email"] for d in dati_alunni.values() if d.get("Email")]
            lista_telefono = [d["Telefono"] for d in dati_alunni.values() if d.get("Telefono")]

            # --- ORA creo i selectbox (dopo aver aggiornato session_state) ---
            col1, col2 = st.columns(2)
            with col1:
                nome_genitore = st.selectbox(
                    "Nome Genitore",
                    [""] + lista_genitori,
                    key="genitore_select"
                )
            with col2:
                telefono = st.selectbox(
                    "Telefono",
                    [""] + lista_telefono,
                    key="telefono_select"
                )

            col3, col4 = st.columns(2)
            with col3:
                email = st.selectbox(
                    "Email",
                    [""] + lista_email,
                    key="email_select"
                )

            # --- Array nomi alunni ---
            nomi_alunni = [st.session_state["alunno_1_select"] if st.session_state["alunno_1_select"] else ""]

            # --- Altri alunni (dal 2 in poi) ---
            for i in range(2, st.session_state["num_figli"] + 1):
                nomi_alunni.append(st.text_input(f"Nome Alunno {i}", key=f"alunno_{i}"))

            st.write("---")  # separatore fuori dal for

            # --- Nomi Alunni / Genitori / Email / Telefono con menu a tendina ---
            lista_genitori = [d.get("Nome Genitore") for d in dati_alunni.values() if d.get("Nome Genitore")]
            lista_email = [d.get("Email") for d in dati_alunni.values() if d.get("Email")]
            lista_telefono = [d.get("Telefono") for d in dati_alunni.values() if d.get("Telefono")]

            # --- Autocompletamento bidirezionale ---
            def aggiorna_session_state(alunno=None, genitore=None, email=None, telefono=None):
                if alunno:
                    dati = dati_alunni.get(alunno, {})
                    st.session_state["genitore_select"] = dati.get("Nome Genitore", "")
                    st.session_state["telefono_select"] = dati.get("Telefono", "")
                    st.session_state["email_select"] = dati.get("Email", "")
                elif genitore:
                    for al, d in dati_alunni.items():
                        if d["Nome Genitore"] == genitore:
                            st.session_state["alunno_1_select"] = al  # <- punta al campo principale con + 
                            st.session_state["telefono_select"] = d.get("Telefono", "")
                            st.session_state["email_select"] = d.get("Email", "")
                            break
                elif email:
                    for al, d in dati_alunni.items():
                        if d["Email"] == email:
                            st.session_state["alunno_1_select"] = al
                            st.session_state["genitore_select"] = d.get("Nome Genitore", "")
                            st.session_state["telefono_select"] = d.get("Telefono", "")
                            break
                elif telefono:
                    for al, d in dati_alunni.items():
                        if d["Telefono"] == telefono:
                            st.session_state["alunno_1_select"] = al
                            st.session_state["genitore_select"] = d.get("Nome Genitore", "")
                            st.session_state["email_select"] = d.get("Email", "")
                            break

			# DISATTIVATO: causava modifica session_state dopo i widget
			# if selezione_alunno:
			# 	aggiorna_session_state(alunno=selezione_alunno)
			# elif st.session_state.get("genitore_select"):
			# 	aggiorna_session_state(genitore=st.session_state["genitore_select"])
			# elif st.session_state.get("email_select"):
			# 	aggiorna_session_state(email=st.session_state["email_select"])
			# elif st.session_state.get("telefono_select"):
			# 	aggiorna_session_state(telefono=st.session_state["telefono_select"])

            # --- Aggiungi al tuo array nomi_alunni per gestione num_figli ---
            nomi_alunni = [st.session_state["alunno_1_select"] if st.session_state["alunno_1_select"] else ""]

                       # --- Filtra mesi non pagati per l'alunno selezionato ---
            mesi_non_pagati = lista_mesi.copy()  # partiamo da tutti i mesi
            if selezione_alunno:
                try:
                    col_mesi = sheet.col_values(9)  # colonna dove sono salvati i mesi (9 = colonna I)
                    col_nomi = sheet.col_values(2)  # colonna Nome Alunno
                    for nome, mese in zip(col_nomi[2:], col_mesi[2:]):  # saltando intestazioni
                        if nome.strip().lower() == selezione_alunno.strip().lower():
                            # rimuovo i mesi già pagati
                            if "Da " in mese or "a " in mese:
                                # caso "Da X a Y"
                                partenza, fine = mese.replace("Da ","").split(" a ")
                                idx_partenza = lista_mesi.index(partenza)
                                idx_fine = lista_mesi.index(fine)
                                for i in range(idx_partenza, idx_fine+1):
                                    if lista_mesi[i] in mesi_non_pagati:
                                        mesi_non_pagati.remove(lista_mesi[i])
                            else:
                                if mese in mesi_non_pagati:
                                    mesi_non_pagati.remove(mese)
                except Exception as e:
                    st.error(f"Errore nel filtrare mesi: {e}")

            # --- Modalità pagamento (reattiva) ---
            tipo_pagamento = st.radio(
                "Seleziona modalità pagamento:",
                ["Un mese", "Più mesi"],
                horizontal=True
            )

                       # --- Mese / Più mesi (aggiornato con mesi non pagati) ---
            mese_da, mese_a, mese_singolo = "", "", ""
            if tipo_pagamento == "Un mese":
                mese_singolo = st.selectbox("Seleziona il mese:", [""] + mesi_non_pagati)
            else:
                st.write("Seleziona l'intervallo di mesi:")
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    mese_da = st.selectbox("Da mese:", [""] + mesi_non_pagati)
                with col_m2:
                    mese_a = st.selectbox("Al mese:", [""] + mesi_non_pagati)

            # --- FORM SOLO PER SALVATAGGIO ---
            with st.form("modulo_dati_fissi"):
                col_imp, col_data = st.columns(2)
                with col_imp:
                    importo = st.number_input("Importo (€):", min_value=0, value=0)
                with col_data:
                    data_pagamento = st.date_input("Data pagamento:", datetime.now())

                responsabile = st.text_input("Responsabile:", value="Sheikh Mahdy Hasan")
                submit = st.form_submit_button("Salva Tutti")

                if submit:
                    errori = []
                    if not nomi_alunni[0]: errori.append("Nome Alunno")
                    if not nome_genitore: errori.append("Nome Genitore")
                    if not email: errori.append("Email")
                    if importo <= 0: errori.append("Importo")

                    if tipo_pagamento == "Un mese" and not mese_singolo: errori.append("Mese")
                    if tipo_pagamento == "Più mesi" and (not mese_da or not mese_a): errori.append("Mesi (Da/A)")

                    if errori:
                        st.error(f"⚠️ Campi mancanti: {', '.join(errori)}")
                    else:
                        nomi_esistenti = [n.strip().lower() for n in sheet.col_values(2)]
                        prossimo_id = len([x for x in sheet.col_values(1) if x])
                        registrati = 0

                        mese_testo = mese_singolo if tipo_pagamento == "Un mese" else f"Da {mese_da} a {mese_a}"

                        for nome in nomi_alunni:
                            if nome and nome.strip():
                                if nome.strip().lower() in nomi_esistenti:
                                    st.warning(f"'{nome}' è già registrato.")
                                else:
                                    riga = [prossimo_id + registrati, nome, nome_genitore, telefono, email, importo, str(data_pagamento), responsabile, mese_testo]
                                    sheet.append_row(riga)
                                    registrati += 1

                        if registrati > 0:
                            st.success("Salvato con successo!")
                            st.balloons()
                            st.session_state["num_figli"] = 1
                            st.rerun()

        except Exception as e:
            st.error(f"Errore: {e}")

    # --- VISUALIZZAZIONE ---
    elif st.session_state.get("pagina") == "visualizza":
        if st.button("⬅️ Torna al Menu"):
            st.session_state["pagina"] = "menu"
            st.rerun()
        st.title("Database")
        try:
            sheet = get_sheet()
            data = sheet.get_all_values()

            # Prima riga vuota, intestazioni nella seconda
            if len(data) < 2:
                st.warning("Database vuoto o senza intestazioni.")
            else:
                headers = data[1]   # seconda riga = intestazioni
                rows = data[2:]     # dati dalla terza in poi
                df = pd.DataFrame(rows, columns=headers)
                st.dataframe(df, use_container_width=True)

        except Exception as e:
            st.error(f"Errore database: {e}")
