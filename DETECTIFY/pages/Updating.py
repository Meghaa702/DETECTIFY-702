import streamlit as st
import cv2
import yaml
import pickle
from utils import submitNew, get_info_from_id, deleteOne
import numpy as np
import pandas as pd
import os
import requests
from io import BytesIO
from PIL import Image

st.set_page_config(layout="wide")
st.title("DETECTIFY")
st.write("This app is used to add new faces to the dataset")

menu = ["Adding", "Deleting", "Adjusting"]
choice = st.sidebar.selectbox("Options", menu)

def fetch_image_from_url(url):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

if choice == "Adding":
    add_choice = st.radio("Choose an option", ("Manual Entry", "Upload CSV"))
    
    if add_choice == "Manual Entry":
        name = st.text_input("Name", placeholder='Enter name')
        id = st.text_input("ID", placeholder='Enter id')
        
        upload = st.radio("Upload image or use webcam", ("Upload", "Webcam"))
        
        if upload == "Upload":
            uploaded_image = st.file_uploader("Upload", type=['jpg', 'png', 'jpeg'])
            if uploaded_image is not None:
                st.image(uploaded_image)
                submit_btn = st.button("Submit", key="submit_btn")
                if submit_btn:
                    if name == "" or id == "":
                        st.error("Please enter name and ID")
                    else:
                        image = cv2.cvtColor(np.array(Image.open(uploaded_image)), cv2.COLOR_RGB2BGR)
                        ret = submitNew(name, id, image)
                        if ret == 1:
                            st.success("Person Data Added")
                        elif ret == 0:
                            st.error("Person ID already exists")
                        elif ret == -1:
                            st.error("There is no face in the picture")
        
        elif upload == "Webcam":
            img_file_buffer = st.camera_input("Take a picture")
            submit_btn = st.button("Submit", key="submit_btn")
            if img_file_buffer is not None:
                bytes_data = img_file_buffer.getvalue()
                cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
                if submit_btn:
                    if name == "" or id == "":
                        st.error("Please enter name and ID")
                    else:
                        ret = submitNew(name, id, cv2_img)
                        if ret == 1:
                            st.success("Person Data Added")
                        elif ret == 0:
                            st.error("Person ID already exists")
                        elif ret == -1:
                            st.error("There is no face in the picture")
    
    elif add_choice == "Upload CSV":
        uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])
        
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            if 'id' in df.columns and 'name' in df.columns and 'image_url' in df.columns:
                for idx, row in df.iterrows():
                    st.write(f"ID: {row['id']}, Name: {row['name']}")
                    
                    image_data = None
                    if pd.notna(row['image_url']) and row['image_url'].strip() != "":
                        try:
                            image_data = fetch_image_from_url(row['image_url'])
                            st.image(cv2.cvtColor(image_data, cv2.COLOR_BGR2RGB), caption=f"Image for ID {row['id']}, Name {row['name']}")
                        except Exception as e:
                            st.warning(f"Could not load image from URL for ID {row['id']}, Name {row['name']}: {e}")
                    
                    if image_data is None:
                        uploaded_image = st.file_uploader(f"Upload image for ID {row['id']}, Name {row['name']}", type=['jpg', 'png', 'jpeg'], key=f"{row['id']}_{row['name']}")
                        if uploaded_image is not None:
                            image_data = cv2.cvtColor(np.array(Image.open(uploaded_image)), cv2.COLOR_RGB2BGR)
                            st.image(cv2.cvtColor(image_data, cv2.COLOR_BGR2RGB), caption=f"Image for ID {row['id']}, Name {row['name']}")
                    
                    if image_data is not None:
                        ret = submitNew(row['name'], str(row['id']), image_data)
                        if ret == 1:
                            st.success(f"Person Data Added for ID {row['id']}, Name {row['name']}")
                        elif ret == 0:
                            st.error(f"Person ID {row['id']} already exists")
                        elif ret == -1:
                            st.error(f"There is no face in the picture for ID {row['id']}, Name {row['name']}")
            else:
                st.error("CSV file must contain 'id', 'name', and 'image_url' columns")

elif choice == "Deleting":
    def del_btn_callback(id):
        deleteOne(id)
        st.success("Person Data deleted")
        
    id = st.text_input("ID", placeholder='Enter id')
    submit_btn = st.button("Submit", key="submit_btn")
    if submit_btn:
        name, image, _ = get_info_from_id(str(id))
        if name is None and image is None:
            st.error("Person ID does not exist")
        else:
            st.success(f"Name of the Person with ID {id} is: {name}")
            st.warning("Please check the image below to make sure you are deleting the right data")
            st.image(image)
            del_btn = st.button("Delete", key="del_btn", on_click=del_btn_callback, args=(id,))
        
elif choice == "Adjusting":
    def form_callback(old_name, old_id, old_image, old_idx):
        new_name = st.session_state['new_name']
        new_id = st.session_state['new_id']
        new_image = st.session_state['new_image']
        
        name = old_name
        id = old_id
        image = old_image
        
        if new_image is not None:
            image = cv2.imdecode(np.frombuffer(new_image.read(), np.uint8), cv2.IMREAD_COLOR)
            
        if new_name != old_name:
            name = new_name
            
        if new_id != old_id:
            id = new_id
        
        ret = submitNew(name, id, image, old_idx=old_idx)
        if ret == 1:
            st.success("Person Data Added")
        elif ret == 0:
            st.error("Person ID already exists")
        elif ret == -1:
            st.error("There is no face in the picture")
    
    id = st.text_input("ID", placeholder='Enter id')
    submit_btn = st.button("Submit", key="submit_btn")
    if submit_btn:
        old_name, old_image, old_idx = get_info_from_id(str(id))
        if old_name is None and old_image is None:
            st.error("Person ID does not exist")
        else:
            with st.form(key='my_form'):
                st.title("Adjusting Person info")
                col1, col2 = st.columns(2)
                new_name = col1.text_input("Name", key='new_name', value=old_name, placeholder='Enter new name')
                new_id = col1.text_input("ID", key='new_id', value=id, placeholder='Enter new id')
                new_image = col1.file_uploader("Upload new image", key='new_image', type=['jpg', 'png', 'jpeg'])
                col2.image(old_image, caption='Current image', width=400)
                st.form_submit_button(label='Submit', on_click=form_callback, args=(old_name, id, old_image, old_idx))
