import tkinter as tk
from tkinter import Label, Entry, Button, messagebox
from firebase_admin import auth

class SignUpWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Register")
        self.root.geometry("800x600")
        self.root.configure(bg="black")

        self.label_email = Label(root, text="Email:", font=("Helvetica", 14), fg="white", bg="black")
        self.label_email.pack(pady=10)

        self.entry_email = Entry(root, font=("Helvetica", 14), bg="black", fg="white", insertbackground="white")
        self.entry_email.pack(pady=10)

        self.label_password = Label(root, text="Password:", font=("Helvetica", 14), fg="white", bg="black")
        self.label_password.pack(pady=10)

        self.entry_password = Entry(root, show="*", font=("Helvetica", 14), bg="black", fg="white", insertbackground="white")
        self.entry_password.pack(pady=10)

        self.label_username = Label(root, text="Username:", font=("Helvetica", 14), fg="white", bg="black")
        self.label_username.pack(pady=10)

        self.entry_username = Entry(root, font=("Helvetica", 14), bg="black", fg="white", insertbackground="white")
        self.entry_username.pack(pady=10)

        self.signup_button = Button(root, text="Register", command=self.register_user, font=("Helvetica", 14), bg="grey", fg="white", activebackground="darkgrey", activeforeground="white")
        self.signup_button.pack(pady=20)

    def register_user(self):
        email = self.entry_email.get()
        password = self.entry_password.get()
        username = self.entry_username.get()

        try:
            user = auth.create_user(
                email=email,
                password=password,
                display_name=username
            )
            messagebox.showinfo("Registration Successful", "User created successfully!")
            # Implement logic for face recognition setup (optional)
        except Exception as e:
            messagebox.showerror("Registration Failed", str(e))
