import pickle

# UID-ul utilizatorului de șters (înlocuiește cu UID-ul vechi al mamei tale)
user_to_remove = "JQKmrx6FYpbV3ArusuRprqSGMmm1"

# Încarcă datele existente
with open("encodings.pickle", "rb") as f:
    data = pickle.load(f)

# Filtrează encodările, eliminând pe cele ale utilizatorului șters
new_encodings = {"encodings": [], "names": []}
for encoding, name in zip(data["encodings"], data["names"]):
    if name != user_to_remove:  # Păstrează doar utilizatorii care NU sunt cel șters
        new_encodings["encodings"].append(encoding)
        new_encodings["names"].append(name)

# Salvează fișierul actualizat fără encodările vechi
with open("encodings.pickle", "wb") as f:
    pickle.dump(new_encodings, f)

print(f"[INFO] Encodările utilizatorului {user_to_remove} au fost șterse.")