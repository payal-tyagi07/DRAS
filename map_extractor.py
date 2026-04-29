import osmnx as ox
import json

def build_graph():
    print("Downloading OSM graph for Faridabad...")
    # Fetch driving network for Faridabad
    G = ox.graph_from_place("Faridabad, Haryana, India", network_type='drive')
    
    nodes = list(G.nodes())
    node_mapping = {old_id: new_id for new_id, old_id in enumerate(nodes)}
    
    edges = []
    # Extract edges and their lengths (weights)
    for u, v, data in G.edges(data=True):
        weight = data.get('length', 1.0)
        edges.append((node_mapping[u], node_mapping[v], weight))
        
    print(f"Graph built: {len(nodes)} nodes, {len(edges)} edges.")

    # Save mathematical graph for C++
    with open('graph.txt', 'w') as f:
        f.write(f"{len(nodes)} {len(edges)}\n")
        for u, v, w in edges:
            f.write(f"{u} {v} {w}\n")

    # Save GPS mapping for Frontend
    coords = {new_id: {'lat': G.nodes[old_id]['y'], 'lng': G.nodes[old_id]['x']} 
              for old_id, new_id in node_mapping.items()}
    
    with open('coords.json', 'w') as f:
        json.dump(coords, f)
        
    print("Export complete. C++ ready.")

if __name__ == "__main__":
    build_graph()