from default_incidents import DEFAULT_INCIDENTS
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import math, heapq, requests, time
from city_data import city_coords, city_hospitals, city_all_hospitals, city_emergency

app = Flask(__name__)
CORS(app)

# ---------- Incident hazard profiles (unchanged) ----------
INCIDENT_PROFILES = {
    "earthquake": {"radii": [0.8, 1.6, 2.5], "hazards": [100, 50, 20]},
    "road_accident": {"radii": [0.1, 0.3, 0.6], "hazards": [80, 40, 10]},
    "storm": {"radii": [2.0, 4.0, 7.0], "hazards": [70, 40, 15]},
    "industrial": {"radii": [0.5, 1.0, 2.0], "hazards": [90, 60, 30]},
    "nuclear": {"radii": [1.5, 3.0, 5.0], "hazards": [100, 80, 50]},
    "air_accident": {"radii": [0.3, 0.8, 1.5], "hazards": [85, 45, 20]},
    "rail_accident": {"radii": [0.2, 0.5, 1.0], "hazards": [75, 35, 10]},
}

def get_hazard_for_incident(incident_type, distance_km, magnitude=5.0):
    profile = INCIDENT_PROFILES.get(incident_type, INCIDENT_PROFILES["earthquake"])
    if incident_type == "earthquake":
        r1, r2, r3 = [r * magnitude for r in profile["radii"]]
    else:
        r1, r2, r3 = profile["radii"]
    haz1, haz2, haz3 = profile["hazards"]
    if distance_km < r1:
        return haz1
    elif distance_km < r2:
        return haz2
    elif distance_km < r3:
        return haz3
    else:
        return 0

# ---------- Graph generation ----------
def build_graph_for_city(city):
    hospitals = city_all_hospitals.get(city, [])
    if not hospitals:
        return {}, {}
    points = [(city_coords[city]['lat'], city_coords[city]['lng'], "center")]
    for h in hospitals:
        points.append((h['lat'], h['lng'], h['name']))
    lats = [p[0] for p in points]
    lngs = [p[1] for p in points]
    min_lat, max_lat = min(lats), max(lats)
    min_lng, max_lng = min(lngs), max(lngs)
    step = 0.02
    for lat in [min_lat + step, max_lat - step]:
        for lng in [min_lng + step, max_lng - step]:
            points.append((lat, lng, f"grid_{lat}_{lng}"))
    nodes = {}
    for i, (lat, lng, name) in enumerate(points):
        nodes[str(i)] = {"lat": lat, "lng": lng, "name": name}
    graph = {str(i): [] for i in range(len(nodes))}
    def haversine(lat1, lng1, lat2, lng2):
        R = 6371
        dlat = math.radians(lat2 - lat1)
        dlng = math.radians(lng2 - lng1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng/2)**2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    for i in range(len(nodes)):
        for j in range(i+1, len(nodes)):
            dist = haversine(nodes[str(i)]['lat'], nodes[str(i)]['lng'],
                             nodes[str(j)]['lat'], nodes[str(j)]['lng'])
            if dist <= 15:
                graph[str(i)].append((str(j), dist))
                graph[str(j)].append((str(i), dist))
    return nodes, graph

CITY_GRAPHS = {}
CITY_NODES = {}

def get_city_graph(city):
    if city not in CITY_GRAPHS:
        CITY_NODES[city], CITY_GRAPHS[city] = build_graph_for_city(city)
    return CITY_NODES[city], CITY_GRAPHS[city]

# ---------- Routing Algorithms (Dijkstra, A*, Min-Max) ----------
def dijkstra(graph, start, end):
    dist = {node: float('inf') for node in graph}
    prev = {}
    dist[start] = 0
    pq = [(0, start)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        if u == end:
            break
        for v, w in graph.get(u, []):
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))
    if dist[end] == float('inf'):
        return []
    path = []
    cur = end
    while cur in prev:
        path.append(cur)
        cur = prev[cur]
    path.append(start)
    return path[::-1]

def heuristic(node, end, nodes):
    n1 = nodes[node]
    n2 = nodes[end]
    R = 6371
    dlat = math.radians(n2['lat'] - n1['lat'])
    dlng = math.radians(n2['lng'] - n1['lng'])
    a = math.sin(dlat/2)**2 + math.cos(math.radians(n1['lat'])) * math.cos(math.radians(n2['lat'])) * math.sin(dlng/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def a_star(graph, start, end, nodes):
    open_set = [(0, start)]
    came_from = {}
    g_score = {node: float('inf') for node in graph}
    g_score[start] = 0
    f_score = {node: float('inf') for node in graph}
    f_score[start] = heuristic(start, end, nodes)
    while open_set:
        _, current = heapq.heappop(open_set)
        if current == end:
            break
        for neighbor, w in graph.get(current, []):
            tentative_g = g_score[current] + w
            if tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristic(neighbor, end, nodes)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))
    if g_score[end] == float('inf'):
        return []
    path = []
    cur = end
    while cur in came_from:
        path.append(cur)
        cur = came_from[cur]
    path.append(start)
    return path[::-1]

def minmax_hazard_path(graph, nodes, start, end, incident_lat, incident_lng, incident_type, magnitude=5.0):
    hazard = {}
    for node_id, coords in nodes.items():
        dist_km = calc_distance(incident_lat, incident_lng, coords['lat'], coords['lng']) / 1000.0
        hazard[node_id] = get_hazard_for_incident(incident_type, dist_km, magnitude)
    max_hazard = {node: float('inf') for node in graph}
    max_hazard[start] = hazard[start]
    prev = {}
    pq = [(hazard[start], start)]
    while pq:
        cur_max, u = heapq.heappop(pq)
        if cur_max > max_hazard[u]:
            continue
        if u == end:
            break
        for v, _ in graph.get(u, []):
            new_max = max(cur_max, hazard[v])
            if new_max < max_hazard[v]:
                max_hazard[v] = new_max
                prev[v] = u
                heapq.heappush(pq, (new_max, v))
    if max_hazard[end] == float('inf'):
        return [], 0
    path = []
    cur = end
    while cur in prev:
        path.append(cur)
        cur = prev[cur]
    path.append(start)
    return path[::-1], max_hazard[end]

def calc_distance(lat1, lng1, lat2, lng2):
    R = 6371e3
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlng/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def find_nearest_node(lat, lng, nodes):
    min_dist = float('inf')
    nearest = None
    for node_id, coords in nodes.items():
        dist = (coords['lat'] - lat)**2 + (coords['lng'] - lng)**2
        if dist < min_dist:
            min_dist = dist
            nearest = node_id
    return nearest

# ---------- DSA: Union-Find for Kruskal (MST) ----------
class DSU:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n
    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x
    def union(self, x, y):
        xr, yr = self.find(x), self.find(y)
        if xr == yr:
            return False
        if self.rank[xr] < self.rank[yr]:
            self.parent[xr] = yr
        elif self.rank[xr] > self.rank[yr]:
            self.parent[yr] = xr
        else:
            self.parent[yr] = xr
            self.rank[xr] += 1
        return True

def kruskal_mst(graph, nodes):
    edges = []
    node_list = list(nodes.keys())
    idx = {node: i for i, node in enumerate(node_list)}
    for u, neigh in graph.items():
        for v, w in neigh:
            if idx[u] < idx[v]:
                edges.append((w, idx[u], idx[v]))
    edges.sort()
    dsu = DSU(len(nodes))
    mst = []
    total = 0.0
    for w, u_i, v_i in edges:
        if dsu.union(u_i, v_i):
            mst.append((node_list[u_i], node_list[v_i], w))
            total += w
    return mst, total

# ---------- DSA: Floyd-Warshall (all-pairs) ----------
def floyd_warshall(graph, nodes):
    node_list = list(nodes.keys())
    n = len(node_list)
    idx = {node: i for i, node in enumerate(node_list)}
    INF = float('inf')
    dist = [[INF] * n for _ in range(n)]
    for i in range(n):
        dist[i][i] = 0
    for u, neigh in graph.items():
        for v, w in neigh:
            i, j = idx[u], idx[v]
            if w < dist[i][j]:
                dist[i][j] = w
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
    return dist, idx

# ---------- DSA: Articulation points (Tarjan) ----------
def find_articulation_points(graph, nodes):
    node_list = list(nodes.keys())
    idx = {node: i for i, node in enumerate(node_list)}
    n = len(node_list)
    adj = [[] for _ in range(n)]
    for u, neigh in graph.items():
        for v, _ in neigh:
            adj[idx[u]].append(idx[v])
    visited = [False] * n
    disc = [-1] * n
    low = [-1] * n
    parent = [-1] * n
    ap = [False] * n
    time_counter = 0
    def dfs(u):
        nonlocal time_counter
        children = 0
        visited[u] = True
        disc[u] = low[u] = time_counter
        time_counter += 1
        for v in adj[u]:
            if not visited[v]:
                parent[v] = u
                children += 1
                dfs(v)
                low[u] = min(low[u], low[v])
                if parent[u] == -1 and children > 1:
                    ap[u] = True
                if parent[u] != -1 and low[v] >= disc[u]:
                    ap[u] = True
            elif v != parent[u]:
                low[u] = min(low[u], disc[v])
    for i in range(n):
        if not visited[i]:
            dfs(i)
    articulation_nodes = [node_list[i] for i in range(n) if ap[i]]
    coords = [nodes[node] for node in articulation_nodes]
    return articulation_nodes, coords

# ---------- DSA: TSP (Nearest neighbour + 2-opt) ----------
def nearest_neighbor_tsp(dist_matrix, start_idx):
    n = len(dist_matrix)
    visited = [False] * n
    order = [start_idx]
    visited[start_idx] = True
    current = start_idx
    for _ in range(n - 1):
        next_idx = min((i for i in range(n) if not visited[i]), key=lambda i: dist_matrix[current][i])
        order.append(next_idx)
        visited[next_idx] = True
        current = next_idx
    return order

def two_opt(route, dist_matrix):
    improved = True
    best = route[:]
    n = len(route)
    while improved:
        improved = False
        for i in range(1, n - 2):
            for j in range(i + 1, n - 1):
                if j - i == 1:
                    continue
                new_route = best[:i] + best[i:j+1][::-1] + best[j+1:]
                def total_dist(r):
                    return sum(dist_matrix[r[k]][r[k+1]] for k in range(len(r)-1))
                if total_dist(new_route) < total_dist(best):
                    best = new_route
                    improved = True
                    break
            if improved:
                break
    return best

# ---------- DSA: Graph connectivity (BFS) ----------
def count_components(graph, nodes):
    visited = set()
    components = 0
    largest = 0
    for node in nodes:
        if node not in visited:
            components += 1
            queue = [node]
            visited.add(node)
            count = 0
            while queue:
                u = queue.pop(0)
                count += 1
                for v, _ in graph.get(u, []):
                    if v not in visited:
                        visited.add(v)
                        queue.append(v)
            largest = max(largest, count)
    return components, largest

# ---------- Existing API Endpoints ----------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/cities', methods=['GET'])
def get_cities():
    return jsonify({"cities": list(city_coords.keys())})

@app.route('/api/city_coords', methods=['POST'])
def city_coords_endpoint():
    data = request.json
    city = data.get('city')
    if city not in city_coords:
        return jsonify({"status": "error", "message": "City not found"}), 404
    return jsonify({"status": "success", "lat": city_coords[city]["lat"], "lng": city_coords[city]["lng"]})

@app.route('/api/emergency_contacts', methods=['GET'])
def emergency_contacts():
    return jsonify(city_emergency)

@app.route('/api/nearest_hospital', methods=['POST'])
def nearest_hospital():
    data = request.json
    city = data.get('city')
    if city not in city_hospitals:
        return jsonify({"status": "error", "message": "No hospital data"}), 404
    return jsonify({"status": "success", "hospital": city_hospitals[city]})

@app.route('/api/hospitals', methods=['POST'])
def get_hospitals():
    data = request.json
    city = data.get('city')
    hospitals = city_all_hospitals.get(city, [])
    return jsonify({"status": "success", "hospitals": hospitals})

@app.route('/api/ip_location', methods=['GET', 'OPTIONS'])
def ip_location():
    if request.method == 'OPTIONS':
        return '', 204
    services = [
        {'url': 'https://ipapi.co/json/', 'parser': lambda d: {'lat': d.get('latitude'), 'lng': d.get('longitude'), 'city': d.get('city'), 'country': d.get('country_name')}},
        {'url': 'https://ip-api.com/json/', 'parser': lambda d: {'lat': d.get('lat'), 'lng': d.get('lon'), 'city': d.get('city'), 'country': d.get('country')} if d.get('status') == 'success' else None},
        {'url': 'https://ipwhois.app/json/', 'parser': lambda d: {'lat': d.get('latitude'), 'lng': d.get('longitude'), 'city': d.get('city'), 'country': d.get('country')} if d.get('success') else None}
    ]
    for service in services:
        try:
            resp = requests.get(service['url'], timeout=10)
            resp.raise_for_status()
            data = resp.json()
            result = service['parser'](data)
            if result and result.get('lat') and result.get('lng'):
                lat = float(result['lat'])
                lng = float(result['lng'])
                if -90 <= lat <= 90 and -180 <= lng <= 180:
                    return jsonify({"status": "success", "lat": lat, "lng": lng, "city": result.get('city', 'Unknown'), "country": result.get('country', 'Unknown')})
        except:
            continue
    return jsonify({"status": "error", "message": "IP location services unavailable"}), 503

# ---------- NEW DSA ENDPOINTS ----------
@app.route('/api/mst', methods=['POST'])
def api_mst():
    data = request.json
    city = data.get('city')
    nodes, graph = get_city_graph(city)
    if not nodes:
        return jsonify({"status": "error", "message": "Graph not available"}), 500
    mst_edges, total_len = kruskal_mst(graph, nodes)
    coords = []
    for u, v, w in mst_edges:
        coords.append([nodes[u]['lat'], nodes[u]['lng']])
        coords.append([nodes[v]['lat'], nodes[v]['lng']])
    return jsonify({"status": "success", "mst_coords": coords, "total_length_km": round(total_len,2), "edges": len(mst_edges)})

@app.route('/api/articulation_points', methods=['POST'])
def api_articulation_points():
    data = request.json
    city = data.get('city')
    nodes, graph = get_city_graph(city)
    if not nodes:
        return jsonify({"status": "error"}), 500
    art_nodes, coords = find_articulation_points(graph, nodes)
    return jsonify({"status": "success", "articulation_points": art_nodes, "coordinates": coords})

@app.route('/api/all_pairs', methods=['POST'])
def api_all_pairs():
    data = request.json
    city = data.get('city')
    nodes, graph = get_city_graph(city)
    if not nodes:
        return jsonify({"status": "error"}), 500
    dist, idx = floyd_warshall(graph, nodes)
    INF = float('inf')
    total = 0.0
    count = 0
    n = len(nodes)
    for i in range(n):
        for j in range(n):
            if i != j and dist[i][j] < INF:
                total += dist[i][j]
                count += 1
    avg = total / count if count else 0
    return jsonify({"status": "success", "average_distance_km": round(avg,2), "nodes_processed": n})

@app.route('/api/hospital_tour', methods=['POST'])
def hospital_tour():
    data = request.json
    city = data.get('city')
    user_lat = float(data['user_lat'])
    user_lng = float(data['user_lng'])
    nodes, graph = get_city_graph(city)
    if not nodes:
        return jsonify({"status": "error", "message": "Graph not available"}), 500
    # Identify hospital nodes (those with 'hospital' in name or in city_hospitals list)
    hospital_nodes = [nid for nid, info in nodes.items() if 'hospital' in info['name'].lower() or 'Hospital' in info['name']]
    if not hospital_nodes:
        return jsonify({"status": "error", "message": "No hospitals found"}), 404
    user_node = find_nearest_node(user_lat, user_lng, nodes)
    all_points = [user_node] + hospital_nodes
    n = len(all_points)
    # Precompute all-pairs shortest paths using Dijkstra from each point (small n)
    import sys
    INF_DIST = 999999
    dist_matrix = [[INF_DIST]*n for _ in range(n)]
    for i, src in enumerate(all_points):
        # Dijkstra from src
        dist = {node: float('inf') for node in graph}
        dist[src] = 0
        pq = [(0, src)]
        while pq:
            d, u = heapq.heappop(pq)
            if d > dist[u]:
                continue
            for v, w in graph.get(u, []):
                nd = d + w
                if nd < dist[v]:
                    dist[v] = nd
                    heapq.heappush(pq, (nd, v))
        for j, tgt in enumerate(all_points):
            dist_matrix[i][j] = dist[tgt] if dist[tgt] != float('inf') else INF_DIST
    # Solve TSP from user (index 0)
    tour = nearest_neighbor_tsp(dist_matrix, 0)
    tour = two_opt(tour, dist_matrix)
    # Build coordinate list
    coords = []
    for idx in tour:
        node_id = all_points[idx]
        coords.append([nodes[node_id]['lat'], nodes[node_id]['lng']])
    total_dist = sum(dist_matrix[tour[i]][tour[i+1]] for i in range(len(tour)-1))
    return jsonify({
        "status": "success",
        "tour_coords": coords,
        "total_distance_km": round(total_dist,2),
        "hospitals_visited": len(hospital_nodes)
    })

@app.route('/api/connectivity', methods=['POST'])
def api_connectivity():
    data = request.json
    city = data.get('city')
    nodes, graph = get_city_graph(city)
    if not nodes:
        return jsonify({"status": "error"}), 500
    components, largest = count_components(graph, nodes)
    return jsonify({"status": "success", "components": components, "total_nodes": len(nodes), "largest_component_size": largest})

# ---------- Updated /api/route_to_hospital with performance tracking ----------
@app.route('/api/route_to_hospital', methods=['POST'])
def route_to_hospital():
    try:
        data = request.json
        city = data.get('city')
        incident_lat = float(data['incident_lat'])
        incident_lng = float(data['incident_lng'])
        magnitude = float(data.get('magnitude', 5.0))
        user_lat = float(data['user_lat'])
        user_lng = float(data['user_lng'])
        hospital_lat = float(data['hospital_lat'])
        hospital_lng = float(data['hospital_lng'])
        algorithm = data.get('algorithm', 'minmax')
        incident_type = data.get('incident_type', 'earthquake')
        start_time = time.perf_counter()
        nodes, graph = get_city_graph(city)
        if not nodes or not graph:
            return jsonify({"status": "error", "message": "Graph not available"}), 500
        source = find_nearest_node(user_lat, user_lng, nodes)
        target = find_nearest_node(hospital_lat, hospital_lng, nodes)
        if source is None or target is None:
            return jsonify({"status": "error", "message": "Location not on graph"}), 400
        if algorithm == 'dijkstra':
            path_nodes = dijkstra(graph, source, target)
            hazard_score = 0
            complexity = "O((V+E) log V) with binary heap"
        elif algorithm == 'astar':
            path_nodes = a_star(graph, source, target, nodes)
            hazard_score = 0
            complexity = "O(E) with optimal heuristic"
        else:  # minmax
            path_nodes, hazard_score = minmax_hazard_path(graph, nodes, source, target,
                                                          incident_lat, incident_lng,
                                                          incident_type, magnitude)
            complexity = "O((V+E) log V) min‑max variant"
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        if not path_nodes:
            return jsonify({"status": "error", "message": "No path found"}), 404
        path_coords = [[nodes[n]['lat'], nodes[n]['lng']] for n in path_nodes if n in nodes]
        return jsonify({
            "status": "success",
            "safest_route": path_coords,
            "hazard_score": hazard_score,
            "dsu_zones": [],
            "performance": {
                "time_ms": round(elapsed_ms, 3),
                "nodes_visited": len(path_nodes),
                "algorithm": algorithm.upper(),
                "complexity": complexity
            }
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/default_incidents/<city>', methods=['GET'])
def get_default_incidents(city):
    incidents = DEFAULT_INCIDENTS.get(city, [])
    return jsonify({"status": "success", "incidents": incidents})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)