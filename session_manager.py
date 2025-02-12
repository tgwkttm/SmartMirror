import os
import json
import requests

def save_session(user_data):
    """salvează sesiunea utilizatorului într-un fișier JSON."""
    try:
        with open("session.json", "w") as file:
            json.dump(user_data, file)
        print("[INFO] Sesiunea utilizatorului a fost salvată!")
    except Exception as e:
        print(f"[ERROR] Nu s-a putut salva sesiunea: {e}")

def load_session():
    """incearcă să încarce sesiunea salvată, dacă există."""
    if os.path.exists("session.json"):
        try:
            with open("session.json", "r") as file:
                user_data = json.load(file)
                print(f"[INFO] Sesiune găsită: {user_data}")
                return user_data
        except Exception as e:
            print(f"[ERROR] Nu s-a putut încărca sesiunea: {e}")
    return None

def clear_session():
    """sterge sesiunea utilizatorului din fișierul JSON."""
    try:
        if os.path.exists("session.json"):
            os.remove("session.json")
            print("[INFO] Sesiunea utilizatorului a fost ștearsă!")
    except Exception as e:
        print(f"[ERROR] Nu s-a putut șterge sesiunea: {e}")
        
def logout_from_firebase():
    """sterge sesiunea locală și forțează o reautentificare la următorul login."""
    print("[INFO] Delogare locală...")

    clear_session()  # stergem fișierul session.json
    
    print("[INFO] Sesiunea locală ștearsă! La următorul login, utilizatorul trebuie să se autentifice din nou.")