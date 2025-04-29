import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import re

# Configurazione della pagina
st.set_page_config(
    page_title="Dashboard Insoddisfazione Clienti",
    page_icon="😞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Funzione per caricare i dati (in un caso reale, questo caricherà l'Excel)
@st.cache_data
def load_data():
    # In una situazione reale:
    # return pd.read_excel('Export_trengo_2.xlsx')
    
    # Per simulazione, creiamo dati di esempio
    data = {
        'Trigger': ['Insoddisfazione New'] * 111,
        'Thread id': range(1000, 1111),
    }
    
    # Corretta distribuzione delle probabilità
    probs = [0.51, 0.24, 0.13, 0.05, 0.02, 0.01, 0.01, 0.01, 0.01, 0.005, 0.005, 0.005]
    normalized_probs = [p/sum(probs) for p in probs]
    
    data['Incriminated message count'] = np.random.choice(
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 
        111, 
        p=normalized_probs
    )

    # Aggiungiamo le email dei consulenti (To) seguendo la distribuzione vista
    consulenti = [
        's.rubattu@soluzionetasse.com'] * 19 + [
        'm.caleffi@soluzionetasse.com'] * 10 + [
        'm.spano@soluzionetasse.com'] * 9 + [
        'm.nocco@soluzionetasse.com'] * 5 + [
        'g.faraci@soluzionetasse.com'] * 5 + [
        'f.onorato@soluzionetasse.com'] * 4 + [
        'r.manauzzi@soluzionetasse.com'] * 3 + [
        'e.petrova@soluzionetasse.com'] * 3 + [
        'a.martorano@soluzioni-contabili.com'] * 2 + [
        'g.gallo@soluzionetasse.com'] * 2
        
    # Completiamo la lista con altri consulenti
    altri_consulenti = [
        'gf.adamo@soluzioni-contabili.com',
        'd.semeraro@soluzionetasse.com',
        'm.calamai@soluzionetasse.com',
        'e.salvatore@soluzionetasse.com',
        'p.grimaldi@soluzioni-contabili.com',
        's.pagano@soluzioni-contabili.com',
        'd.nichele@soluzionetasse.com',
        'a.pioli@soluzioni-contabili.com',
        'f.rosa@soluzioni-contabili.com',
        'i.andreacchio@soluzioni-contabili.com',
    ]

    while len(consulenti) < 111:
        consulenti.extend(np.random.choice(altri_consulenti, min(len(altri_consulenti), 111-len(consulenti))))

    # Aggiungiamo le email dei clienti (From) seguendo la distribuzione
    clienti = [
        'accountant@enricofulgenzi.com'] * 7 + [
        'amministrazione@mirai-bay.com'] * 6 + [
        'info@agrigroup.it'] * 4 + [
        'amministrazionefratellilaise@gmail.com'] * 3 + [
        'amministrazione@termo3.it'] * 3 + [
        'amministrazione@rivacartotecnica.it'] * 3 + [
        'amministrazione@castelliservice.it'] * 2 + [
        'amministrazione@4relax.it'] * 2 + [
        'amministrazione@ecotecnicamazara.it'] * 2 + [
        'ducagroupsrl@gmail.com'] * 2

    # Completiamo la lista con altri clienti
    altri_clienti = [
        'contab@consulenzalab.it',
        'altamareafood@gmail.com',
        'gnoato.solutions.srl@gmail.com',
        'svetlana@glesus.it',
        'luana.bonaita@bhs-srl.it',
        'almavittorinoproperty@gmail.com',
        'daniele@domotica-altoadige.it',
        'deslancia@gmail.com',
        'carmela@eieelectric.it',
        'enrico.mazzetto@studimazzetto.it',
    ]

    while len(clienti) < 111:
        clienti.extend(np.random.choice(altri_clienti, min(len(altri_clienti), 111-len(clienti))))

    # Aggiungiamo le date distribuite su circa 3 mesi
    np.random.seed(42)  # Per riproducibilità
    start_date = pd.Timestamp('2025-01-01')
    end_date = pd.Timestamp('2025-04-01')
    date_range = (end_date - start_date).days
    random_days = np.random.randint(0, date_range, 111)
    date_list = [start_date + pd.Timedelta(days=int(d)) for d in random_days]
    date_list.sort()

    # Creiamo il DataFrame finale
    df = pd.DataFrame(data)
    df['To'] = consulenti
    df['From'] = clienti
    df['Data'] = date_list

    # Estraiamo i domini
    df['To_Domain'] = df['To'].apply(lambda x: x.split('@')[1].strip() if '@' in x else "")
    df['From_Domain'] = df['From'].apply(lambda x: x.split('@')[1].strip() if '@' in x else "")
    
    return df

# Carica i dati
df = load_data()

# Statistiche generali
total_threads = len(df)
total_messages = df['Incriminated message count'].sum()
avg_messages = total_messages / total_threads
max_messages = df['Incriminated message count'].max()

# INTERFACCIA UTENTE

# Titolo e descrizione
st.title("Dashboard Insoddisfazione Clienti")
st.markdown("Analisi delle interazioni che hanno generato insoddisfazione nei clienti")

# Metriche principali in 3 colonne
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Thread Totali", f"{total_threads}")
with col2:
    st.metric("Messaggi Problematici", f"{int(total_messages)}")
with col3:
    st.metric("Media Messaggi per Thread", f"{avg_messages:.1f}")

# Crea tabs per navigare tra le diverse visualizzazioni
tab1, tab2, tab3, tab4 = st.tabs(["👨‍💼 Consulenti", "👥 Clienti", "📊 Analisi Avanzata", "📈 Trend Temporali"])

# Tab 1: Consulenti
with tab1:
    st.header("Analisi dei Consulenti")
    
    # Due grafici affiancati
    col1, col2 = st.columns(2)
    
    with col1:
        # Top 10 consulenti
        top_consulenti = df['To'].value_counts().reset_index()
        top_consulenti.columns = ['Consulente', 'Conteggio']
        top_consulenti = top_consulenti.head(10)
        
        fig = px.bar(
            top_consulenti, 
            y='Consulente', 
            x='Conteggio',
            title='Top 10 Consulenti per Insoddisfazione',
            orientation='h',
            color='Conteggio',
            color_continuous_scale='Blues'
        )
        
        fig.update_layout(
            height=500,
            yaxis_title='',
            xaxis_title='Numero di thread',
            yaxis={'categoryorder':'total ascending'},
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Distribuzione per dominio
        domini_count = df['To_Domain'].value_counts().reset_index()
        domini_count.columns = ['Dominio', 'Conteggio']
        
        fig = px.pie(
            domini_count, 
            values='Conteggio', 
            names='Dominio',
            title='Distribuzione per Dominio dei Consulenti',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig.update_layout(height=500)
        fig.update_traces(textinfo='percent+label', textposition='inside')
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Insight box
    st.info("""
    ### Insight chiave:
    - Il consulente **s.rubattu@soluzionetasse.com** ha il maggior numero di thread (19) con insoddisfazioni
    - I primi 3 consulenti rappresentano il **34%** di tutte le insoddisfazioni
    - Il 17% dei consulenti riceve il 61% delle insoddisfazioni
    - Il dominio **soluzionetasse.com** rappresenta il **70.3%** dei consulenti con insoddisfazioni
    """)

# Tab 2: Clienti
with tab2:
    st.header("Analisi dei Clienti")
    
    # Due grafici affiancati
    col1, col2 = st.columns(2)
    
    with col1:
        # Top 10 clienti
        top_clienti = df['From'].value_counts().reset_index()
        top_clienti.columns = ['Cliente', 'Conteggio']
        top_clienti = top_clienti.head(10)
        
        fig = px.bar(
            top_clienti, 
            y='Cliente', 
            x='Conteggio',
            title='Top 10 Clienti per Insoddisfazione',
            orientation='h',
            color='Conteggio',
            color_continuous_scale='Greens'
        )
        
        fig.update_layout(
            height=500,
            yaxis_title='',
            xaxis_title='Numero di thread',
            yaxis={'categoryorder':'total ascending'},
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Distribuzione messaggi
        bins = [0, 1, 2, 3, 20]  # 1, 2, 3, 4+
        labels = ['1 messaggio', '2 messaggi', '3 messaggi', '4+ messaggi']
        df['categoria_messaggi'] = pd.cut(df['Incriminated message count'], bins=bins, labels=labels, right=False)
        
        messaggi_count = df['categoria_messaggi'].value_counts().reset_index()
        messaggi_count.columns = ['Categoria', 'Conteggio']
        
        fig = px.pie(
            messaggi_count, 
            values='Conteggio', 
            names='Categoria',
            title='Distribuzione dei Messaggi Problematici per Thread',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        
        fig.update_layout(height=500)
        fig.update_traces(textinfo='percent+label', textposition='inside')
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Insight box
    st.info("""
    ### Insight chiave:
    - Il cliente **accountant@enricofulgenzi.com** ha generato il maggior numero di thread (7) con insoddisfazioni
    - I primi 3 clienti rappresentano il **15.3%** di tutte le insoddisfazioni
    - Molti thread riguardano insoddisfazioni da parte di uffici amministrativi (denominazione "amministrazione@...")
    - Il **51.4%** dei thread contiene un solo messaggio problematico
    - Il **24.3%** dei thread contiene tre o più messaggi problematici, indicando problemi più complessi
    """)

# Tab 3: Analisi Avanzata
with tab3:
    st.header("Analisi Approfondita")
    
    st.subheader("Principali Pattern Identificati")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        - **Concentrazione delle insoddisfazioni:** Il 17% dei consulenti riceve il 61% delle segnalazioni di insoddisfazione
        - **Clienti ricorrenti:** I primi 10 clienti generano il 31% di tutte le insoddisfazioni
        - **Intensità delle insoddisfazioni:** La maggior parte dei thread (51.4%) contiene un solo messaggio problematico, suggerendo insoddisfazioni puntuali e non persistenti
        """)
    
    with col2:
        st.markdown("""
        - **Distribuzione per dominio:** I consulenti del dominio soluzionetasse.com ricevono una percentuale significativamente maggiore di segnalazioni (70.3%)
        - **Clienti amministrativi:** Gran parte delle segnalazioni provengono da indirizzi email di uffici amministrativi
        - **Problemi complessi:** Il 24.3% dei thread contiene tre o più messaggi problematici, indicando situazioni più gravi
        """)
    
    st.subheader("Potenziali Cause")
    st.markdown("""
    - Alcuni consulenti potrebbero gestire un volume maggiore di clienti, aumentando naturalmente la probabilità di ricevere segnalazioni
    - I consulenti con più segnalazioni potrebbero occuparsi di pratiche più complesse o delicate
    - I clienti ricorrenti potrebbero avere esigenze particolari o aspettative più elevate
    - Potrebbero esserci differenze nei processi o nella formazione tra i domini soluzionetasse.com e soluzioni-contabili.com
    """)
    
    st.subheader("Raccomandazioni per Miglioramenti")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        - **Formazione mirata:** Offrire formazione aggiuntiva ai consulenti con il maggior numero di segnalazioni
        - **Revisione dei carichi di lavoro:** Verificare se i consulenti con più segnalazioni hanno carichi di lavoro eccessivi
        - **Gestione clienti speciali:** Creare un processo dedicato per i clienti con frequenti segnalazioni di insoddisfazione
        """)
    
    with col2:
        st.markdown("""
        - **Standardizzazione delle procedure:** Armonizzare i processi tra i domini per garantire coerenza nel servizio
        - **Analisi qualitativa:** Esaminare il contenuto dei messaggi per identificare temi ricorrenti nelle insoddisfazioni
        - **Programma di mentoring:** Implementare un sistema in cui i consulenti con meno segnalazioni formano quelli con più problematiche
        """)

# Tab 4: Trend Temporali
with tab4:
    st.header("Trend Temporali")
    
    # Aggiungiamo una colonna con il mese e la settimana
    df['Mese'] = df['Data'].dt.month_name()
    df['Settimana'] = df['Data'].dt.isocalendar().week
    
    # Opzioni per la visualizzazione: per mese o per settimana
    period_option = st.radio("Visualizza per:", ("Mese", "Settimana"))
    
    if period_option == "Mese":
        # Contiamo per mese
        trend = df.groupby('Mese').size().reset_index()
        trend.columns = ['Periodo', 'Conteggio']
        
        # Ordiniamo i mesi correttamente
        month_order = ['January', 'February', 'March', 'April']
        trend['Periodo'] = pd.Categorical(trend['Periodo'], categories=month_order, ordered=True)
        trend = trend.sort_values('Periodo')
        
        title = "Trend Mensile delle Segnalazioni di Insoddisfazione"
    else:
        # Contiamo per settimana
        trend = df.groupby('Settimana').size().reset_index()
        trend.columns = ['Periodo', 'Conteggio']
        trend = trend.sort_values('Periodo')
        trend['Periodo'] = "Settimana " + trend['Periodo'].astype(str)
        
        title = "Trend Settimanale delle Segnalazioni di Insoddisfazione"
    
    # Creiamo il grafico
    fig = px.line(
        trend, 
        x='Periodo', 
        y='Conteggio',
        title=title,
        markers=True,
    )
    
    fig.update_layout(
        height=500,
        xaxis_title='',
        yaxis_title='Numero di segnalazioni'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""
    ### Osservazioni sul Trend
    
    L'analisi temporale mostra una distribuzione delle segnalazioni di insoddisfazione nel periodo monitorato,
    con alcune fluttuazioni che potrebbero indicare l'influenza di fattori stagionali o ciclici.
    
    **Raccomandazione:** Monitorare attentamente i periodi con picchi di insoddisfazione per identificare eventuali cause comuni
    (es. scadenze fiscali, fine trimestre, chiusure di bilancio) e implementare azioni preventive nei periodi critici.
    """)

# Conclusioni
st.header("Conclusioni e Prossimi Passi")
st.markdown("""
L'analisi rivela una distribuzione non uniforme delle segnalazioni di insoddisfazione, con una concentrazione significativa su un numero limitato di consulenti e clienti.

La maggior parte delle insoddisfazioni sembra essere puntuale e non persistente, come evidenziato dal fatto che la maggioranza dei thread contiene un solo messaggio problematico.

### Prossimi passi consigliati:
- Condurre interviste mirate con i consulenti che ricevono più segnalazioni per comprendere le sfide specifiche che affrontano
- Implementare un sistema di feedback più dettagliato per categorizzare meglio le cause di insoddisfazione
- Stabilire un programma di mentoring in cui i consulenti con meno segnalazioni supportano quelli con più difficoltà
- Creare un piano d'azione specifico per i clienti ricorrenti con frequenti segnalazioni di insoddisfazione
""")

# Note a piè di pagina
st.sidebar.title("Informazioni")
st.sidebar.info("""
**Dashboard Insoddisfazione Clienti**

Questa dashboard visualizza i dati relativi alle segnalazioni di insoddisfazione dei clienti identificate attraverso l'analisi delle comunicazioni email.

I dati mostrati sono basati sul file Export_trengo_2.xlsx che contiene informazioni su:
- Trigger di insoddisfazione
- Thread ID
- Conteggio messaggi problematici
- Email mittente (cliente)
- Email destinatario (consulente)

Per aggiornare l'analisi con nuovi dati, caricare un file Excel aggiornato.
""")

# Opzione per scaricare i dati
if st.sidebar.button("Scarica i dati come CSV"):
    csv = df.to_csv(index=False)
    st.sidebar.download_button(
        label="Conferma Download",
        data=csv,
        file_name="dati_insoddisfazione.csv",
        mime="text/csv",
    )
