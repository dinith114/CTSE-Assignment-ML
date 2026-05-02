from app.tools.distance_calculator_tool import distance_calculator_tool

result = distance_calculator_tool('Kottawa', 'National Hospital', 'low')
print(f"Distance: {result['distance_km']} km")
print(f"Travel time: {result['estimated_travel_time_minutes']} minutes")
print(f"Route advice: {result['route_advice']}")
print(f"\nFull result:")
print(result)
