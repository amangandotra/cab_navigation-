from agent_runner import run_task_sync

def get_prices(pickup, destination):
    goal = f"""
    Open Uber app.
    Set pickup location to "{pickup}".
    Set destination to "{destination}".
    Wait until price options are visible.

    Extract all available cab options with:
    - service name
    - price in INR
    - ETA in minutes
    Make sure all the details are extracted correctly, no missing fields or incorrect data.
    Create a JSON array like:
    [
      {{"service":"Uber Go","price":325.14,"eta":2}},
      {{"service":"Bike Saver","price":224.41,"eta":4}}
    ]

    DO NOT use remember().
    Instead, return the JSON array directly as the reason in complete().

    After that, go to the Android home screen.

    Return ONLY the JSON array text.
    """

    result = run_task_sync(goal)

    if result["json"] is None:
        return {
            "error": "No JSON extracted",
            "reason": result["reason"]
        }

    return result["json"]



def book_ride(pickup, destination, vehicle_type):
    goal = f"""
Open Uber app.
If pickup or destination is not set,
Set pickup location to "{pickup}".
Set destination to "{destination}".
and if already set, verify they are correct.
if not correct, update them.
Vehicle type preference: {vehicle_type}

If vehicle_type is:
- cab: choose Uber Go / Sedan / Mini / Prime
- auto: choose Auto
- bike: choose Bike Saver / Moto

Select the cheapest option in that category.

Tap Book or Confirm Ride button.


the ride should be booked.
confirm booking everything should be managed by you."""

    return run_task_sync(goal)
