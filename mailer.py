import smtplib
from email.message import EmailMessage
from datetime import date
import streamlit as st

def invia_ricevuta_email(
    email_destinatario: str,
    nome_genitore: str,
    nome_alunno: str,
    importo: float,
    mesi_pagati: str,
    resp: str
):
    """
    Invia la ricevuta di pagamento via Gmail SMTP
    """

    # 🔐 CONFIGURAZIONE MAIL
    EMAIL_MITTENTE = st.secrets["email"]["user"]
    PASSWORD_APP = st.secrets["email"]["password"]


    # ✉️ OGGETTO
    oggetto = f"Ricevuta di Pagamento - {nome_alunno}"

    # 📝 CORPO MAIL
    corpo = f"""
Assalamualaikum wa rohmatullahi wa barokatuhu.

Gentile sig. {nome_genitore},
Con la presente confermiamo il pagamento per l'alunno: {nome_alunno}.

Dettagli della ricevuta:
- Importo: €{importo}
- Periodo: {mesi_pagati}
- Data: {date.today().strftime("%d/%m/%Y")}
- Ricevuto da: #nome responsabile qua

Questa è una mail automatica, si prega di non rispondere. JazakAllah.
Assalamualaikum wa rohmatullah,
Baytul Aman Monza.
"""

    # 📦 COSTRUZIONE EMAIL
    msg = EmailMessage()
    msg["From"] = EMAIL_MITTENTE
    msg["To"] = email_destinatario
    msg["Subject"] = oggetto
    msg.set_content(corpo)

    # 🚀 INVIO
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_MITTENTE, PASSWORD_APP)
        server.send_message(msg)