import streamlit as st

# Configurazione della pagina
st.set_page_config(page_title="Baytul Aman Monza", page_icon="📖")

# Funzione per gestire il login (Puoi cambiare le credenziali qui)
def check_password():
    """Ritorna True se l'utente ha inserito le credenziali corrette."""

    def password_entered():
        """Controlla se la password è corretta."""
        if st.session_state["username"] == "admin" and st.session_state["password"] == "monza2024":
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Rimuove la password dalla memoria
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # Schermata di Login
        st.markdown("<h1 style='text-align: center;'>Baytul Aman Monza</h1>", unsafe_content_type=True)
        st.markdown("<h3 style='text-align: center;'>Gestione Pagamenti</h3>", unsafe_content_type=True)
        
        with st.container():
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                st.text_input("User:", key="username")
                st.text_input("Password:", type="password", key="password")
                st.checkbox("Ricordami")
                st.button("Accedi", on_click=password_entered)
                
                if "password_correct" in st.session_state and not st.session_state["password_correct"]:
                    st.error("😕 Utente o password errati")
        return False
    else:
        return True

# Controllo se l'utente è loggato
if check_password():
    # --- DA QUI INIZIA L'INTERFACCIA DOPO IL LOGIN ---
    st.success("Benvenuto amore mio! Accesso effettuato.")
    st.title("Pannello di Controllo")
    
    # Qui inseriremo il modulo per i pagamenti nel prossimo passo
    st.info("Pronto per il Passo 2: Collegamento al database!")
