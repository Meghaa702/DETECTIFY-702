import streamlit as st
import cv2
import face_recognition as frg
import yaml
from utils import recognize, build_dataset, get_blacklist, send_alert

st.set_page_config(layout="wide")
cfg = yaml.load(open('config.yaml', 'r'), Loader=yaml.FullLoader)
PICTURE_PROMPT = cfg['INFO']['PICTURE_PROMPT']
WEBCAM_PROMPT = cfg['INFO']['WEBCAM_PROMPT']

st.sidebar.title("Settings")

menu = ["Picture", "Webcam"]
choice = st.sidebar.selectbox("Input type", menu)
TOLERANCE = st.sidebar.slider("Tolerance", 0.0, 1.0, 0.5, 0.01)
st.sidebar.info("Tolerance is the threshold for face recognition. The lower the tolerance, the stricter the face recognition. The higher the tolerance, the looser the face recognition.")

st.sidebar.title("Person Information")
name_container = st.sidebar.empty()
id_container = st.sidebar.empty()
name_container.info('Name: Unknown')
id_container.success('ID: Unknown')

blacklist = get_blacklist() 

if choice == "Picture":
    st.title("DETECTIFY")
    st.write(PICTURE_PROMPT)
    uploaded_images = st.file_uploader("Upload", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)
    if uploaded_images:
        for image in uploaded_images:
            image = frg.load_image_file(image)
            image, name, id = recognize(image, TOLERANCE)
            name_container.info(f"Name: {name}")
            id_container.success(f"ID: {id}")

            col1, col2 = st.columns(2)
            with col1:
                st.image(image)
            with col2:
                st.write(f"**Name:** {name}")
                st.write(f"**ID:** {id}")
    else:
        st.info("Please upload an image")

elif choice == "Webcam":
    st.title("DETECTIFY")
    st.write(WEBCAM_PROMPT)

    cam = cv2.VideoCapture(0)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    FRAME_WINDOW = st.image([])

    while True:
        ret, frame = cam.read()
        if not ret:
            st.error("Failed to capture frame from camera")
            st.info("Please turn off the other app that is using the camera and restart the app")
            st.stop()

        image, name, id = recognize(frame, TOLERANCE)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

       
        if name in blacklist:
            send_alert(f"Intruder Alert: {name} with ID {id} detected!")
            st.warning(f"Intruder Alert: {name} with ID {id} detected!")

        name_container.info(f"Name: {name}")
        id_container.success(f"ID: {id}")

        col1, col2 = st.columns(2)
        with col1:
            FRAME_WINDOW.image(image)
        with col2:
            st.write(f"**Name:** {name}")
            st.write(f"**ID:** {id}")

with st.sidebar.form(key='my_form'):
    st.title("Developer Section")
    submit_button = st.form_submit_button(label='REBUILD DATASET')
    if submit_button:
        with st.spinner("Rebuilding dataset..."):
            build_dataset()
        st.success("Dataset has been reset")