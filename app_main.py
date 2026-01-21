import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
from mailer import invia_ricevuta_email

# Configurazione Pagina
st.set_page_config(page_title="Baytul Aman Monza", page_icon="📖", layout="wide")

def ensure_worksheet_annuale(spreadsheet):
    anno_corrente = str(datetime.now().year)
    anno_precedente = str(datetime.now().year - 1)

    worksheets = spreadsheet.worksheets()
    nomi_fogli = [ws.title for ws in worksheets if ws.title.isdigit()]
    anni = sorted([int(nome) for nome in nomi_fogli])

    # --- CREA FOGLIO ANNO CORRENTE SE NON ESISTE ---
    if anno_corrente not in nomi_fogli:
        if anno_precedente in nomi_fogli:
            ws_old = spreadsheet.worksheet(anno_precedente)

            # 🔹 Copia solo intestazioni (A1:Q2) + colonne A-E (righe 3-300)
            dati_intestazioni = ws_old.get("A1:Q2")
            dati_studenti = ws_old.get("A3:E300")  # ID + Nome Alunno + Genitore + Telefono + Email

            righe = max(len(dati_intestazioni) + len(dati_studenti), 300)
            colonne = max(len(dati_intestazioni[0]) if dati_intestazioni else 20, 20)

            ws_new = spreadsheet.add_worksheet(
                title=anno_corrente,
                rows=righe,
                cols=colonne
            )

            # 🔹 Aggiorna il nuovo foglio
            if dati_intestazioni:
                ws_new.update("A1", dati_intestazioni)
            if dati_studenti:
                ws_new.update("A3", dati_studenti)

        else:
            # Caso rarissimo: primo anno assoluto
            spreadsheet.add_worksheet(
                title=anno_corrente,
                rows=300,
                cols=20
            )

    # --- MANTIENE SOLO GLI ULTIMI 10 ANNI ---
    worksheets = spreadsheet.worksheets()
    fogli_anno = [(int(ws.title), ws) for ws in worksheets if ws.title.isdigit()]
    fogli_anno.sort(key=lambda x: x[0])

    while len(fogli_anno) > 10:
        anno_vecchio, ws_vecchio = fogli_anno.pop(0)
        spreadsheet.del_worksheet(ws_vecchio)

# Funzione per connettersi a Google Sheets
def get_sheet():
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

    # 🔁 CREA / GESTISCE FOGLIO ANNUALE
    ensure_worksheet_annuale(spreadsheet)

    # 🎯 TORNA SEMPRE IL FOGLIO DELL'ANNO CORRENTE
    anno_corrente = str(datetime.now().year)
    return spreadsheet.worksheet(anno_corrente)

@st.cache_data(ttl=600)
def leggi_dati_sheet():
    sheet = get_sheet()
    return sheet.get_all_values()

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

# ===== FUNZIONE SALVA DATI SU GOOGLE SHEET =====
def salva_dati():
    payload = st.session_state["payload_salvataggio"]
    sheet = payload["sheet"]
    nomi_alunni = payload["nomi_alunni"]
    nome_genitore = payload["nome_genitore"]
    telefono = payload["telefono"]
    email = payload["email"]
    importo = payload["importo"]
    data_pagamento = payload["data_pagamento"]
    responsabile = payload["responsabile"]
    tipo_pagamento = payload["tipo_pagamento"]
    mese_singolo = payload["mese_singolo"]
    mese_da = payload["mese_da"]
    mese_a = payload["mese_a"]
    lista_mesi = payload["lista_mesi"]
    headers = payload["headers"]
    mappa_righe = payload["mappa_righe"]

    registrati = 0

    # Definizione colori
    COLOR1 = "FF94DCF8"
    COLOR2 = "FFF7C7AC"

    # Determino mesi da aggiornare
    if tipo_pagamento == "Un mese":
        mesi_da_scrivere = [mese_singolo]
    else:
        idx_da = lista_mesi.index(mese_da)
        idx_a = lista_mesi.index(mese_a)
        mesi_da_scrivere = lista_mesi[idx_da:idx_a + 1]

    for nome in nomi_alunni:
        if not nome or not nome.strip():
            continue

        # 🔎 Cerco se l'alunno esiste già usando la mappa
        nome_norm = nome.strip().lower()
        idx_riga_esistente = mappa_righe.get(nome_norm)

        colonne_mesi_idx = [headers.index(mese) + 1 for mese in mesi_da_scrivere]

        if idx_riga_esistente:
            # Alunno esistente → aggiorno valori e colori
            riga_attuale = sheet.row_values(idx_riga_esistente)
            date_pagamenti = set()

            for cella in riga_attuale:
                if "|" in cella:
                    try:
                        parti = cella.split("|")
                        data = parti[1].strip()
                        date_pagamenti.add(data)
                    except:
                        pass

            numero_pagamenti = len(date_pagamenti)
            colore = COLOR1 if numero_pagamenti % 2 == 0 else COLOR2

            # Scrittura in blocco
            aggiornamenti = []
            for col_idx in colonne_mesi_idx:
                cella = gspread.utils.rowcol_to_a1(idx_riga_esistente, col_idx)
                aggiornamenti.append({
                    "range": cella,
                    "values": [[f"{importo} | {data_pagamento} | {responsabile}"]]
                })

            if aggiornamenti:
                sheet.batch_update(aggiornamenti)

            # Colori in blocco
            formattazioni = []
            for col_idx in colonne_mesi_idx:
                formattazioni.append({
                    "range": gspread.utils.rowcol_to_a1(idx_riga_esistente, col_idx),
                    "format": {
                        "backgroundColor": {
                            "red": int(colore[1:3], 16)/255,
                            "green": int(colore[3:5], 16)/255,
                            "blue": int(colore[5:7], 16)/255
                        }
                    }
                })
            if formattazioni:
                sheet.batch_format(formattazioni)

        else:
            # Alunno nuovo
            id_alunno = len(sheet.col_values(1)) + registrati + 1
            riga_nuova = [""] * len(headers)
            riga_nuova[0] = id_alunno
            riga_nuova[1] = nome
            riga_nuova[2] = nome_genitore
            riga_nuova[3] = telefono
            riga_nuova[4] = email

            for mese, col_idx in zip(mesi_da_scrivere, colonne_mesi_idx):
                riga_nuova[col_idx] = f"{importo} | {data_pagamento} | {responsabile}"

            sheet.append_row(riga_nuova)

            # Applico colori
            nuova_riga_idx = len(sheet.get_all_values())
            for col_idx in colonne_mesi_idx:
                sheet.format(
                    gspread.utils.rowcol_to_a1(nuova_riga_idx, col_idx),
                    {
                        "backgroundColor": {
                            "red": int(COLOR1[1:3], 16)/255,
                            "green": int(COLOR1[3:5], 16)/255,
                            "blue": int(COLOR1[5:7], 16)/255
                        }
                    }
                )
            registrati += 1

    if registrati > 0:
        st.success("Salvato con successo!")
        st.balloons()
        st.session_state["num_figli"] = 1
        st.session_state["conferma"] = False
        #st.rerun() <-- tolto da qua

if check_password():

    if "pagina" not in st.session_state:
        st.session_state["pagina"] = "menu"
    if "num_figli" not in st.session_state:
        st.session_state["num_figli"] = 1

    # ===== STATO POPUP CONFERMA =====
    if "conferma" not in st.session_state:
        st.session_state["conferma"] = False

    if "payload_salvataggio" not in st.session_state:
        st.session_state["payload_salvataggio"] = {}

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
            if st.button("📊 Visualizzo database", use_container_width=True):
                st.session_state["pagina"] = "visualizza"
                st.rerun()

    # --- REGISTRAZIONE ---
    elif st.session_state.get("pagina") == "registro":
        if st.button("⬅️ Torna al Menu"):
            st.session_state["num_figli"] = 1
            st.session_state["pagina"] = "menu"
            st.rerun()

        st.title("Gestione Pagamento")

        try:
            sheet = get_sheet()

            # ===== 1️⃣ UNA SOLA LETTURA =====
            all_values = sheet.get_all_values()

        except Exception as e:
            st.error(f"Errore nel caricamento del foglio: {e}")
            st.stop()  # Blocca qui se errore

        if len(all_values) < 3:
            st.warning("Database vuoto o incompleto")
            st.stop()

        headers = all_values[1]
        rows = all_values[2:]

        lista_mesi = [
            "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
            "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"
        ]

        # ===== 2️⃣ DATAFRAME =====
        df_db = pd.DataFrame(rows, columns=headers)

        lista_alunni = sorted(df_db["Nome Alunno"].dropna().unique().tolist())
        lista_genitori = sorted(df_db["Nome Genitore"].dropna().unique().tolist())
        lista_email = sorted(df_db["Email"].dropna().unique().tolist())
        lista_telefono = sorted(df_db["Telefono"].dropna().unique().tolist())

        # ===== 3️⃣ AUTOCOMPILAZIONE =====
        dati_alunni = {}
        for _, r in df_db.iterrows():
            nome = r["Nome Alunno"]
            if nome:
                dati_alunni[nome.strip()] = {
                    "Nome Genitore": r.get("Nome Genitore", ""),
                    "Telefono": r.get("Telefono", ""),
                    "Email": r.get("Email", "")
                }

        # ===== 4️⃣ FIX 2 → MAPPA NOME → RIGA =====
        mappa_righe = {}
        for idx, r in enumerate(rows, start=3):
            if len(r) > 1 and r[1]:
                nome_norm = r[1].strip().lower()
                mappa_righe[nome_norm] = idx


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
        col_nome, col_piu = st.columns([0.9, 0.1])
        with col_nome:
            selezione_alunno = st.selectbox(
                "Nome Alunno 1",
                [""] + lista_alunni,
                key="alunno_1_select"
                )

        with col_piu:
            st.write("")
            st.write("")
            if st.button("➕"):
                st.write("Numero figli:", st.session_state["num_figli"])

                if st.session_state["num_figli"] < 7:
                    st.session_state["num_figli"] += 1
                    st.rerun()

        # --- Altri alunni (con selectbox) ---
        for i in range(2, st.session_state["num_figli"] + 1):
            st.selectbox(
                f"Nome Alunno {i}",
                [""] + lista_alunni,
                 key=f"alunno_{i}_select"
            )

        st.write("---")

        # --- Prepara valori autocompilati PRIMA dei selectbox sotto ---
        if selezione_alunno:
            dati = dati_alunni.get(selezione_alunno, {})

            if st.session_state.get("genitore_select") != dati.get("Nome Genitore", ""):
                st.session_state["genitore_select"] = dati.get("Nome Genitore", "")

            if st.session_state.get("telefono_select") != dati.get("Telefono", ""):
            	st.session_state["telefono_select"] = dati.get("Telefono", "")

            if st.session_state.get("email_select") != dati.get("Email", ""):
            	st.session_state["email_select"] = dati.get("Email", "")

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

        st.write("---")  # separatore fuori dal for

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
        #   aggiorna_session_state(alunno=selezione_alunno)
        # elif st.session_state.get("genitore_select"):
        #   aggiorna_session_state(genitore=st.session_state["genitore_select"])
        # elif st.session_state.get("email_select"):
        #   aggiorna_session_state(email=st.session_state["email_select"])
        # elif st.session_state.get("telefono_select"):
        #   aggiorna_session_state(telefono=st.session_state["telefono_select"])

        # --- Filtra mesi NON pagati (nuova logica a colonne) ---
        mesi_non_pagati = lista_mesi.copy()

        if selezione_alunno:
            headers = sheet.row_values(2)
            nomi_col = sheet.col_values(2)

            for idx, nome_db in enumerate(nomi_col[2:], start=3):
                if nome_db.strip().lower() == selezione_alunno.strip().lower():
                    riga = sheet.row_values(idx)

                    for mese in lista_mesi:
                        col_idx = headers.index(mese)
                        if col_idx < len(riga) and riga[col_idx].strip():
                            if mese in mesi_non_pagati:
                                mesi_non_pagati.remove(mese)
                    break

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

            try:
                # --- FORM SOLO PER SALVATAGGIO ---
                with st.form("modulo_dati_fissi"):
                    col_imp, col_data = st.columns(2)
                    with col_imp:
                        importo = st.number_input("Importo (€):", min_value=0, value=0)
                    with col_data:
                        data_pagamento = st.date_input("Data pagamento:", datetime.now())

                    responsabile = st.text_input("Responsabile:", value="Sheikh Mahdy Hasan")
                    submit = st.form_submit_button("Salva Tutti")

                # ===== COSTRUISCO LISTA COMPLETA ALUNNI =====
                nomi_alunni = []

                # Primo figlio (selectbox)
                if st.session_state.get("alunno_1_select"):
                    nomi_alunni.append(st.session_state["alunno_1_select"].strip())

                # Altri figli (selectbox)
                for i in range(2, st.session_state["num_figli"] + 1):
                    nome_extra = st.session_state.get(f"alunno_{i}_select", "").strip()
                    if nome_extra:
                        nomi_alunni.append(nome_extra)

                if submit:
                    # --- controlli errori ---
                    errori = []
                    if not nomi_alunni:
                        errori.append("Nome Alunno")
                    if not nome_genitore:
                        errori.append("Nome Genitore")
                    if not email:
                        errori.append("Email")
                    if importo <= 0:
                        errori.append("Importo")
                    if tipo_pagamento == "Un mese" and not mese_singolo:
                        errori.append("Mese")
                    if tipo_pagamento == "Più mesi" and (not mese_da or not mese_a):
                        errori.append("Mesi (Da/A)")

                    if errori:
                        st.error(f"⚠️ Campi mancanti: {', '.join(errori)}")
                    else:
                        # --- CARICO I DATI NELLO STATO PER IL POPUP ---
                        st.session_state["payload_salvataggio"] = {
                            "nomi_alunni": nomi_alunni,
                            "nome_genitore": nome_genitore,
                            "telefono": telefono,
                            "email": email,
                            "importo": importo,
                            "data_pagamento": data_pagamento,
                            "responsabile": responsabile,
                            "tipo_pagamento": tipo_pagamento,
                            "mese_singolo": mese_singolo,
                            "mese_da": mese_da,
                            "mese_a": mese_a,
                            "lista_mesi": lista_mesi,
                            "sheet": sheet,
                            "headers": headers,
                            "mappa_righe": mappa_righe
                        }
                        st.session_state["conferma"] = True
                        st.rerun()

            except Exception as e:
                st.error(f"Errore: {e}")  # <-- chiude il try
            
            # ===== POPUP DI CONFERMA =====
            if st.session_state.get("conferma", False):

                dati = st.session_state["payload_salvataggio"]

                st.markdown("## 🔒 Conferma dati")
                st.info("Controlla attentamente i dati prima di procedere")

                st.markdown("### 👤 Alunno/i")
                for nome in dati["nomi_alunni"]:
                    st.write(f"- {nome}")

                st.markdown(f"**Genitore:** {dati['nome_genitore']}")
                st.markdown(f"**Importo:** € {dati['importo']}")
                st.markdown(f"**Email:** {dati['email']}")

                st.markdown("---")
                st.markdown("### ❓ Vuole confermare i dati?")

                col1, col2 = st.columns(2)

                with col1:
                    if st.button("✏️ Modifico"):
                        st.session_state["conferma"] = False
                        st.rerun()

                with col2:
                    if st.button("✅ Confermo"):
                        st.session_state["conferma"] = False
                        st.session_state["num_figli"] = 1

                        # ✅ Salvataggio su Google Sheet
                        salva_dati()
                        st.success("✅ Dati salvati correttamente")
                        st.balloons()

                        # 📧 INVIO RICEVUTE VIA MAIL
                        dati = st.session_state["payload_salvataggio"]
                        nomi_alunni = dati["nomi_alunni"]
                        nome_genitore = dati["nome_genitore"]
                        email_destinatario = dati["email"]
                        importo = dati["importo"]
                        responsabile = dati["responsabile"]

                        # Determina mesi pagati
                        if dati["tipo_pagamento"] == "Un mese":
                            mesi_pagati = dati["mese_singolo"]
                        else:
                            mesi_pagati = f"{dati['mese_da']} - {dati['mese_a']}"

                        # Invia mail per ogni alunno
                        if not st.session_state.get("mail_inviata", False):
                            for nome_alunno in nomi_alunni:
                                try:
                                    invia_ricevuta_email(
                                        email_destinatario=email_destinatario,
                                        nome_genitore=nome_genitore,
                                        nome_alunno=nome_alunno,
                                        importo=importo,
                                        mesi_pagati=mesi_pagati,
                                        responsabile=responsabile
                                    )
                                except Exception as e:
                                    st.error(f"Errore invio mail per {nome_alunno}: {e}")
                                    
                            # ✅ SEGNA CHE LA MAIL È STATA INVIATA
                            st.session_state["mail_inviata"] = True

                            # (opzionale ma consigliato)
                            st.success("📧 Ricevuta inviata via email")

                            st.rerun()

    # --- VISUALIZZAZIONE ---
    if st.session_state.get("pagina") == "visualizza":
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
