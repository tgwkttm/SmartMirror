import tkinter as tk
from tkinter import Label, Button
import cv2
from PIL import Image, ImageTk
from tflite_runtime.interpreter import Interpreter
import numpy as np
from picamera2 import Picamera2
import threading
import time

class EmotionDetectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Emotion Detector")
        self.root.configure(bg="black")

        #face fereastra complet fullscreen și stabilă
        self.root.attributes("-fullscreen", True)
        self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}")

        # Eticheta pentru descriere
        self.label = Label(root, text="Press 'Detect Emotion' to start detecting...", font=("Helvetica", 14), fg="white", bg="black")
        self.label.pack(pady=20)

        #eticheta pentru afișarea rezultatului
        self.emotion_label = Label(root, text="", font=("Helvetica", 18), fg="white", bg="black")
        self.emotion_label.pack(pady=20)
        
        self.message_label = Label(root, text="", font=("Helvetica", 16), fg="yellow", bg="black")
        self.message_label.pack(pady=10)

        #butoane
        self.detect_button = Button(root, text="Detect Emotion", command=self.start_detection, font=("Helvetica", 14), bg="grey", fg="white")
        self.detect_button.pack(pady=20)

        self.stop_button = Button(root, text="Stop Detection", command=self.stop_detection, font=("Helvetica", 14), bg="red", fg="white")
        self.stop_button.pack(pady=20)
        self.stop_button.config(state=tk.DISABLED)

        #etichetă pentru video (ajustabilă la raportul camerei)
        self.video_label = Label(root, bg="black")
        self.video_label.pack(expand=True)

        #inițializare Cameră
        self.picam2 = None
        self.initialize_camera()

        #incărcarea clasificatorului de fețe
        self.face_classifier = cv2.CascadeClassifier('haarcascades_models/haarcascade_frontalface_default.xml')

        #configurarea modelului de detecție a emoțiilor
        self.emotion_interpreter = Interpreter(model_path="emotion_detection_model_100epochs_opt.tflite")
        self.emotion_interpreter.allocate_tensors()

        self.emotion_input_details = self.emotion_interpreter.get_input_details()
        self.emotion_output_details = self.emotion_interpreter.get_output_details()

        #etichetele pentru emoții
        self.class_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Neutral', 'Sad', 'Surprise']

        self.emotion_messages = {
            'Angry': "Take a deep breath! 😊",
            'Disgust': "Try to focus on something positive!",
            'Fear': "You're safe, don't worry! ❤️",
            'Happy': "Keep smiling! 😁",
            'Neutral': "Stay calm and relaxed!",
            'Sad': "Everything will be okay! 💕",
            'Surprise': "Wow! That was unexpected! 🎉"
        }
        
        self.last_detected_emotion = None
        self.message_display_time = 3000  # 3 secunde
        
        #flag pentru a controla detectarea
        self.is_detection_running = False

    def initialize_camera(self):
        """inițializează camera cu setări optimizate pentru stabilitate"""
        try:
            print("inițializare camera...")
            self.picam2 = Picamera2()
            self.picam2.configure(self.picam2.create_preview_configuration(main={"size": (1280, 720), "format": "RGB888"}))
            self.picam2.start()
            print("camera inițializată cu succes!")
        except Exception as e:
            print(f"eroare la inițializarea camerei: {e}")
            self.picam2 = None

    def start_detection(self):
        """Începe detecția emoțiilor"""
        if self.picam2 is None:
            self.initialize_camera()

        self.is_detection_running = True
        self.stop_button.config(state=tk.NORMAL)
        self.detect_button.config(state=tk.DISABLED)

        # Thread pentru detecția emoțiilor
        self.detection_thread = threading.Thread(target=self.detect_emotion)
        self.detection_thread.daemon = True
        self.detection_thread.start()

        # Thread pentru actualizarea video
        self.video_thread = threading.Thread(target=self.update_video)
        self.video_thread.daemon = True
        self.video_thread.start()

    def stop_detection(self):
        """Oprește detecția emoțiilor și camera"""
        self.is_detection_running = False
        self.stop_button.config(state=tk.DISABLED)
        self.detect_button.config(state=tk.NORMAL)

        if self.picam2:
            self.picam2.stop()
            del self.picam2
            self.picam2 = None

        cv2.destroyAllWindows()

    def detect_emotion(self):
        """Detectează emoțiile"""
        while self.is_detection_running:
            if self.picam2 is None:
                continue

            frame = self.picam2.capture_array()
            frame_resized = cv2.resize(frame, (640, 480), interpolation=cv2.INTER_LINEAR)  # 🔴 Păstrăm proporțiile
            gray = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)

            # 🔴 Stabilizăm detecția fețelor prin creșterea minNeighbors și scaleFactor
            faces = self.face_classifier.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=8, minSize=(50, 50))
            print(f"Detected {len(faces)} face(s).")

            for (x, y, w, h) in faces:
                cv2.rectangle(frame_resized, (x, y), (x+w, y+h), (0, 255, 0), 2)

                roi_gray = gray[y:y + h, x:x + w]
                roi_gray = cv2.resize(roi_gray, (48, 48))

                roi = roi_gray.astype('float32') / 255.0
                roi = np.expand_dims(roi, axis=(0, -1))

                self.emotion_interpreter.set_tensor(self.emotion_input_details[0]['index'], roi)
                self.emotion_interpreter.invoke()
                emotion_preds = self.emotion_interpreter.get_tensor(self.emotion_output_details[0]['index'])

                emotion_label = self.class_labels[emotion_preds.argmax()]
                self.emotion_label.config(text=f"Detected Emotion: {emotion_label}")
                
                if emotion_label != self.last_detected_emotion:
                    self.last_detected_emotion = emotion_label
                    self.message_label.config(text=self.emotion_messages.get(emotion_label, ""))
                    self.root.after(self.message_display_time, lambda: self.message_label.config(text=""))

            frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img = ImageTk.PhotoImage(img)

            self.video_label.config(image=img)
            self.video_label.image = img

            self.root.update_idletasks()
            cv2.waitKey(1)

        if self.picam2:
            self.picam2.stop()

    def update_video(self):
        """Actualizează imaginea video păstrând proporțiile naturale"""
        while self.is_detection_running:
            if self.picam2 is None:
                continue

            frame = self.picam2.capture_array()
            frame_resized = cv2.resize(frame, (640, 480), interpolation=cv2.INTER_LINEAR)  # 🔴 Păstrăm proporțiile
            frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)

            img = Image.fromarray(frame_rgb)
            img = ImageTk.PhotoImage(img)

            self.video_label.config(image=img)
            self.video_label.image = img

            cv2.waitKey(1)

if __name__ == "__main__":
    root = tk.Tk()
    app = EmotionDetectorApp(root)
    root.mainloop()