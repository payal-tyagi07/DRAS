# 🚨 DRAS – Disaster Response Assistance System

**Multi‑Incident Emergency Response System** with advanced DSA visualisations, real‑time routing, and live deployment.

![DRAS Demo](https://dras-gw0j.onrender.com) ![Python](https://img.shields.io/badge/Python-3.10-blue) ![Flask](https://img.shields.io/badge/Flask-2.0-red) ![Leaflet](https://img.shields.io/badge/Leaflet-Map-green)

---

## 📌 Overview

DRAS is a web‑based emergency response system for Uttar Pradesh cities. It helps users:
- Locate **hospitals** and **relief centres**.
- Visualise **disaster risk zones** (earthquake, accident, storm, nuclear, etc.).
- Compute **optimal rescue routes** using multiple algorithms.
- Analyse **critical infrastructure** (articulation points, MST, TSP).

Built as a **DSA showcase** – every feature maps directly to a core algorithm.

---

## 🧠 DSA Algorithms Implemented

### ✅ Core Routing
| Algorithm | Use Case | Complexity |
|-----------|----------|-------------|
| **Dijkstra** | Shortest path (distance) | O((V+E) log V) |
| **A*** | Fastest path with heuristic | O(E) with good heuristic |
| **Min‑Max Hazard** | Safest path (minimises max hazard) | O((V+E) log V) |

### ✅ Advanced DSA Features
| Feature | Algorithm / Data Structure | Visualisation |
|---------|----------------------------|----------------|
| Minimum Spanning Tree | Kruskal + Union‑Find | Green dashed lines connecting all hospitals |
| Critical Nodes | Tarjan’s articulation points | Red circles on map |
| Hospital Tour | Nearest neighbour + 2‑opt (TSP approx.) | Purple dashed line visiting all hospitals |
| Graph Connectivity | BFS | Component count & largest component size |

### ✅ Performance Tracking
Every route displays:
- Execution time (ms)
- Number of nodes visited
- Theoretical complexity class

---

## 🗺️ Features

- **7 Uttar Pradesh cities** (Lucknow, Kanpur, Varanasi, Agra, Noida, Prayagraj, Meerut)
- **7 incident types** – Earthquake, Road Accident, Storm, Industrial, Nuclear, Air Accident, Rail Accident
- **Live user location** – GPS, IP fallback, or manual entry
- **Interactive map** (Leaflet + OpenStreetMap)
- **Pre‑defined incident locations** for quick demo
- **Live nearby incidents list** – shows all incidents within 20 km of your location
- **Email alerts** – sends a report of nearby incidents (optional)
- **Algorithm comparison** – side‑by‑side performance of Dijkstra, A*, Min‑Max
- **Fully responsive dashboard** – modern glass‑morphism UI

---

## 🚀 Live Demo

[👉 Click here to try DRAS online](https://dras-gw0j.onrender.com)

*Note: Free tier may sleep – refresh after a few seconds.*

---

## 🛠️ Tech Stack

### Backend
- **Flask 2.0** – Web framework
- **Gunicorn** – Production WSGI server
- **Requests** – IP geolocation API calls
- **Python 3.10+** – All algorithms implemented in pure Python

### Frontend
- **Leaflet.js** – Interactive maps
- **HTML5 / CSS3** – Glassmorphism, responsive layout
- **JavaScript (ES6)** – Dynamic UI, API fetches

### Deployment
- **GitHub** – Version control
- **Render** – Free cloud hosting

---

## 📂 Project Structure
