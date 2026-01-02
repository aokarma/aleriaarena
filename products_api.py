import os, requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("ALLEGRO_CLIENT_ID")
CLIENT_SECRET = os.getenv("ALLEGRO_CLIENT_SECRET")

def get_allegro_token():
    url = "https://allegro.pl/auth/oauth/token"
    data = {"grant_type": "client_credentials"}
    auth = (CLIENT_ID, CLIENT_SECRET)
    r = requests.post(url, data=data, auth=auth)
    r.raise_for_status()
    return r.json()["access_token"]

def get_allegro_offers(token, limit=10):
    url = "https://api.allegro.pl/offers/listing"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.allegro.public.v1+json"
    }
    params = {"limit": limit}
    r = requests.get(url, headers=headers, params=params)
    r.raise_for_status()
    return r.json()

if __name__ == "__main__":
    token = get_allegro_token()
    data = get_allegro_offers(token)
    print(data)
