import streamlit as st
import random 
from model.graph import Graph
from RouteManager import RouteManager
from RouteOptimizer import RouteOptimizer
from RouteTracker import RouteTracker
from OrderSimulator import OrderSimulator

st.set_page_config(page_title="Pestaña 1", layout="centered")

n_nodes = st.slider("Cantidad de nodos", min_value=10, max_value=150, value=15)
m_edges = st.slider("Cantidad de aristas", min_value=10, max_value=300, value=14)
n_orders = st.slider("Cantidad de ordenes", min_value=10, max_value=300, value=5)

if st.button("Star Simulaton"):
    g = Graph()
    verts = []

    for i in range (n_nodes):
        element = {
            'id': i,
            'almacen': (i < max(1, n_nodes // 10)),
            'cliente': (i >= n_nodes - max(1, n_nodes // 10)),
            'estacion': (i % 5 == 0 and i != 0)
        }
        verts.append(g.insert_vertex(element))

    edge_count = 0
    while edge_count < m_edges:
        u = random.choice(verts)
        v = random.choice(verts)
        if u != v and not g.get_edge(u, v):
            g.insert_edge(u, v, random.randint(5, 20))
            edge_count += 1

    rm = RouteManager(g)
    rt = RouteTracker()
    ro = RouteOptimizer(rt, rm)
    sim = OrderSimulator(g, rm, rt, ro)


    st.subheader("Órdenes procesadas:")
    output = ""
    for i in range(1, n_orders + 1):
        o = random.choice(sim.warehouses)
        d = random.choice(sim.clients)
        route = ro.suggest_optimized_route(o.element()['id'], d.element()['id'])
        if not route:
            output += f"Orden #{i}: No se encontró ruta de {o.element()['id']} a {d.element()['id']}\n"
            continue
        path = route['path']
        cost = route['total_cost']
        recs = route.get('recharge_stops', [])
        rt.register_route(path, cost)
        output += f"Orden #{i}: {o.element()['id']} → {d.element()['id']}\n"
        output += f"Ruta: {'→'.join(map(str, path))}\n"
        output += f"Costo: {cost} | Recargas: {recs} | Estado: Entregado\n\n"

    st.text(output)

    st.subheader("Estadísticas de nodos:")
    warehouses = sum(1 for v in g.vertices() if v.is_warehouse)
    clients = sum(1 for v in g.vertices() if v.is_client)
    stations = sum(1 for v in g.vertices() if v.is_recharge)

    total = n_nodes
    st.markdown(f"""
    - 🏬 Almacenes: {warehouses} ({warehouses/total:.0%})  
    - 🧍 Clientes: {clients} ({clients/total:.0%})  
    - ⚡ Estaciones de recarga: {stations} ({stations/total:.0%})  
    """)

    st.subheader("⭐ Rutas más frecuentes:")
    for r, f in rt.get_most_frequent_routes(5):
        st.write(f" {r} — {f} usos")

    st.subheader("📍 Visitas por nodo:")
    st.write(rt.get_node_visit_stats())

    st.subheader("Reporte de Optimización:")
    st.text(ro.get_optimization_report())