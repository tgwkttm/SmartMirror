import firebase_admin
from firebase_admin import credentials, auth, firestore, storage
from datetime import datetime
import hashlib
import os
import pickle
import face_recognition
import cv2

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_config.json")
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'smartmirror-c6c98.appspot.com'
    })

db = firestore.client()
bucket = storage.bucket()

def create_and_store_user(name, email, password):
    try:
        user = auth.create_user(email=email, password=password)
        print(f'[INFO] Successfully created new user: {user.uid}')
        
        users_ref = db.collection("users")
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        user_data = {
            "name": name,
            "email": email,
            "password": hashed_password,
            "face_model": None,
            "registration_time": datetime.now()
        }
        users_ref.document(user.uid).set(user_data)
        print("[INFO] User data added to Firestore successfully!")
        
        return user.uid
    except Exception as e:
        print(f"[ERROR] Failed to create user: {str(e)}")
        return None

def upload_image_to_storage(image_path, storage_path):
    try:
        blob = bucket.blob(storage_path)
        blob.upload_from_filename(image_path)
        public_url = blob.public_url
        print(f'[INFO] Image {storage_path} uploaded to Firebase Storage.')
        return public_url
    except Exception as e:
        print(f"[ERROR] Failed to upload image: {str(e)}")
        return None

def upload_user_images(user_id, local_image_folder):
    try:
        storage_folder = f"images/{user_id}/"
        image_urls = []
        for img_file in os.listdir(local_image_folder):
            local_image_path = os.path.join(local_image_folder, img_file)
            if os.path.isfile(local_image_path):
                storage_path = f"{storage_folder}{img_file}"
                image_url = upload_image_to_storage(local_image_path, storage_path)
                if image_url:
                    image_urls.append(image_url)
        print(f"[INFO] All images for user {user_id} uploaded successfully.")
        return image_urls
    except Exception as e:
        print(f"[ERROR] Failed to upload user images: {str(e)}")
        return []

def link_images_to_user(user_id, image_urls):
    try:
        user_ref = db.collection("users").document(user_id)
        user_ref.update({"face_images": image_urls})
        print(f"[INFO] Images linked to user {user_id} in Firestore.")
        update_encodings()  # 🔴 Actualizăm encodările după adăugarea unui nou utilizator
    except Exception as e:
        print(f"[ERROR] Failed to link images to user in Firestore: {str(e)}")

def update_encodings(dataset_path="dataset", encodings_file="encodings.pickle"):
    """Actualizează fișierul encodings.pickle după fiecare înregistrare de utilizator."""
    print("[INFO] Updating face encodings...")
    knownEncodings = []
    knownNames = []

    if not os.path.exists(dataset_path):
        print("[WARNING] Dataset folder not found!")
        return

    for user in os.listdir(dataset_path):
        user_path = os.path.join(dataset_path, user)
        if os.path.isdir(user_path):
            print(f"[DEBUG] Procesăm utilizatorul: {user}")  # 🔴 Verifică dacă utilizatorul apare
            for image_file in os.listdir(user_path):
                image_path = os.path.join(user_path, image_file)
                print(f"[DEBUG] Procesăm imaginea: {image_file}")  # 🔴 Verifică fiecare imagine
                image = cv2.imread(image_path)
                if image is None:
                    print(f"[ERROR] Imaginea {image_file} nu a fost încărcată corect!")
                    continue

                rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                boxes = face_recognition.face_locations(rgb, model="hog")
                encodings = face_recognition.face_encodings(rgb, boxes)

                if encodings:
                    knownEncodings.append(encodings[0])
                    knownNames.append(user)
                    print(f"[INFO] Adăugat encoding pentru {user}")
                else:
                    print(f"[WARNING] Nu s-a găsit față în {image_file}")

    if not knownEncodings:
        print("[ERROR] Nu au fost găsite encodări! Verifică imaginile.")
        return

    with open(encodings_file, "wb") as f:
        data = {"encodings": knownEncodings, "names": knownNames}
        pickle.dump(data, f)
    print("[INFO] Encodings updated successfully.")
    print(f"[DEBUG] Utilizatori salvați în encodings.pickle: {set(knownNames)}")