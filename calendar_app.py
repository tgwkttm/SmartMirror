import tkinter as tk
from tkinter import messagebox
from tkcalendar import Calendar
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Initialize Firebase only if not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_config.json")
    firebase_admin.initialize_app(cred)

class CalendarApp:
    def __init__(self, root, user_data):
        self.root = root
        self.root.title("User Calendar")
        self.user_data = user_data
        self.db = firestore.client()
        self.events_ref = self.db.collection('calendar').document(self.user_data['uid']).collection('events')

        self.event_data = {}  # Dictionary to store event data for quick access

        # Frame for calendar and events
        self.calendar_frame = tk.Frame(self.root)
        self.calendar_frame.pack(padx=20, pady=20)

        # Tkinter Calendar widget
        self.calendar = Calendar(self.calendar_frame, selectmode='day', date_pattern='yyyy-mm-dd')
        self.calendar.pack(pady=10)

        # Frame for event actions
        self.events_frame = tk.Frame(self.root)
        self.events_frame.pack(padx=20, pady=20)

        # Buttons for adding and deleting events
        self.add_button = tk.Button(self.events_frame, text="Add Event", command=self.add_event)
        self.add_button.pack(side=tk.LEFT, padx=5)

        self.delete_button = tk.Button(self.events_frame, text="Delete Event", command=self.delete_event)
        self.delete_button.pack(side=tk.LEFT, padx=5)

        self.view_button = tk.Button(self.events_frame, text="View Description", command=self.view_description)
        self.view_button.pack(side=tk.LEFT, padx=5)

        # Listbox to display events
        self.events_listbox = tk.Listbox(self.root, height=10, width=50)
        self.events_listbox.pack(pady=10)

        self.load_events()

    def load_events(self):
        """Load events from Firestore and populate the calendar and Listbox."""
        try:
            self.event_data.clear()
            self.events_listbox.delete(0, tk.END)
            self.calendar.calevent_remove('all')
            
            self.calendar.tag_config('event', background='lightblue', foreground='black')
            
            events = self.events_ref.stream()
            for event in events:
                event_data = event.to_dict()
                date_str = event_data.get('date', '')
                title = event_data.get('title', 'No Title')
                description = event_data.get('description', '')

                if date_str:
                    date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    self.calendar.calevent_create(date, text=title, tags="event")
                    self.event_data[f"{date_str}: {title}"] = description
                    self.events_listbox.insert(tk.END, f"{date_str}: {title}")

            print("Events loaded successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load events: {str(e)}", parent=self.root)

    def add_event(self):
        """Add a new event."""
        selected_date = self.calendar.get_date()

        def save_event():
            title = title_entry.get().strip()
            description = description_entry.get("1.0", tk.END).strip()

            if not title:
                messagebox.showwarning("Input Error", "Please enter a title for the event.", parent=add_window)
                return

            try:
                self.events_ref.add({
                    "title": title,
                    "date": selected_date,
                    "description": description
                })
                add_window.destroy()
                self.load_events()
                messagebox.showinfo("Success", "Event added successfully!", parent=self.root)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add event: {str(e)}", parent=self.root)

        add_window = tk.Toplevel(self.root)
        add_window.title("Add Event")

        tk.Label(add_window, text=f"Date: {selected_date}").pack(pady=5)

        tk.Label(add_window, text="Event Title:").pack()
        title_entry = tk.Entry(add_window, width=30)
        title_entry.pack(pady=5)

        tk.Label(add_window, text="Description:").pack()
        description_entry = tk.Text(add_window, height=5, width=30)
        description_entry.pack(pady=5)

        save_button = tk.Button(add_window, text="Save Event", command=save_event)
        save_button.pack(pady=10)

    def delete_event(self):
        """Delete the selected event."""
        selected_event_index = self.events_listbox.curselection()
        if selected_event_index:
            event_text = self.events_listbox.get(selected_event_index)
            date_str, title = event_text.split(": ", 1)

            try:
                events = self.events_ref.where('date', '==', date_str).where('title', '==', title).stream()
                for event in events:
                    self.events_ref.document(event.id).delete()
                self.load_events()
                messagebox.showinfo("Success", "Event deleted successfully!", parent=self.root)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete event: {str(e)}", parent=self.root)
        else:
            messagebox.showwarning("Selection Error", "Please select an event to delete.", parent=self.root)

    def view_description(self):
        """View the description of the selected event."""
        selected_event_index = self.events_listbox.curselection()
        if selected_event_index:
            event_text = self.events_listbox.get(selected_event_index)
            description = self.event_data.get(event_text, "No description available.")
            messagebox.showinfo("Event Description", description, parent=self.root)
        else:
            messagebox.showwarning("Selection Error", "Please select an event to view its description.", parent=self.root)


if __name__ == "__main__":
    root = tk.Tk()
    user_data = {"uid": "test_user_id"}  # Replace with actual user data
    app = CalendarApp(root, user_data)
    root.mainloop()