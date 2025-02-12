import firebase_admin
from firebase_admin import credentials, auth

#initialize the Firebase Admin SDK
cred = credentials.Certificate("firebase_config.json")
firebase_admin.initialize_app(cred)

#function to create a new user
def create_user(email, password):
    try:
        user = auth.create_user(
            email=email,
            password=password
        )
        print(f'Successfully created new user: {user.uid}')
    except Exception as e:
        print(f'Error creating new user: {e}')

#function to verify user
def verify_user(uid):
    try:
        user = auth.get_user(uid)
        print(f'Successfully fetched user data: {user.email}')
    except Exception as e:
        print(f'Error fetching user data: {e}')

if __name__ == "__main__":
    test_email = "testuser@example.com"
    test_password = "Test@12345"
    
    # Create a new user
    create_user(test_email, test_password)
    
    # Use the user UID you got from the creation step above
    # uid = 'user-uid-from-create-step'
    # verify_user(uid)
