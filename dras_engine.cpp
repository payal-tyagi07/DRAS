#include <iostream>
#include <vector>
#include <queue>
#include <fstream>
#include <algorithm>
#include <string>

// Notice: <unordered_set> is completely gone from here!

using namespace std;

const double INF = 1e15;

struct Edge { int to; double weight; };

int n, m;
vector<vector<Edge>> graph;
vector<int> hazards;

void loadData() {
    ifstream infile("graph.txt");
    if(!infile) return;
    infile >> n >> m;
    graph.resize(n);
    for (int i = 0; i < m; ++i) {
        int u, v; double w;
        infile >> u >> v >> w;
        graph[u].push_back({v, w});
    }
    infile.close();

    hazards.resize(n, 0);
    ifstream hazfile("hazards.txt");
    if(hazfile) {
        for (int i = 0; i < n; ++i) hazfile >> hazards[i];
    }
}

// --- DSU: Find Safe Zone Clusters (For UI Visuals Only) ---
struct DSU {
    vector<int> parent, size;
    DSU(int n) {
        parent.resize(n); size.resize(n, 1);
        for(int i=0; i<n; i++) parent[i] = i;
    }
    int find(int v) {
        if (v == parent[v]) return v;
        return parent[v] = find(parent[v]);
    }
    void unite(int a, int b) {
        a = find(a); b = find(b);
        if (a != b) {
            if (size[a] < size[b]) swap(a, b);
            parent[b] = a;
            size[a] += size[b];
        }
    }
};

vector<vector<int>> getSafeComponents() {
    DSU dsu(n);
    for (int u = 0; u < n; ++u) {
        if (hazards[u] > 0) continue; 
        for (auto& edge : graph[u]) {
            if (hazards[edge.to] == 0) dsu.unite(u, edge.to);
        }
    }
    vector<vector<int>> components(n);
    for (int i = 0; i < n; ++i) {
        if (hazards[i] == 0) components[dsu.find(i)].push_back(i);
    }
    vector<pair<int, int>> sizes;
    for (int i = 0; i < n; ++i) {
        if (!components[i].empty()) sizes.push_back({(int)components[i].size(), i});
    }
    sort(sizes.rbegin(), sizes.rend());
    vector<vector<int>> top_components;
    for (size_t i = 0; i < min((size_t)3, sizes.size()); ++i) top_components.push_back(components[sizes[i].second]);
    return top_components;
}

// --- KADANE'S: Damage Assessment ---
pair<int, pair<int, int>> runKadane(const vector<int>& path) {
    if(path.empty()) return {0, {0,0}};
    int max_so_far = hazards[path[0]], curr_max = hazards[path[0]];
    int start = 0, end = 0, temp_start = 0;
    for (size_t i = 1; i < path.size(); i++) {
        if (hazards[path[i]] > curr_max + hazards[path[i]]) {
            curr_max = hazards[path[i]]; temp_start = i;
        } else curr_max += hazards[path[i]];

        if (curr_max > max_so_far) { max_so_far = curr_max; start = temp_start; end = i; }
    }
    return {max_so_far, {start, end}};
}

// --- DIJKSTRA: Route to specific Relief Camps ---
void runDijkstra(int source, const vector<int>& targets) {
    vector<bool> is_target(n, false);
    for(int t : targets) if(t >= 0 && t < n) is_target[t] = true;

    vector<double> dist(n, INF);
    vector<int> parent(n, -1);
    priority_queue<pair<double, int>, vector<pair<double, int>>, greater<pair<double, int>>> pq;

    dist[source] = 0;
    pq.push({0, source});
    int best_target = -1;

    while (!pq.empty()) {
        int u = pq.top().second;
        double d = pq.top().first;
        pq.pop();

        if (is_target[u]) { best_target = u; break; } // STOP ONLY AT A RELIEF CAMP
        if (d > dist[u]) continue;

        for (auto& edge : graph[u]) {
            int v = edge.to;
            double cost = edge.weight * (1.0 + (hazards[v] * 10.0)); 
            if (dist[u] + cost < dist[v]) {
                dist[v] = dist[u] + cost;
                parent[v] = u;
                pq.push({dist[v], v});
            }
        }
    }

    if (best_target == -1) { cout << "{\"error\": \"No path to any Relief Camp found.\"}" << endl; return; }

    vector<int> path;
    for (int at = best_target; at != -1; at = parent[at]) path.push_back(at);
    reverse(path.begin(), path.end());

    auto damage_report = runKadane(path);

    cout << "{\"algorithm\": \"Dijkstra+Kadane\", \"target_reached\": " << best_target << ", \"path\": [";
    for (size_t i = 0; i < path.size(); ++i) cout << path[i] << (i == path.size() - 1 ? "" : ", ");
    cout << "], \"max_hazard_score\": " << damage_report.first << "}" << endl;
}

int main(int argc, char* argv[]) {
    if (argc < 2) return 1;
    string mode = argv[1];
    loadData();

    if (mode == "zones") {
        auto comps = getSafeComponents();
        cout << "{\"zones\": [";
        for (size_t i = 0; i < comps.size(); ++i) {
            cout << "{\"nodes\": [";
            for(size_t j = 0; j < comps[i].size(); ++j) cout << comps[i][j] << (j == comps[i].size()-1 ? "" : ",");
            cout << "]}" << (i == comps.size()-1 ? "" : ",");
        }
        cout << "]}" << endl;
    } 
    else if (mode == "route") {
        int source = stoi(argv[2]);
        vector<int> targets;
        // Read all remaining arguments as target nodes
        for(int i = 3; i < argc; ++i) targets.push_back(stoi(argv[i]));
        runDijkstra(source, targets);
    }
    return 0;
}