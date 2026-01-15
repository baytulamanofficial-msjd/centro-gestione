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
        dati_list = []

        if len(data_sheet) >= 2:
            headers = data_sheet[1]
            rows = data_sheet[2:]
            df_db = pd.DataFrame(rows, columns=headers)
            for _, r in df_db.iterrows():
                dati_list.append({
                    "Nome Alunno": r.get("Nome Alunno", "").strip(),
                    "Nome Genitore": r.get("Nome Genitore", "").strip(),
                    "Telefono": r.get("Telefono", "").strip(),
                    "Email": r.get("Email", "").strip()
                })

        # --- Liste per menu a tendina ---
        lista_alunni = [""] + [r["Nome Alunno"] for r in dati_list]
        lista_genitori = [""] + [r["Nome Genitore"] for r in dati_list]
        lista_telefono = [""] + [r["Telefono"] for r in dati_list]
        lista_email = [""] + [r["Email"] for r in dati_list]

        # --- Inizializza session_state per autocompletamento ---
        for key in ["alunno_select", "genitore_select", "telefono_select", "email_select"]:
            if key not in st.session_state:
                st.session_state[key] = ""

        # --- Menu a tendina con autocompletamento ---
        col1, col2 = st.columns(2)
        with col1:
            selezione_alunno = st.selectbox("Nome Alunno", lista_alunni, key="alunno_select")
            selezione_genitore = st.selectbox("Nome Genitore", lista_genitori, key="genitore_select")
        with col2:
            selezione_telefono = st.selectbox("Telefono", lista_telefono, key="telefono_select")
            selezione_email = st.selectbox("Email", lista_email, key="email_select")

        # --- Logica di autocompletamento bidirezionale ---
        def aggiorna_campi(campo_modificato):
            record = None
            if campo_modificato == "alunno" and selezione_alunno:
                record = next((r for r in dati_list if r["Nome Alunno"] == selezione_alunno), None)
            elif campo_modificato == "genitore" and selezione_genitore:
                record = next((r for r in dati_list if r["Nome Genitore"] == selezione_genitore), None)
            elif campo_modificato == "telefono" and selezione_telefono:
                record = next((r for r in dati_list if r["Telefono"] == selezione_telefono), None)
            elif campo_modificato == "email" and selezione_email:
                record = next((r for r in dati_list if r["Email"] == selezione_email), None)

            if record:
                st.session_state["alunno_select"] = record["Nome Alunno"]
                st.session_state["genitore_select"] = record["Nome Genitore"]
                st.session_state["telefono_select"] = record["Telefono"]
                st.session_state["email_select"] = record["Email"]

        # Applica autocompletamento per tutti i campi
        aggiorna_campi("alunno")
        aggiorna_campi("genitore")
        aggiorna_campi("telefono")
        aggiorna_campi("email")

        # --- Nomi Alunni aggiuntivi (dal 2 in poi) ---
        nomi_alunni = [st.session_state["alunno_select"]]
        if st.button("➕"):
            if st.session_state["num_figli"] < 7:
                st.session_state["num_figli"] += 1
                st.rerun()

        for i in range(2, st.session_state["num_figli"] + 1):
            nomi_alunni.append(st.text_input(f"Nome Alunno {i}", key=f"alunno_{i}"))

        st.write("---")  # separatore fuori dal for

        # --- Altri campi ---
        nome_genitore = st.session_state["genitore_select"]
        telefono = st.session_state["telefono_select"]
        email = st.session_state["email_select"]

        # --- Modalità pagamento e form originale ---
        tipo_pagamento = st.radio(
            "Seleziona modalità pagamento:",
            ["Un mese", "Più mesi"],
            horizontal=True
        )

        mese_da, mese_a, mese_singolo = "", "", ""
        if tipo_pagamento == "Un mese":
            mese_singolo = st.selectbox("Seleziona il mese:", [""] + lista_mesi)
        else:
            st.write("Seleziona l'intervallo di mesi:")
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                mese_da = st.selectbox("Da mese:", [""] + lista_mesi)
            with col_m2:
                mese_a = st.selectbox("Al mese:", [""] + lista_mesi)

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
