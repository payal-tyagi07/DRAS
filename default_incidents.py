# default_incidents.py

# Each incident: name, lat, lng, type, magnitude (if earthquake, else optional)
DEFAULT_INCIDENTS = {
    "Lucknow": [
        {"name": "Hazratganj Market Fire", "lat": 26.8550, "lng": 80.9340, "type": "industrial", "magnitude": None},
        {"name": "Gomti Nagar Road Accident", "lat": 26.8400, "lng": 80.9560, "type": "road_accident", "magnitude": None},
        {"name": "Charbagh Railway Station Accident", "lat": 26.8467, "lng": 80.9462, "type": "rail_accident", "magnitude": None},
        {"name": "Kaiserbagh Earthquake (simulated)", "lat": 26.8630, "lng": 80.9215, "type": "earthquake", "magnitude": 6.2},
    ],
    "Kanpur": [
        {"name": "Kalpi Road Accident", "lat": 26.4540, "lng": 80.3180, "type": "road_accident", "magnitude": None},
        {"name": "Ganga Barrage Industrial Leak", "lat": 26.4800, "lng": 80.3120, "type": "industrial", "magnitude": None},
        {"name": "Kanpur Central Station Rail Accident", "lat": 26.4499, "lng": 80.3319, "type": "rail_accident", "magnitude": None},
        {"name": "Jajmau Nuclear Alert (drill)", "lat": 26.4290, "lng": 80.3060, "type": "nuclear", "magnitude": None},
    ],
    "Varanasi": [
        {"name": "Dashashwamedh Ghat Crowd Stampede", "lat": 25.3176, "lng": 82.9739, "type": "storm", "magnitude": None},  # treat as storm-like incident
        {"name": "Varanasi Airport Air Accident", "lat": 25.4405, "lng": 82.8650, "type": "air_accident", "magnitude": None},
        {"name": "BHU Hospital Area Earthquake", "lat": 25.3176, "lng": 82.9739, "type": "earthquake", "magnitude": 5.4},
    ],
    "Agra": [
        {"name": "Taj Mahal Area Terror Alert", "lat": 27.1767, "lng": 78.0081, "type": "industrial", "magnitude": None},
        {"name": "Agra Fort – Rail Accident", "lat": 27.1795, "lng": 78.0215, "type": "rail_accident", "magnitude": None},
        {"name": "Fatehabad Road Flooding", "lat": 27.1560, "lng": 78.0380, "type": "storm", "magnitude": None},
    ],
    "Noida": [
        {"name": "Sector 18 Mall Fire", "lat": 28.5730, "lng": 77.3235, "type": "industrial", "magnitude": None},
        {"name": "DND Flyway Accident", "lat": 28.5870, "lng": 77.3140, "type": "road_accident", "magnitude": None},
        {"name": "Noida Metro Rail Accident", "lat": 28.5355, "lng": 77.3910, "type": "rail_accident", "magnitude": None},
        {"name": "Sector 62 Earthquake (simulated)", "lat": 28.6265, "lng": 77.3580, "type": "earthquake", "magnitude": 5.0},
    ],
    "Prayagraj": [
        {"name": "Sangam Area Stampede (Kumbh scenario)", "lat": 25.4358, "lng": 81.8463, "type": "storm", "magnitude": None},
        {"name": "Prayagraj Junction Rail Accident", "lat": 25.4358, "lng": 81.8463, "type": "rail_accident", "magnitude": None},
        {"name": "Industrial Fire in Naini", "lat": 25.3950, "lng": 81.8450, "type": "industrial", "magnitude": None},
    ],
    "Meerut": [
        {"name": "Mall Road Accident", "lat": 28.9845, "lng": 77.7064, "type": "road_accident", "magnitude": None},
        {"name": "Meerut Cantt Rail Accident", "lat": 29.0000, "lng": 77.7000, "type": "rail_accident", "magnitude": None},
        {"name": "Earthquake near Sardhana", "lat": 29.1450, "lng": 77.6140, "type": "earthquake", "magnitude": 5.2},
    ],
}