import face_recognition as frg
import pickle as pkl
import os
import cv2
import numpy as np
import yaml
from collections import defaultdict

information = defaultdict(dict)
cfg = yaml.load(open('config.yaml', 'r'), Loader=yaml.FullLoader)
DATASET_DIR = cfg['PATH']['DATASET_DIR']
PKL_PATH = cfg['PATH']['PKL_PATH']
BLACKLIST_PATH = cfg['PATH'].get('BLACKLIST_PATH', 'blacklist.pkl')  
def get_databse():
    with open(PKL_PATH, 'rb') as f:
        database = pkl.load(f)
    return database

def get_blacklist():
    if os.path.exists(BLACKLIST_PATH):
        with open(BLACKLIST_PATH, 'rb') as f:
            blacklist = pkl.load(f)
    else:
        blacklist = []
    return blacklist

def recognize(image, TOLERANCE):
    database = get_databse()
    known_encodings = [database[id]['encoding'] for id in database.keys()]
    name = 'Unknown'
    id = 'Unknown'
    
    face_locations = frg.face_locations(image)
    face_encodings = frg.face_encodings(image, face_locations)
    
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = frg.compare_faces(known_encodings, face_encoding, tolerance=TOLERANCE)
        if True in matches:
            match_index = matches.index(True)
            name = database[list(database.keys())[match_index]]['name']
            id = database[list(database.keys())[match_index]]['id']
        cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(image, name, (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    return image, name, id

def isFaceExists(image):
    face_locations = frg.face_locations(image)
    return len(face_locations) > 0

def submitNew(name, id, image, old_idx=None):
    database = get_databse()
    
    if isinstance(image, bytes):
        image = cv2.imdecode(np.frombuffer(image, np.uint8), cv2.IMREAD_COLOR)

    if not isFaceExists(image):
        return -1
    
    encoding = frg.face_encodings(image)[0]
   
    existing_ids = [database[i]['id'] for i in database.keys()]
   
    if old_idx is not None: 
        new_idx = old_idx
    else: 
        if id in existing_ids:
            return 0
        new_idx = len(database)
    
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    database[new_idx] = {
        'image': image,
        'id': id, 
        'name': name,
        'encoding': encoding
    }
    with open(PKL_PATH, 'wb') as f:
        pkl.dump(database, f)
    return 1

def get_info_from_id(id):
    database = get_databse()
    for idx, person in database.items():
        if person['id'] == id:
            name = person['name']
            image = person['image']
            return name, image, idx       
    return None, None, None

def deleteOne(id):
    database = get_databse()
    id = str(id)
    for key, person in database.items():
        if person['id'] == id:
            del database[key]
            break
    with open(PKL_PATH, 'wb') as f:
        pkl.dump(database, f)
    return True

def build_dataset():
    counter = 0
    for image_file in os.listdir(DATASET_DIR):
        image_path = os.path.join(DATASET_DIR, image_file)
        image_name = image_file.split('.')[0]
        parsed_name = image_name.split('_')
        person_id = parsed_name[0]
        person_name = ' '.join(parsed_name[1:])
        if not image_path.endswith('.jpg'):
            continue
        image = frg.load_image_file(image_path)
        information[counter]['image'] = image
        information[counter]['id'] = person_id
        information[counter]['name'] = person_name
        information[counter]['encoding'] = frg.face_encodings(image)[0]
        counter += 1

    with open(PKL_PATH, 'wb') as f:
        pkl.dump(information, f)

def send_alert(message):
    print(message)

if __name__ == "__main__": 
    deleteOne(4)
