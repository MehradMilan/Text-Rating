import requests
import random
import string

BASE_URL = "http://localhost:8000/api"  # Replace with your API's base URL

# User details
username = "testuser"
password = "testpassword"
email = "testuser@example.com"

# Helper function to generate random string
def random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Register user
def register_user():
    url = f"{BASE_URL}/register/"
    payload = {
        "username": username,
        "email": email,
        "password": password,
    }
    response = requests.post(url, json=payload)
    if response.status_code == 201:
        print("User registered successfully.")
    elif response.status_code == 400 and "username" in response.json():
        print("User already exists. Proceeding to login.")
    else:
        print("Failed to register user:", response.json())

# Login user
def login_user():
    url = f"{BASE_URL}/login/"
    payload = {
        "username": username,
        "password": password,
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("Login successful.")
        return response.json()["access"]  # Return the access token
    else:
        print("Failed to login:", response.json())
        return None

# Create posts
def create_posts(auth_token):
    url = f"{BASE_URL}/create-post/"
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }
    for _ in range(50):
        payload = {
            "title": random_string(10),
            "content": random_string(50),
        }
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 201:
            print(f"Post created: {response.json()}")
        else:
            print(f"Failed to create post: {response.json()}")

if __name__ == "__main__":
    # Step 1: Register the user
    register_user()

    # Step 2: Login and get the token
    token = login_user()

    if token:
        # Step 3: Create posts
        create_posts(token)
