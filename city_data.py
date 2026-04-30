# city_data.py

city_coords = {
    "Lucknow": {"lat": 26.8467, "lng": 80.9462},
    "Kanpur": {"lat": 26.4499, "lng": 80.3319},
    "Varanasi": {"lat": 25.3176, "lng": 82.9739},
    "Agra": {"lat": 27.1767, "lng": 78.0081},
    "Noida": {"lat": 28.5355, "lng": 77.3910},
    "Prayagraj": {"lat": 25.4358, "lng": 81.8463},
    "Meerut": {"lat": 28.9845, "lng": 77.7064},
}

city_hospitals = {
    "Lucknow": {"name": "Balrampur Hospital", "lat": 26.8730, "lng": 80.9080, "phone": "0522-2251234"},
    "Kanpur": {"name": "Lala Lajpat Rai Hospital", "lat": 26.4499, "lng": 80.3319, "phone": "0512-2530001"},
    "Varanasi": {"name": "BHU Hospital", "lat": 25.3176, "lng": 82.9739, "phone": "0542-2368558"},
    "Agra": {"name": "SN Medical College", "lat": 27.1767, "lng": 78.0081, "phone": "0562-2850182"},
    "Noida": {"name": "Kailash Hospital", "lat": 28.5355, "lng": 77.3910, "phone": "0120-2443333"},
    "Prayagraj": {"name": "Swarup Rani Nehru Hospital", "lat": 25.4358, "lng": 81.8463, "phone": "0532-2251234"},
    "Meerut": {"name": "PL Sharma Hospital", "lat": 28.9845, "lng": 77.7064, "phone": "0121-2523000"},
}

city_all_hospitals = {
    "Lucknow": [
        {"name": "Balrampur Hospital", "lat": 26.8730, "lng": 80.9080, "phone": "0522-2251234"},
        {"name": "KGMU", "lat": 26.8610, "lng": 80.9310, "phone": "0522-2258000"},
        {"name": "Medanta", "lat": 26.8438, "lng": 80.9919, "phone": "0522-6700000"},
    ],
    "Kanpur": [
        {"name": "Lala Lajpat Rai Hospital", "lat": 26.4499, "lng": 80.3319, "phone": "0512-2530001"},
        {"name": "Ursula Horsman Hospital", "lat": 26.4689, "lng": 80.3428, "phone": "0512-1234567"},
        {"name": "Regency Hospital", "lat": 26.4575, "lng": 80.3175, "phone": "0512-2580000"},
    ],
    "Varanasi": [
        {"name": "BHU Hospital", "lat": 25.3176, "lng": 82.9739, "phone": "0542-2368558"},
        {"name": "Heritage Hospital", "lat": 25.3388, "lng": 82.9970, "phone": "0542-2500000"},
        {"name": "Shiv Prasad Gupta Hospital", "lat": 25.3277, "lng": 82.9718, "phone": "0542-2501234"},
    ],
    "Agra": [
        {"name": "SN Medical College", "lat": 27.1767, "lng": 78.0081, "phone": "0562-2850182"},
        {"name": "Pushpanjali Hospital", "lat": 27.1545, "lng": 78.0350, "phone": "0562-4000000"},
        {"name": "Agra Hospital", "lat": 27.1912, "lng": 78.0205, "phone": "0562-2520500"},
    ],
    "Noida": [
        {"name": "Kailash Hospital", "lat": 28.5355, "lng": 77.3910, "phone": "0120-2443333"},
        {"name": "Jaypee Hospital", "lat": 28.5562, "lng": 77.3798, "phone": "0120-2472222"},
        {"name": "Fortis Hospital", "lat": 28.5755, "lng": 77.3220, "phone": "0120-2442222"},
    ],
    "Prayagraj": [
        {"name": "Swarup Rani Nehru Hospital", "lat": 25.4358, "lng": 81.8463, "phone": "0532-2251234"},
        {"name": "Belly Hospital", "lat": 25.4420, "lng": 81.8375, "phone": "0532-2420000"},
        {"name": "Aravalli Hospital", "lat": 25.4280, "lng": 81.8540, "phone": "0532-2412000"},
    ],
    "Meerut": [
        {"name": "PL Sharma Hospital", "lat": 28.9845, "lng": 77.7064, "phone": "0121-2523000"},
        {"name": "Amar Hospital", "lat": 28.9960, "lng": 77.6800, "phone": "0121-4000000"},
        {"name": "Metro Hospital", "lat": 28.9710, "lng": 77.6990, "phone": "0121-2540000"},
    ],
}

city_emergency = {
    "Police": "112",
    "Ambulance": "108",
    "Fire": "101",
    "Disaster Management": "1077",
    "CM Helpline UP": "1076"
}