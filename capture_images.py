import cv2  

def capture_images(self, user_directory, user_uid):
    try:
        camera = Picamera2()
        config = camera.create_still_configuration(main={"size": (1024, 768)})
        camera.configure(config)
        camera.start()
        time.sleep(2)

        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        for i in range(10):
            frame = camera.capture_array()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detectează fețele din imagine
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(50, 50))

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)  #draw rectangle on the face

            #display the video stream for users 
            cv2.imshow("Position your face correctly", frame)

            img_name = f"image_{i}.jpg"
            img_path = os.path.join(user_directory, img_name)
            cv2.imwrite(img_path, frame)  #save the image

            print(f"Captured {img_name}")

            #wait
            if cv2.waitKey(500) & 0xFF == ord("q"):
                break

        camera.stop()
        cv2.destroyAllWindows()  #close the window after capturing

        firebase_user_manager.upload_user_images(user_uid, user_directory)
        firebase_user_manager.link_images_to_user(user_uid, user_directory)
        messagebox.showinfo("Capture complete", "The image capture is complete!")
        self.main_app.open_login_options_window()

    except Exception as e:
        messagebox.showerror("Error", f"There's an error at capturing the pictures: {str(e)}")