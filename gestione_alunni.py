import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# =====================
# --- REGISTRA NUOVO ALUNNO ---
# =====================
def registra_alunno():
    st.title("➕ Registra Nuovo Alunno")

    # ⬅️ Torna al menu
    if st.button("⬅️ Torna al Menu"):
        st.session_state["pagina"] = "menu"
        st.rerun()

    # --- Form per inserire dati ---
    with st.form("form_nuovo_alunno"):
        nome_alunno = st.text_input("Nome Alunno")
        nome_genitore = st.text_input("Nome Genitore")
        telefono = st.text_input("Telefono")
        email = st.text_input("Email")
        submit = st.form_submit_button("Salva")

    if submit:
        # --- Controllo campi obbligatori ---
        errori = []
        if not nome_alunno.strip():
            errori.append("Nome Alunno")
        if not nome_genitore.strip():
            errori.append("Nome Genitore")
        if not telefono.strip():
            errori.append("Telefono")
        if not email.strip():
            errori.append("Email")

        if errori:
            st.error(f"⚠️ Campi mancanti: {', '.join(errori)}")
        else:
            # Salviamo i dati nello stato per il popup di conferma
            st.session_state["nuovo_alunno"] = {
                "Nome Alunno": nome_alunno.strip(),
                "Nome Genitore": nome_genitore.strip(),
                "Telefono": telefono.strip(),
                "Email": email.strip()
            }
            st.session_state["conferma_nuovo_alunno"] = True
            st.rerun()

    # --- Popup di conferma ---
    if st.session_state.get("conferma_nuovo_alunno", False):
        dati = st.session_state.get("nuovo_alunno", {})

        st.markdown("## 🔒 Conferma dati nuovo alunno")
        st.info("Controlla attentamente i dati prima di confermare")

        st.markdown(f"**Nome Alunno:** {dati.get('Nome Alunno')}")
        st.markdown(f"**Nome Genitore:** {dati.get('Nome Genitore')}")
        st.markdown(f"**Telefono:** {dati.get('Telefono')}")
        st.markdown(f"**Email:** {dati.get('Email')}")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Modifico!"):
                st.session_state["conferma_nuovo_alunno"] = False
                st.rerun()

        with col2:
            if st.button("Confermo!"):
                try:
                    # --- Connetti a Google Sheet ---
                    scope = [
                        "https://www.googleapis.com/auth/spreadsheets",
                        "https://www.googleapis.com/auth/drive"
                    ]
                    creds = Credentials.from_service_account_info(
                        st.secrets["gspread"],
                        scopes=scope
                    )
                    client = gspread.authorize(creds)
                    spreadsheet = client.open("Database_pagamenti")
                    anno_corrente = str(datetime.now().year)
                    sheet = spreadsheet.worksheet(anno_corrente)

                    # --- Legge tutte le righe esistenti ---
                    all_values = sheet.get_all_values()
                    if len(all_values) < 2:
                        st.error("Foglio non correttamente inizializzato!")
                        st.stop()

                    # Colonne nella riga 2
                    headers = all_values[1]
                    col_ID = headers.index("ID") + 1
                    col_nome_alunno = headers.index("Nome Alunno") + 1
                    col_nome_genitore = headers.index("Nome Genitore") + 1
                    col_telefono = headers.index("Telefono") + 1
                    col_email = headers.index("Email") + 1

                    # Calcolo nuovo ID
                    righe = all_values[2:]  # dati dalla riga 3
                    ultimo_id = 0
                    for r in righe:
                        try:
                            ultimo_id = max(ultimo_id, int(r[col_ID - 1]))
                        except:
                            continue
                    nuovo_id = ultimo_id + 1

                    # --- Nuova riga da appendere ---
                    nuova_riga = [""] * len(headers)
                    nuova_riga[col_ID - 1] = nuovo_id
                    nuova_riga[col_nome_alunno - 1] = dati["Nome Alunno"]
                    nuova_riga[col_nome_genitore - 1] = dati["Nome Genitore"]
                    nuova_riga[col_telefono - 1] = dati["Telefono"]
                    nuova_riga[col_email - 1] = dati["Email"]

                    # Append su Google Sheet
                    sheet.append_row(nuova_riga)

                    st.success(f"✅ Nuovo alunno registrato con ID {nuovo_id}")
                    st.balloons()

                    # reset stato conferma
                    st.session_state["conferma_nuovo_alunno"] = False
                    st.session_state.pop("nuovo_alunno", None)

                except Exception as e:
                    st.error(f"Errore salvataggio su Google Sheet: {e}")


# =====================
# --- ELIMINA ALUNNO ---
# =====================
def elimina_alunno():
    st.title("❌ Elimina Alunno Esistente")

    # ⬅️ Torna al menu
    if st.button("⬅️ Torna al Menu"):
        st.session_state["pagina"] = "menu"
        st.rerun()

    try:
        # --- Connetti a Google Sheet ---
        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = Credentials.from_service_account_info(
            st.secrets["gspread"],
            scopes=scope
        )
        client = gspread.authorize(creds)
        spreadsheet = client.open("Database_pagamenti")
        anno_corrente = str(datetime.now().year)
        sheet = spreadsheet.worksheet(anno_corrente)

        # --- Leggi tutti i dati ---
        all_values = sheet.get_all_values()
        if len(all_values) < 2:
            st.warning("Foglio non correttamente inizializzato!")
            st.stop()

        headers = all_values[1]
        rows = all_values[2:]  # dalla riga 3 in poi

        # Lista alunni e dati mappati
        lista_alunni = [r[headers.index("Nome Alunno")].strip() for r in rows if r[headers.index("Nome Alunno")].strip()]
        dati_alunni = {
            r[headers.index("Nome Alunno")].strip(): {
                "Nome Genitore": r[headers.index("Nome Genitore")].strip(),
                "Telefono": r[headers.index("Telefono")].strip(),
                "Email": r[headers.index("Email")].strip(),
                "Riga": idx + 3  # +3 perché righe 1-2 intestazione
            }
            for idx, r in enumerate(rows)
            if r[headers.index("Nome Alunno")].strip()
        }

    except Exception as e:
        st.error(f"Errore caricamento Google Sheet: {e}")
        st.stop()

    # --- Selezione alunno ---
    nome_alunno = st.selectbox("Seleziona Nome Alunno da eliminare", [""] + lista_alunni, key="alunno_da_eliminare")

    if nome_alunno:
        dati = dati_alunni.get(nome_alunno, {})
        st.text_input("Nome Genitore", value=dati.get("Nome Genitore", ""), disabled=True)
        st.text_input("Telefono", value=dati.get("Telefono", ""), disabled=True)
        st.text_input("Email", value=dati.get("Email", ""), disabled=True)

        if st.button("Elimina"):
            st.session_state["alunno_da_eliminare_dati"] = dati
            st.session_state["conferma_eliminazione"] = True
            st.rerun()

    # --- Popup di conferma ---
    if st.session_state.get("conferma_eliminazione", False):
        dati = st.session_state.get("alunno_da_eliminare_dati", {})

        st.markdown("## 🔒 Conferma Eliminazione")
        st.info("Controlla attentamente i dati prima di confermare")

        st.markdown(f"**Nome Alunno:** {nome_alunno}")
        st.markdown(f"**Nome Genitore:** {dati.get('Nome Genitore')}")
        st.markdown(f"**Telefono:** {dati.get('Telefono')}")
        st.markdown(f"**Email:** {dati.get('Email')}")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Modifico!"):
                st.session_state["conferma_eliminazione"] = False
                st.session_state.pop("alunno_da_eliminare_dati", None)
                st.rerun()

        with col2:
            if st.button("Confermo Eliminazione!"):
                try:
                    riga_da_eliminare = dati.get("Riga")
                    if riga_da_eliminare:
                        sheet.delete_rows(riga_da_eliminare)
                        st.success(f"✅ Alunno '{nome_alunno}' eliminato correttamente")
                        st.balloons()
                    else:
                        st.error("Errore: riga alunno non trovata")

                    # reset stati senza toccare direttamente il widget
                    st.session_state["conferma_eliminazione"] = False
                    st.session_state.pop("alunno_da_eliminare_dati", None)
                    st.rerun()  # ricarica tutto da capo pulito

                except Exception as e:
                    st.error(f"Errore eliminazione su Google Sheet: {e}")



