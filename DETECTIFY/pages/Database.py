import streamlit as st
import pickle
import yaml
import pandas as pd
import base64

cfg = yaml.load(open("config.yaml", "r"), Loader=yaml.FullLoader)
PKL_PATH = cfg['PATH']["PKL_PATH"]

st.set_page_config(layout="wide")

with open(PKL_PATH, 'rb') as file:
    database = pickle.load(file)

Index, Id, Name, Image  = st.columns([0.5, 0.5, 3, 3])
for idx, person in database.items():
    with Index:
        st.write(idx)
    with Id: 
        st.write(person['id'])
    with Name:     
        st.write(person['name'])
    with Image:     
        st.image(person['image'], width=200)

def create_csv(database):
    data = []
    for idx, person in database.items():
        data.append({'Index': idx, 'ID': person['id'], 'Name': person['name']})
    df = pd.DataFrame(data)
    return df.to_csv(index=False)

csv = create_csv(database)

def download_link(object_to_download, download_filename, download_link_text):
    """
    Generates a link to download the given object_to_download.
    """
    if isinstance(object_to_download, pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False)

    b64 = base64.b64encode(object_to_download.encode()).decode()

    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'

st.markdown(download_link(csv, 'database.csv', 'Download Database as CSV'), unsafe_allow_html=True)
