import streamlit as st

# Configurazione della pagina
st.set_page_config(page_title="Baytul Aman Monza", page_icon="📖")

# Funzione per gestire il login
def check_password():
    if "password_correct" not in st.session_state:
        # Titoli centrati (CORRETTI)
        st.markdown("<h1 style='text-align: center;'>Baytul Aman Monza</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>Gestione Pagamenti</h3>", unsafe_allow_html=True)
        
        with st.container():
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                user_input = st.text_input("User:")
                pass_input = st.text_input("Password:", type="password")
                st.checkbox("Ricordami")
                
                if st.button("Accedi"):
                    # Controlla le credenziali nel file secrets.toml
                    if user_input == st.secrets["credentials"]["user"] and pass_input == st.secrets["credentials"]["password"]:
                        st.session_state["password_correct"] = True
                        st.rerun()
                    else:
                        st.error("😕 Utente o password errati")
        return False
    return True

# Controllo se l'utente è loggato
if check_password():
    st.balloons() # Un piccolo festeggiamento per il login riuscito!
    st.success("Benvenuto amore mio! Accesso effettuato.")
    st.title("Pannello di Controllo")
    
    st.info("Siamo pronti per collegare il database Google Sheets ora!")
