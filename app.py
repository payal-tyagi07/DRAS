from flask import Flask, jsonify, render_template, request
import subprocess
import json
import math
import os

app = Flask(__name__)
CPP_ENGINE = './dras_engine.exe' if os.name == 'nt' else './dras_engine'

try:
    with open('coords.json', 'r') as f:
        COORDS = json.load(f)
except FileNotFoundError:
    COORDS = {}

# Re-establish 5 Specific Relief Camps
FIXED_CENTERS = []
if COORDS:
    node_ids = list(COORDS.keys())
    step = len(node_ids) // 6
    for i in range(1, 6):
        n_id = node_ids[i * step]
        FIXED_CENTERS.append({"id": n_id, "lat": COORDS[n_id]['lat'], "lng": COORDS[n_id]['lng'], "name": f"Relief Camp {chr(64+i)}"})

def calc_distance(lat1, lon1, lat2, lon2):
    R = 6371e3
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    a = math.sin(math.radians(lat2 - lat1)/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(math.radians(lon2 - lon1)/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def find_nearest_node(lat, lng):
    min_dist, nearest = float('inf'), None
    for node_id, data in COORDS.items():
        dist = (data['lat'] - lat)**2 + (data['lng'] - lng)**2
        if dist < min_dist:
            min_dist = dist
            nearest = node_id
    return nearest

@app.route('/')
def index(): return render_template('index.html')

@app.route('/api/get_fixed_centers', methods=['GET'])
def get_fixed_centers():
    return jsonify({"status": "success", "data": FIXED_CENTERS})

@app.route('/api/analyze_situation', methods=['POST'])
def analyze_situation():
    try:
        data = request.json
        epi_lat, epi_lng, magnitude = float(data['epi_lat']), float(data['epi_lng']), float(data['magnitude'])
        user_lat, user_lng = float(data['user_lat']), float(data['user_lng'])
        
        # 1. Generate Hazards
        z1, z2, z3 = magnitude * 800, magnitude * 1600, magnitude * 2500
        hazards = {}
        for node_id, coords in COORDS.items():
            dist = calc_distance(epi_lat, epi_lng, coords['lat'], coords['lng'])
            if dist < z1: hazards[node_id] = 100
            elif dist < z2: hazards[node_id] = 50
            elif dist < z3: hazards[node_id] = 20
            else: hazards[node_id] = 0
                
        with open('hazards.txt', 'w') as f:
            for node_id in range(len(COORDS)): f.write(f"{hazards.get(str(node_id), 0)}\n")

        # 2. Get Safe Zones (DSU)
        zones_res = subprocess.run([CPP_ENGINE, 'zones'], capture_output=True, text=True, check=True)
        raw_zones = json.loads(zones_res.stdout).get('zones', [])
        
        processed_zones = []
        for idx, zone in enumerate(raw_zones):
            lats = [COORDS[str(n)]['lat'] for n in zone['nodes'] if str(n) in COORDS]
            lngs = [COORDS[str(n)]['lng'] for n in zone['nodes'] if str(n) in COORDS]
            if lats and lngs:
                processed_zones.append({"id": idx+1, "lat": sum(lats)/len(lats), "lng": sum(lngs)/len(lngs), "size": len(zone['nodes'])})

        # 3. Route to Relief Camps
        source_node = find_nearest_node(user_lat, user_lng)
        target_nodes = [str(c['id']) for c in FIXED_CENTERS] # Pass all camps as destinations
        
        cmd = [CPP_ENGINE, 'route', str(source_node)] + target_nodes
        route_res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        route_data = json.loads(route_res.stdout)
        
        if "error" in route_data: return jsonify({"status": "error", "message": route_data["error"]}), 400

        # Draw raw graph path (no more glitchy OSRM)
        gps_path = [[COORDS[str(n)]['lat'], COORDS[str(n)]['lng']] for n in route_data['path'] if str(n) in COORDS]

        return jsonify({
            "status": "success",
            "dsu_zones": processed_zones,
            "safest_route": gps_path,
            "hazard_score": route_data.get('max_hazard_score', 0)
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)