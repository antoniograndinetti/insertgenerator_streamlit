from datetime import datetime
import pandas as pd
import unicodedata
import re

# Nome del file di output
output_file = 'output.sql'

# Funzione per convertire il giorno in formato abbreviato
def abbreviazione_giorno(giorno):
    mapping = {
        'Lunedi': 'lun',
        'Martedi': 'mar',
        'Mercoledi': 'mer',
        'Giovedi': 'gio',
        'Venerdi': 'ven',
        'Sabato': 'sab',
        'Domenica': 'dom'
    }
    return mapping.get(giorno, giorno[:3].lower())

def insert_sms_config(id_cluster_priority, sms_text, data_str):
    return f"""
INSERT INTO wind_cra_app.sms_config
(id, id_cluster_priority, sms_text, start_validity, end_validity, creation_dt, last_update_dt)
VALUES
(nextval('wind_cra_app.sms_config_id_seq'),
{id_cluster_priority},
'{sms_text}',
'{data_str} 00:00:00.000',
'{data_str} 23:59:59.999',
now(),
NULL);
            """

def normalize_and_remove_non_ascii(text):
    # Normalizza la stringa in forma NFD (decomposizione canonica)
    normalized_text = unicodedata.normalize('NFD', text)
    # Rimuove i caratteri non ASCII usando una regex
    ascii_text = re.sub(r'[^\x00-\x7F]', '', normalized_text)
    return ascii_text

def is_string_different(original, transformed):
    removed_chars = []
    for i, char in enumerate(original):
        if i >= len(transformed) or char != transformed[i]:
            removed_chars.append(char)
    return len(removed_chars) != 0

def generate_insert(file_path, data_inizio, data_fine, st):

    col1, col2 = st.columns(2)

    with col1:
        log_content ="""
            <div style="border: 1px solid #ddd; padding: 16px; border-radius: 8px;">
                <h3 style="color: #4CAF50;">LOG:</h3>"""

        # Log di informazioni nella colonna sinistra
        log_content += "<div style='color: #000; font-weight: bold;'>INFO: Inizio lettura file...</div>"

        # CONFIGURAZIONI
        # file_path = 'Piano_WINDAY_All5.xlsx' # Specifica il nome del excel qui
        sheet_name = 'Testi SMS'  # Specifica il nome del foglio qui
        df = pd.read_excel(file_path, sheet_name=sheet_name)

        counter_days = 0
        counter_insert_campaign = 0
        counter_insert_ampliamento = 0
        counter_insert_subcluster = 0
        counter_warning = 0

        with open(output_file, mode='w') as output:
            # reader = csv.DictReader(file, delimiter=';')
            for index, row in df.iterrows():
                data_dt = row['Data']
                if data_dt != None and pd.isnull(data_dt) == False:
                    data_str = data_dt.strftime('%Y-%m-%d')

                    # Filtra le righe in base alle date
                    if pd.to_datetime(data_inizio) <= data_dt and data_dt <= pd.to_datetime(data_fine):
                        counter_days = counter_days + 1

                        output.write(f"""
------------------ INIZIO data {data_str} --------------------""")
                        giorno = row['Giorno']
                        log_content += f"<div style='color: #000;'>INFO: Generando per giorno {giorno}, data {data_str}.</div>"

                        note = row['Note']
                        ampliamento = 'S' if note == 'DA PREVEDERE AMPLIAMENTO SU CLUSTER OLD E SUPEROLD' else 'N'
                        giorno_abbr = abbreviazione_giorno(giorno)

                        # Inserimento per la tabella campaign
                        campaign_insert = f"""
INSERT INTO public.campaign
(code, campaign_channel, campaign_type, enddt, fl_imported, name, startdt, day, creation_date, contact_dt, file_name, fl_exported_selligent, fl_has_lead, stack_brand)
VALUES('MarketingAutomation{data_dt.strftime('%Y%m%d')}',
'SMS',
'MacroCluster',
'{data_str} 23:59:59.999',
'N',
'MarketingAutomation{data_dt.strftime('%Y%m%d')}name',
'{data_str} 00:00:00.000',
'{giorno_abbr}',
now(),
'{data_str} 00:00:00.000',
NULL,
'N',
'CLUSTER',
NULL);
        """
                        output.write(campaign_insert)
                        counter_insert_campaign = counter_insert_campaign + 1

                        sub_cluster_list = [14, 15, 16, 17, 18, 21]

                        # Inserimento su config_run_function se c'è ampliamento
                        if ampliamento == 'S':
                            config_run_function_insert = f"""
INSERT INTO wind_cra_app.config_run_function
(dt_start, dt_end, fl_active)
VALUES('{data_str} 00:00:00.000',
'{data_str} 00:00:00.000',
'S');
            """
                            log_content += f"<div style='color: #000;'>INFO: Identificato ampliamento a old e superold.</div>"
                            output.write(config_run_function_insert)
                            counter_insert_ampliamento = counter_insert_ampliamento + 1

                            sub_cluster_list = [14, 15, 16, 17, 18, 19, 20, 21]

                        # Inserimento su sms_config
                        sms_text_normalized = normalize_and_remove_non_ascii(row['Testo SMS  '])

                        if is_string_different(row['Testo SMS  '], sms_text_normalized):
                            output.write(f"""
------------------ WARN: CARATTERI ASCII TROVATI! VERIFICARE IL TESTO! --------------------\n""")
                            log_content += f"""
                                <div style='color: #FF9800; font-weight: bold;'>
                                    WARN: Caratteri non ASCII rilevati nel giorno {data_str}. Verificare il testo!
                                </div>
                            """
                            counter_warning += 1

                        sms_text = sms_text_normalized.replace("'", "''")
                        for id_cluster_priority in sub_cluster_list:
                            sms_config_insert = insert_sms_config(id_cluster_priority, sms_text, data_str)
                            counter_insert_subcluster += 1
                            output.write(sms_config_insert)

                        output.write(f"""
------------------ FINE data {data_str} --------------------\n""")

        log_content += "<div style='color: #000; font-weight: bold;'>INFO: Fine.</div>"
        
        # Chiudiamo il div del log box
        log_content += "</div>"

        st.markdown(log_content, unsafe_allow_html=True)

    # Mostra le statistiche con colori e formattazione
    with col2:
        st.markdown(f"""
        <div style="border: 1px solid #ddd; padding: 16px; border-radius: 8px;">
            <h3 style="color: #4CAF50;">STATISTICS:</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="color: #000; padding: 8px; border-bottom: 1px solid #ddd;">Date selezionate:</td>
                    <td style="color: #000; padding: 8px; border-bottom: 1px solid #ddd;">inizio {data_inizio} - fine {data_fine}</td>
                </tr>
                <tr>
                    <td style="color: #000; padding: 8px; border-bottom: 1px solid #ddd;">Le insert sono state salvate nel file:</td>
                    <td style="color: #000; padding: 8px; border-bottom: 1px solid #ddd;">{output_file}</td>
                </tr>
                <tr>
                    <td style="color: #000; padding: 8px; border-bottom: 1px solid #ddd;">Giorni generati:</td>
                    <td style="color: #000; padding: 8px; border-bottom: 1px solid #ddd;">{counter_days}</td>
                </tr>
                <tr>
                    <td style="color: #000; padding: 8px; border-bottom: 1px solid #ddd;">Insert nella tabella campaign:</td>
                    <td style="color: #000; padding: 8px; border-bottom: 1px solid #ddd;">{counter_insert_campaign}</td>
                </tr>
                <tr>
                    <td style="color: #000; padding: 8px; border-bottom: 1px solid #ddd;">Insert nella tabella di ampliamento:</td>
                    <td style="color: #000; padding: 8px; border-bottom: 1px solid #ddd;">{counter_insert_ampliamento}</td>
                </tr>
                <tr>
                    <td style="color: #000; padding: 8px; border-bottom: 1px solid #ddd;">Insert nella sms_config:</td>
                    <td style="color: #000; padding: 8px; border-bottom: 1px solid #ddd;">{counter_insert_subcluster}</td>
                </tr>
                <tr>
                    <td style="color: #FF0000; padding: 8px; border-bottom: 1px solid #ddd;">Warning:</td>
                    <td style="color: #FF0000; padding: 8px; border-bottom: 1px solid #ddd;">{counter_warning}</td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)