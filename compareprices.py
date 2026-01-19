# compareprices.py
import os
import json
import re
import google.generativeai as genai

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "models/gemini-1.0-pro"
  # fast & cheap

def normalize_data(uber_data, ola_data, rapido_data, choice):
    vehicle_map = {
        "1": ["cab", "mini", "prime", "sedan", "economy", "xl", "go"],
        "2": ["auto"],
        "3": ["bike", "moto"]
    }

    keywords = vehicle_map.get(choice, [])
    normalized = []

    # ---------- Uber ----------
    if isinstance(uber_data, list):
        for item in uber_data:
            service = str(item.get("service", "")).lower()
            if any(k in service for k in keywords):
                normalized.append({
                    "app": "Uber",
                    "price": float(item.get("price", 99999)),
                    "eta": int(item.get("eta", 999))
                })

    # ---------- Ola ----------
    ola_list = []

    if isinstance(ola_data, dict):
        ola_list = ola_data.get("json") or []
    elif isinstance(ola_data, list):
        ola_list = ola_data

    for item in ola_list:
        if not isinstance(item, dict):
            continue

        service = str(item.get("service", "")).lower()
        if any(k in service for k in keywords):
            normalized.append({
                "app": "Ola",
                "price": float(item.get("price", 99999)),
                "eta": int(item.get("eta", 999))
            })

    # ---------- Rapido ----------
    rapido_list = []

    if isinstance(rapido_data, dict):
        rapido_list = rapido_data.get("json") or []
    elif isinstance(rapido_data, list):
        rapido_list = rapido_data

    for item in rapido_list:
        if not isinstance(item, dict):
            continue

        service = str(item.get("ride_type", "")).lower()
        if any(k in service for k in keywords):
            price_raw = str(item.get("estimated_fare", "99999")).replace("₹", "").strip()
            eta_raw = str(item.get("eta") or item.get("time") or "999")

            try:
                price = float(price_raw)
            except:
                price = 99999

            try:
                eta = int("".join(c for c in eta_raw if c.isdigit()))
            except:
                eta = 999

            normalized.append({
                "app": "Rapido",
                "price": price,
                "eta": eta
            })

    return normalized

def ask_gemini(data):
    prompt = f"""
You are given ride options from multiple cab apps.

Data:
{json.dumps(data, indent=2)}

Rules:
- Prefer lowest price
- If prices are close, prefer lower ETA

Respond with ONLY ONE WORD:
Uber OR Ola OR Rapido

No explanation.
"""

    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content(prompt)

    text = response.text.strip()

    for app in ["Uber", "Ola", "Rapido"]:
        if app.lower() in text.lower():
            return app

    return None


def fallback_logic(data):
    data.sort(key=lambda x: (x["price"], x["eta"]))
    return data[0]["app"]


def compare_and_choose(uber_data, ola_data, rapido_data, choice):
    normalized = normalize_data(uber_data, ola_data, rapido_data, choice)

    if not normalized:
        return "NoServiceFound"

    try:
        gemini_choice = ask_gemini(normalized)
        if gemini_choice in ["Uber", "Ola", "Rapido"]:
            return gemini_choice
    except Exception as e:
        print("Gemini error:", e)

    # Fallback
    return fallback_logic(normalized)
