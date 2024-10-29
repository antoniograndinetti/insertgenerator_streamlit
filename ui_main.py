import streamlit as st
from datetime import date
import windtre_generate_insert as wgi

st.set_page_config(layout="wide")

# Titolo della pagina
st.title("Winday sms plan insert generator")

# Nome del file di output
output_file = 'output.sql'

upper_col1, upper_col2 = st.columns(2)

# Selettori di date
# Disposizione dei selettori di date su una riga
col1, col2 = upper_col1.columns(2)
with col1:
    start_date = st.date_input("Data di inizio", value=date.today())
with col2:
    end_date = st.date_input("Data di fine", value=date.today())

# Controlla se i risultati sono già presenti nello stato della sessione
if "results_displayed" not in st.session_state:
    st.session_state["results_displayed"] = False

# Carica il file
uploaded_file = upper_col1.file_uploader("Carica il file del piano", type=["xlsx", "xls"])

but_col1, but_col2, _ = upper_col1.columns([1,1,7])
with but_col1:
    if st.button("Run", key="generate", type="primary"):
        if uploaded_file is not None:
            try:
                wgi.generate_insert(uploaded_file, output_file, start_date, end_date, st)
                
            except Exception as e:
                st.write("Errore nella lettura del file:", e)
        else:
            st.write("Carica un file da elaborare.")

with but_col2:
    if st.button("Clear all", key="clear"):
        st.session_state.clear()
        st.session_state["results_displayed"] = False

res_col1, res_col2 = st.columns(2)

with res_col1:
    if st.session_state["results_displayed"]:
        st.markdown(st.session_state["log_content"], unsafe_allow_html=True)

with upper_col2:
    if st.session_state["results_displayed"]:
        
        # Mostra le statistiche con colori e formattazione
        st.markdown(f"""
    <div style="border: 1px solid #ddd; padding: 16px; border-radius: 8px;">
        <h3 style="color: #4CAF50;">STATISTICS:</h3>
        <table style="width: 100%; border-collapse: collapse;">
            <tr>
                <td style="color: #000; padding: 8px; border-bottom: 1px solid #ddd;">Date selezionate:</td>
                <td style="color: #000; padding: 8px; border-bottom: 1px solid #ddd;">inizio {start_date} - fine {end_date}</td>
            </tr>
            <tr>
                <td style="color: #000; padding: 8px; border-bottom: 1px solid #ddd;">Le insert sono state salvate nel file:</td>
                <td style="color: #000; padding: 8px; border-bottom: 1px solid #ddd;">{output_file}</td>
            </tr>
            <tr>
                <td style="color: #000; padding: 8px; border-bottom: 1px solid #ddd;">Giorni generati:</td>
                <td style="color: #000; padding: 8px; border-bottom: 1px solid #ddd;">{st.session_state["counter_days"]}</td>
            </tr>
            <tr>
                <td style="color: #000; padding: 8px; border-bottom: 1px solid #ddd;">Insert nella tabella campaign:</td>
                <td style="color: #000; padding: 8px; border-bottom: 1px solid #ddd;">{st.session_state["counter_insert_campaign"]}</td>
            </tr>
            <tr>
                <td style="color: #000; padding: 8px; border-bottom: 1px solid #ddd;">Insert nella tabella di ampliamento:</td>
                <td style="color: #000; padding: 8px; border-bottom: 1px solid #ddd;">{st.session_state["counter_insert_ampliamento"]}</td>
            </tr>
            <tr>
                <td style="color: #000; padding: 8px; border-bottom: 1px solid #ddd;">Insert nella sms_config:</td>
                <td style="color: #000; padding: 8px; border-bottom: 1px solid #ddd;">{st.session_state["counter_insert_subcluster"]}</td>
            </tr>
            <tr>
                <td style="color: #FF0000; padding: 8px; border-bottom: 1px solid #ddd;">Warning:</td>
                <td style="color: #FF0000; padding: 8px; border-bottom: 1px solid #ddd;">{st.session_state["counter_warning"]}</td>
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)
    

if st.session_state["results_displayed"]:
    with open(output_file, "rb") as file:
        st.download_button(
            label="Scarica il file SQL",
            data=file,
            file_name=output_file,
            mime="application/sql"
        )