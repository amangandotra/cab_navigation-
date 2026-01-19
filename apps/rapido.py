from agent_runner import run_task_sync

def get_prices(pickup, destination):
    goal = f"""
Open Rapido app.
Set pickup location to "{pickup}".
Set destination to "{destination}".
Wait for price info.

Extract all ride options.
Make sure all the details are extracted correctly, no missing fields or incorrect data.

Return JSON array.
DO NOT use remember().
Instead, return the JSON array directly as the reason in complete().

After that, go to the Android home screen.

Return ONLY the JSON array text.
"""

    return run_task_sync(goal)

def book_ride(pickup, destination, vehicle_type):
    goal = f"""
Open Rapido app.
Set pickup to "{pickup}".
Set destination to "{destination}".

Vehicle type preference: {vehicle_type}

Select cheapest option in:
- cab → Cab Economy / Cab Priority
- auto → Auto
- bike → Bike

Tap Book Ride.


the ride should be booked.
confirm booking everything should be managed by you."""
    return run_task_sync(goal)
