import requests
import streamlit as st
import pandas as pd
import plotly.express as px
import os

api_url = 'http://backend/'


# Nacteni dat
@st.cache_data()
def load_data(input_df: pd.DataFrame = None,):
    global data
    if input_df is None:
        data = pd.read_csv('scitani.csv')
    else:
        data = input_df
    return data

if 'data' not in st.session_state:
    # První spuštění aplikace, načtěte a nastavte data
    st.session_state.data = load_data()

# Upload csv souboru
uploaded_file = st.sidebar.file_uploader("Vyberte csv či Excel soubor:", type=['csv', 'xlsx'])   

if uploaded_file is not None:
    if uploaded_file.name.endswith('csv'):       
        save_data = pd.read_csv(uploaded_file)
        save_data.to_csv(uploaded_file.name, index=False)
    if uploaded_file.name.endswith('xlsx'):
        xl = pd.ExcelFile(uploaded_file)
        xl.to_excel(uploaded_file.name, index=False)    





# Request na API pro zobrazení dostupných souborů
response_file = requests.get(api_url + 'getFiles')
selected_file = st.sidebar.selectbox('Vyberte soubor:', response_file.json()['all_files']) 
if selected_file.endswith('.xls') or selected_file.endswith('.xlsx'):
    response_sheet = requests.get(api_url + f'getSheets/{selected_file}')
    selected_sheet = st.sidebar.selectbox('Vyberte sešit:', response_sheet.json()['sheets'])  
else:
    selected_sheet = None

response_cols = requests.get(api_url + f'getColumnInfo/{selected_file}/{selected_sheet}')
# st.header(response_cols.json())

# Vyber sloupcu 
selected_cols = st.sidebar.multiselect('Vyberte sloupce:', [(i, col) for i, col in enumerate(response_cols.json()['column_info']['all_columns'])])


build_url = api_url + f'getColumnData/{selected_file}/{selected_sheet}/' + '?columns=' + '&columns='.join([str(i) for i, popis in selected_cols])         
# st.header(build_url)    
load = st.sidebar.button('Načti data')

if load:
    response_data = requests.get(build_url)
    api_data = pd.read_json(response_data.json()['data'])
    st.session_state.data = load_data(api_data)
    st.header('Data')
    st.dataframe(data)
    st.header('Statistiky')
    st.dataframe(data.describe())

if st.session_state.data is not None:
    # Dropdown menu pro vyber grafu pro druhy graf
    chart_type = st.sidebar.selectbox('Vyberte typ grafu:', ['Treemap', 'Bar', 'Sunburst'])

    # vyberu hodnoty pro int a object
    categoty_columns = st.session_state.data.select_dtypes(include=['object'])
    int_columns = st.session_state.data.select_dtypes(include=['int64'])


    path = None
    hodnota = None
    # Vytvoreni grafu
    if chart_type == 'Treemap':
        path = st.sidebar.multiselect('Vyberte osu x grafu:', st.session_state.data.columns)
        hodnota = st.sidebar.selectbox('Vyberte hodnoty:', int_columns.columns)
        # show data from multiselect
        fig_2 = px.treemap(st.session_state.data, path=path, values=hodnota)

    elif chart_type == 'Bar':
        x = st.sidebar.selectbox('Vyberte osu x grafu:', st.session_state.data.columns)
        y = st.sidebar.selectbox('Vyberte osu y grafu:', int_columns.columns)
        fig_2 = px.bar(st.session_state.data, x=x, y=y)

    else:
        path = st.sidebar.multiselect('Vyberte osu x grafu:', st.session_state.data.columns)
        hodnota = st.sidebar.selectbox('Vyberte hodnoty:', int_columns.columns)
        fig_2 = px.sunburst(st.session_state.data, path=path, values=hodnota)

    fig_2.update_layout(autosize=True,height=600, width=1000)

    # Vykresleni grafu
    if path is None:
        path = x
        st.header(f'Graf pro :green[{x}] s hodnotou :blue[{hodnota}]')
    else:
        st.header(f'Graf pro :green[{", ".join(path)}] s hodnotou :blue[{hodnota}]')

    if hodnota is None:
        hodnota = y
    # st.header(f'Graf pro :green[{", ".join(path)}] s hodnotou :blue[{hodnota}]')
    st.plotly_chart(fig_2, use_container_width=True)

