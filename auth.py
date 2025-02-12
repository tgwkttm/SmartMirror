import requests

FIREBASE_WEB_API_KEY = 'AIzaSyAgLz3RD7F9qef2jDIrlCeouOuQHrGdRlI'

def sign_in_with_email_and_password(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        return response.json().get('error', {}).get('message', 'Autentificare eșuată')

if __name__ == "__main__":
    email = input("Email: ")
    password = input("Parolă: ")
    result = sign_in_with_email_and_password(email, password)
    print(result)