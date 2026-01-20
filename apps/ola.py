from agent_runner import run_task_sync

def get_prices(pickup, destination):
    goal = f"""
Open Ola app.
Set pickup location to "{pickup}".
Set destination to "{destination}".
Wait for price list.

Extract cab options with price and ETA.
Make sure all the details are extracted correctly, no missing fields or incorrect data.

Return JSON array like:
[
  {{"service":"Mini","price":200,"eta":7}}
]
DO NOT use remember().
Instead, return the JSON array directly as the reason in complete().

After that, go to the Android home screen.

Return ONLY the JSON array text.
"""

    return run_task_sync(goal)

def book_ride(pickup, destination, vehicle_type):
    goal = f"""
Open Ola app.
If pickup or destination is not set,
Set pickup location to "{pickup}".
Set destination to "{destination}".
and if already set, verify they are correct.
if not correct, update them.

Vehicle type preference: {vehicle_type}

Select cheapest option in:
- cab → Mini / Prime / Economy
- auto → Auto
- bike → Bike

Tap Book Ride.

the ride should be booked.
confirm booking everything should be managed by you."""
    return run_task_sync(goal)
