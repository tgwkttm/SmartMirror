import pickle

with open("encodings.pickle", "rb") as f:
    data = pickle.load(f)

print(f"Utilizatori salvați în encodings.pickle: {set(data['names'])}")