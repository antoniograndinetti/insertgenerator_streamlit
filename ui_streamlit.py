import streamlit as st
from datetime import date
import windtre_generate_insert as wgi

st.set_page_config(layout="wide")

# Titolo della pagina
st.title("Winday sms plan insert generator")

# Selettori di date
# Disposizione dei selettori di date su una riga
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Data di inizio", value=date.today())
with col2:
    end_date = st.date_input("Data di fine", value=date.today())

# Carica il file
uploaded_file = st.file_uploader("Carica un file di testo", type=["xlsx", "xls"])

if st.button("Conta le righe"):
    if uploaded_file is not None:
        # Lettura del file
        try:
            wgi.generate_insert(uploaded_file, start_date, end_date, st)
            
            # Sezione per mostrare o nascondere testo aggiuntivo
            # show_more = st.checkbox("Mostra/nascondi testo aggiuntivo")
            # if show_more:
            #     st.write("Questo è il testo aggiuntivo che può essere visualizzato o nascosto.")
        except Exception as e:
            st.write("Errore nella lettura del file:", e)
    else:
        st.write("Carica un file da elaborare.")
