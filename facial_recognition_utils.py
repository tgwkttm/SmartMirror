import face_recognition
import pickle
import os

def add_images_to_encodings(user_directory, username):
    encodings_path = "encodings.pickle"

    # Încarcă encodings existente
    try:
        data = pickle.loads(open(encodings_path, "rb").read())
    except FileNotFoundError:
        data = {"encodings": [], "names": []}

    # Procesează fiecare imagine nouă
    for image_name in os.listdir(user_directory):
        image_path = os.path.join(user_directory, image_name)
        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image)

        for encoding in encodings:
            data["encodings"].append(encoding)
            data["names"].append(username)

    # Salvează encodings actualizate
    with open(encodings_path, "wb") as f:
        f.write(pickle.dumps(data))

    print(f"[INFO] Encodings actualizate pentru {username}.")
