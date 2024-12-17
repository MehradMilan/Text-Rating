import requests

REGISTER_API_URL = "http://localhost:8000/api/register/"
LOGIN_API_URL = "http://localhost:8000/api/login/"
RATING_API_URL = "http://localhost:8000/api/ratings/"

POST_ID = 1
USER_COUNT = 20
ANOMALOUS_SCORE = 1

def register_users(user_count):
    print("\n--- Registering Users ---")
    for i in range(1, user_count + 1):
        username = f"testuser{i}"
        password = "password"
        email = f"testuser{i}@example.com"

        response = requests.post(REGISTER_API_URL, json={
            "username": username,
            "password": password,
            "email": email
        })
        if response.status_code == 201:
            print(f"Registered user {username}")
        elif "username" in response.text:
            print(f"User {username} already exists.")
        else:
            print(f"Failed to register user {username}: {response.text}")

def login_users(user_count):
    print("\n--- Logging In Users ---")
    tokens = []
    for i in range(1, user_count + 1):
        username = f"testuser{i}"
        password = "password"
        response = requests.post(LOGIN_API_URL, data={"username": username, "password": password})
        if response.status_code == 200:
            token = response.json().get("access")
            tokens.append(token)
            print(f"Logged in user {username}")
        else:
            print(f"Failed to log in user {username}: {response.text}")
    return tokens

def submit_anomalous_ratings(tokens, post_id, score):
    print("\n--- Submitting Anomalous Ratings ---")
    headers_template = {"Content-Type": "application/json"}
    for token in tokens:
        headers = headers_template.copy()
        headers["Authorization"] = f"Bearer {token}"
        payload = {"post": post_id, "score": score}

        response = requests.post(RATING_API_URL, json=payload, headers=headers)
        if response.status_code == 200:
            print(f"Submitted rating {score} for user token {token[-10:]}...")
        else:
            print(f"Failed to submit rating: {response.text}")

if __name__ == "__main__":
    print("Starting Anomaly Simulation...\n")

    register_users(USER_COUNT)

    tokens = login_users(USER_COUNT)
    if not tokens:
        print("No users could log in. Exiting...")
        exit()

    print("\nSimulating anomaly with low ratings...")
    submit_anomalous_ratings(tokens, POST_ID, ANOMALOUS_SCORE)

    print("\n--- Simulation Complete ---")
    print("Verify Redis buffer and average rating to confirm anomaly detection.")