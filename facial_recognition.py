import face_recognition
import imutils
import pickle
import time
import cv2
import numpy as np
from picamera2 import Picamera2
from imutils.video import FPS
import firebase_admin
from firebase_admin import firestore

# Inițializează Firebase Firestore dacă nu este deja inițializat
if not firebase_admin._apps:
    firebase_admin.initialize_app()

db = firestore.client()

class FaceLogin:
    def __init__(self):  # 🔴 Corectăm inițializarea
        self.camera = Picamera2()
        self.load_encodings()  # 🔴 Încărcăm encodings la inițializare
        self.currentname = "unknown"

    def load_encodings(self):
        """Încărcăm encodings din fișierul pickle"""
        try:
            with open("encodings.pickle", "rb") as f:
                self.data = pickle.load(f)
            print("[INFO] Encodings loaded successfully.")
        except FileNotFoundError:
            print("[ERROR] Encodings file not found! Creating an empty dataset.")
            self.data = {"encodings": [], "names": []}

    def authenticate(self):
        """Starts facial recognition to authenticate a user."""
        print("[INFO] Starting face authentication...")

        self.camera.configure(self.camera.create_still_configuration(main={"size": (640, 480)}))
        self.camera.start()
        time.sleep(2.0)

        fps = FPS().start()
        recognized_user = None

        try:
            while True:
                frame = self.camera.capture_array()
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                rgb_frame = imutils.resize(rgb_frame, width=500)
                
                boxes = face_recognition.face_locations(rgb_frame)
                encodings = face_recognition.face_encodings(rgb_frame, boxes)
                names = []

                for encoding in encodings:
                    matches = face_recognition.compare_faces(self.data["encodings"], encoding, tolerance=0.55)
                    name = "Unknown"

                    if True in matches:
                        matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                        counts = {}

                        for i in matchedIdxs:
                            name = self.data["names"][i]
                            counts[name] = counts.get(name, 0) + 1

                        name = max(counts, key=counts.get)
                        if self.currentname != name:
                            self.currentname = name
                            recognized_user = name
                            print(f"Recognized user: {name}")
                            
                            user_ref = db.collection("users").where("name", "==", name).limit(1).stream()
                            user_data = None
                            for doc in user_ref:
                                user_data = doc.to_dict()

                            if user_data:
                                email = user_data.get("email")
                                if email:
                                    print(f"[INFO] Autentificare Firebase pentru: {email}")
                                    try:
                                        firebase_auth_user = auth.get_user_by_email(email)
                                        print(f"[SUCCESS] Utilizator logat în Firebase: {firebase_auth_user.uid}")
                                    except:
                                        print(f"[WARNING] Utilizatorul {email} nu a fost găsit în Firebase Authentication!")

                    names.append(name)

                for ((top, right, bottom, left), name) in zip(boxes, names):
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 225), 2)
                    y = top - 15 if top - 15 > 15 else top + 15
                    cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

                cv2.imshow("Facial Recognition is Running", frame)
                key = cv2.waitKey(1) & 0xFF

                if recognized_user or key == ord("q"):
                    break

                fps.update()

        except Exception as e:
            print(f"⚠ Eroare în timpul autentificării: {e}")

        finally:
            fps.stop()
            print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
            print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
            cv2.destroyAllWindows()
            self.close_camera()

        return recognized_user

    def close_camera(self):
        """Închide camera dacă este activă pentru a evita conflictele"""
        if hasattr(self, "camera") and self.camera:
            try:
                print("🔴 Închidere cameră Face Login...")
                self.camera.close()
                del self.camera
                time.sleep(2)
                print("✅ Camera Face Login închisă!")
            except Exception as e:
                print(f"⚠ Eroare la închiderea camerei Face Login: {e}")