import tkinter as tk
from datetime import datetime

class LoginOptionsWindow:
    def __init__(self, root, main_app):
        self.root = root
        self.main_app = main_app

        #set window title
        self.root.title("Login Options")

        #set window background color to black and make it full screen
        self.root.configure(bg="black")
        self.root.attributes("-fullscreen", True)

        #escape key to exit full screen
        self.root.bind("<Escape>", self.exit_fullscreen)

        #create a frame with black background
        self.frame = tk.Frame(self.root, bg="black")
        self.frame.pack(expand=True)

        #new User button
        self.new_user_button = tk.Button(self.frame, text="New User", command=self.open_new_user_window, bg="grey", fg="white", font=("Helvetica", 16))
        self.new_user_button.pack(pady=10)

        #existing User button
        self.existing_user_button = tk.Button(self.frame, text="Existing User", command=self.open_existing_user_window, bg="grey", fg="white", font=("Helvetica", 16))
        self.existing_user_button.pack(pady=10)

    def open_new_user_window(self):
        self.main_app.open_new_user_window()

    def open_existing_user_window(self):
        self.main_app.open_existing_user_window()

    def exit_fullscreen(self, event=None):
        self.root.attributes("-fullscreen", False)

if __name__ == "__main__":
    class MainApp:
        def open_new_user_window(self):
            print("New User button clicked")

        def open_existing_user_window(self):
            print("Existing User button clicked")

    root = tk.Tk()
    app = LoginOptionsWindow(root, MainApp())
    root.mainloop()