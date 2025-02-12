import tkinter as tk
from tkinter import messagebox
import firebase_admin
from firebase_admin import credentials, firestore

#initialize Firebase only if not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_config.json")
    firebase_admin.initialize_app(cred)

class NotesApp:
    def __init__(self, root, user_data):
        self.root = root
        self.root.title("Notes")
        self.user_data = user_data
        self.db = firestore.client()
        self.notes_ref = self.db.collection('notes').document(self.user_data['uid']).collection('user_notes')

        #frame for notes list
        self.notes_frame = tk.Frame(self.root)
        self.notes_frame.pack(padx=20, pady=20)

        #listbox to display notes
        self.notes_listbox = tk.Listbox(self.notes_frame, height=10, width=50, selectmode=tk.SINGLE)
        self.notes_listbox.pack(side=tk.LEFT, padx=10, pady=10)

        #scrollbar for Listbox
        self.scrollbar = tk.Scrollbar(self.notes_frame, orient=tk.VERTICAL, command=self.notes_listbox.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.notes_listbox.config(yscrollcommand=self.scrollbar.set)

        #buttons for adding and deleting notes
        self.add_button = tk.Button(self.root, text="Add Note", command=self.add_note)
        self.add_button.pack(pady=5)

        self.delete_button = tk.Button(self.root, text="Delete Note", command=self.delete_note)
        self.delete_button.pack(pady=5)

        self.load_notes()

    def load_notes(self):
        """Load notes from Firestore and display them in Listbox."""
        try:
            self.notes_listbox.delete(0, tk.END)
            notes = self.notes_ref.stream()
            for index, note in enumerate(notes, start=1):
                content = note.to_dict().get('content', '')
                self.notes_listbox.insert(tk.END, f"{index}. {content}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load notes: {str(e)}")

    def add_note(self):
        """Add a new note."""
        note_content = self.get_note_content()
        if note_content:
            try:
                self.notes_ref.add({'content': note_content})
                self.load_notes()
                messagebox.showinfo("Success", "Note added successfully!", parent=self.root)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add note: {str(e)}", parent=self.root)
        else:
            messagebox.showwarning("Input Error", "Please enter some text for the note.", parent=self.root)

    def delete_note(self):
        """Delete the selected note."""
        selected_note_index = self.notes_listbox.curselection()
        if selected_note_index:
            selected_note_content = self.notes_listbox.get(selected_note_index).split(". ", 1)[1]  # Get note content without index
            try:
                # Find the document in Firestore based on the content
                notes = self.notes_ref.where('content', '==', selected_note_content).stream()
                for note in notes:
                    self.notes_ref.document(note.id).delete()
                self.load_notes()
                messagebox.showinfo("Success", "Note deleted successfully!", parent=self.root)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete note: {str(e)}", parent=self.root)
        else:
            messagebox.showwarning("Selection Error", "Please select a note to delete.", parent=self.root)

    def get_note_content(self):
        """Open a popup window to get note content from the user."""
        new_window = tk.Toplevel(self.root)
        new_window.title("New Note")

        text_box = tk.Text(new_window, height=10, width=50)
        text_box.pack(padx=10, pady=10)

        content = []

        def save_note():
            note_text = text_box.get("1.0", tk.END).strip()
            if note_text:
                content.append(note_text)  # Save the note content to the list
                new_window.destroy()
            else:
                messagebox.showwarning("Input Error", "Please enter some text for the note.")

        save_button = tk.Button(new_window, text="Save", command=save_note)
        save_button.pack(pady=5)

        self.root.wait_window(new_window)  # Wait until the popup is closed
        return content[0] if content else None

if __name__ == "__main__":
    #example usage for testing
    root = tk.Tk()
    user_data = {"uid": "test_user_id"}  # Replace with actual user data
    app = NotesApp(root, user_data)
    root.mainloop()