from fastapi import FastAPI, HTTPException
from sim.simulation import Simulation
from model.graph import Graph
from model.vertex import Vertex

app = FastAPI()

simulation = None

# comenzar la simulación
@app.post("/start_simulation")
async def start_simulation(grafojson: dict):
    try:
        datos = grafojson.get("grafo", {})
        # Contruir el grafo a partir del JSON recibido
        vertices = datos.get("vertices", [])
        edges = datos.get("edges", [])
        if not vertices or not edges:
            raise HTTPException(status_code=400, detail="Invalid graph data")
        grafo = Graph()
        for vertex in vertices:
            grafo.insert_vertex(vertex.get("data", {}))
        for edge in edges:
            u = Vertex(edge.get("from"))
            v = Vertex(edge.get("to"))
            grafo.insert_edge(u, v, edge.get("cost", {}))
        # Iniciar la simulación
        print("funciona hasta aqui")
        global simulation
        simulation = Simulation(grafo)
        return {"message": "Simulation started successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Obtener simulación
@app.get("/get_simulation")
async def get_simulation():
    global simulation
    if simulation is None:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return simulation