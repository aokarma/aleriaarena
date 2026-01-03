import requests
import json
import os
from pathlib import Path

CLIENT_ID = "99e59d9e334648ac87aab0bf4b877cc2"
CLIENT_SECRET = "oCaGFIp447oYOWkGA4FnN3Vht4QlI5OYR85cKxWKOGfTL0Agqk51BobQx9EcbWKu"
# USER_ID = "141492764"   # login sprzedawcy
USER_ID = "galeriaarena"   # login sprzedawcy

# -----------------------------------------
# 1. Pobranie tokenu
# -----------------------------------------
def get_token():
    url = "https://allegro.pl/auth/oauth/token"
    data = {
        "grant_type": "client_credentials"
    }
    response = requests.post(url, data=data, auth=(CLIENT_ID, CLIENT_SECRET))
    response.raise_for_status()
    return response.json()["access_token"]

# -----------------------------------------
# 2. Pobranie listy ofert użytkownika
# -----------------------------------------
def get_user_offers(token):
    url = f"https://api.allegro.pl/sale/offers?limit=100&seller.id={USER_ID}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.allegro.public.v1+json"
    }

    offers = []
    while url:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        data = r.json()

        offers.extend(data["offers"])
        url = data.get("nextPage", {}).get("href")

    return offers

# -----------------------------------------
# 3. Pobranie szczegółów oferty
# -----------------------------------------
def get_offer_details(token, offer_id):
    url = f"https://api.allegro.pl/sale/offers/{offer_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.allegro.public.v1+json"
    }
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.json()

# -----------------------------------------
# 4. Pobranie zdjęć
# -----------------------------------------
def download_images(images, folder):
    Path(folder).mkdir(parents=True, exist_ok=True)

    for i, img in enumerate(images):
        url = img["url"]
        ext = url.split("?")[0].split(".")[-1]
        filename = f"{folder}/img_{i}.{ext}"

        try:
            data = requests.get(url).content
            with open(filename, "wb") as f:
                f.write(data)
        except:
            pass

# -----------------------------------------
# 5. Główna logika
# -----------------------------------------
def main():
    token = get_token()
    offers = get_user_offers(token)

    results = []

    for offer in offers:
        offer_id = offer["id"]
        print("Pobieram:", offer["name"])

        details = get_offer_details(token, offer_id)

        # Pobieranie zdjęć
        images = details.get("images", [])
        download_images(images, f"zdjecia/{offer_id}")

        results.append({
            "id": offer_id,
            "tytul": details.get("name"),
            "opis": details.get("description", {}).get("sections", []),
            "cena": details.get("sellingMode", {}).get("price", {}).get("amount"),
            "waluta": details.get("sellingMode", {}).get("price", {}).get("currency"),
            "parametry": details.get("parameters", []),
            "zdjecia": [img["url"] for img in images]
        })

    # Zapis do JSON
    with open("produkty.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    print("Zakończono!")

if __name__ == "__main__":
    main()
