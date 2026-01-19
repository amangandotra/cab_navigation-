# main.py
from apps import uber, ola, rapido
from compareprices import compare_and_choose
import json

def main():
    pickup = input("Pickup location: ").strip()
    destination = input("Destination: ").strip()

    print("\nFetching Uber prices...")
    uber_data = uber.get_prices(pickup, destination)
    print("Uber raw:", uber_data)

    print("\nFetching Ola prices...")
    ola_data = ola.get_prices(pickup, destination)
    print("Ola raw:", ola_data)

    print("\nFetching Rapido prices...")
    rapido_data = rapido.get_prices(pickup, destination)
    print("Rapido raw:", rapido_data)

    print("\n=== SUMMARY ===")
    print("Uber:", uber_data)
    print("Ola:", ola_data)
    print("Rapido:", rapido_data)

    print("\nChoose service type:")
    print("1 = Cab")
    print("2 = Auto")
    print("3 = Bike")

    choice = input("Enter choice (1/2/3): ").strip()
    if choice not in ("1","2","3"):
        print("Invalid choice, defaulting to Cab (1).")
        choice = "1"

    print("\nComparing options using Gemini + fallback logic...")
    winner = compare_and_choose(uber_data, ola_data, rapido_data, choice)
    print("\nGemini (or fallback) chose:", winner)
    # best_app = compare_and_choose(uber_data, ola_data, rapido_data, choice)
    # print("\nBest option selected by Gemini:", best_app)

    if winner == "NoServiceFound":
        print("No matching services found for your vehicle choice.")
        return

    vehicle_type_map = {"1":"cab","2":"auto","3":"bike"}
    vehicle_type = vehicle_type_map.get(choice, "cab")

    print(f"\nBooking on {winner} for {vehicle_type}...")
    if winner == "Uber":
        res = uber.book_ride(pickup, destination, vehicle_type)
    elif winner == "Ola":
        res = ola.book_ride(pickup, destination, vehicle_type)
    elif winner == "Rapido":
        res = rapido.book_ride(pickup, destination, vehicle_type)
    else:
        print("Unknown winner:", winner)
        return

    print("Booking result (raw):", res)


if __name__ == "__main__":
    main()
