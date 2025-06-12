import streamlit as st
import matplotlib.pyplot as plt
import networkx as nx
from visual.networkx_adapter import NetworkXAdapter
from sim.simulation import Simulation
from model.graph import Graph

def run_dashboard():
    st.set_page_config(layout="wide")
    st.title("Sistema de Drones Autónomos - Explore Network")

    # Inicialización del grafo (para demo, aquí puedes cargar uno real)
    if "sim" not in st.session_state:
        g = Graph()
        verts = []
        for i in range(6):
            v = g.insert_vertex({
                'id': i,
                'almacen': (i == 0),
                'cliente': (i in [4, 5]),
                'estacion': (i == 2)
            })
            verts.append(v)
        g.insert_edge(verts[0], verts[1], 10)
        g.insert_edge(verts[1], verts[2], 15)
        g.insert_edge(verts[2], verts[3], 10)
        g.insert_edge(verts[3], verts[4], 10)
        g.insert_edge(verts[3], verts[5], 15)
        st.session_state.sim = Simulation(g)

    sim = st.session_state.sim
    graph_adapter = NetworkXAdapter(sim.graph)
    pos = nx.spring_layout(graph_adapter.nx_graph)

    # Dibujar grafo
    node_colors = []
    node_labels = {}
    for node_id, data in graph_adapter.nx_graph.nodes(data=True):
        if data['role'] == 'almacenamiento':
            node_colors.append('blue')
        elif data['role'] == 'recarga':
            node_colors.append('green')
        else:
            node_colors.append('red')
        node_labels[node_id] = f"{node_id} ({data['role'][0].upper()})"

    fig, ax = plt.subplots(figsize=(8, 6))
    nx.draw_networkx_nodes(graph_adapter.nx_graph, pos, node_color=node_colors, ax=ax)
    nx.draw_networkx_edges(graph_adapter.nx_graph, pos, ax=ax)
    nx.draw_networkx_labels(graph_adapter.nx_graph, pos, labels=node_labels, ax=ax)
    st.pyplot(fig)

    # Interacción de ruta
    st.subheader("Calcular Ruta")

    node_ids = list(graph_adapter.nx_graph.nodes)
    origen = st.selectbox("Origen", node_ids, key="origen")
    destino = st.selectbox("Destino", node_ids, key="destino")

    if st.button("✈ Calcular Ruta"):
        resultado = sim.find_route_with_recharge(origen, destino, max_autonomy=50)
        if resultado:
            path = resultado["path"]
            costo = resultado["cost"]
            recs = resultado["recharge_stops"]
            st.text_area("Ruta encontrada:", f"Path: {' → '.join(path)}\nCosto: {costo}\nRecargas: {recs}")
            if st.button("✅ Completar Entrega y Crear Orden"):
                oid = sim.create_order_from_route(origen, destino, resultado)
                st.success(f"Orden {oid} creada.")
        else:
            st.warning("No se encontró ruta válida con la batería actual.")

    # Mostrar rutas anteriores
    if sim.orders:
        st.sidebar.subheader("🧾 Rutas registradas")
        selected_order = st.sidebar.selectbox("Ver orden", list(sim.orders.keys()))
        od = sim.orders[selected_order]
        st.sidebar.write(f"De: {od['origin']}, A: {od['dest']}, Costo: {od['cost']}")
        if st.sidebar.button("Mostrar ruta registrada"):
            path_edges = [(od["path"][i], od["path"][i+1]) for i in range(len(od["path"]) - 1)]
            fig2, ax2 = plt.subplots(figsize=(8, 6))
            nx.draw_networkx_nodes(graph_adapter.nx_graph, pos, node_color=node_colors, ax=ax2)
            nx.draw_networkx_edges(graph_adapter.nx_graph, pos, ax=ax2)
            nx.draw_networkx_edges(graph_adapter.nx_graph, pos, edgelist=path_edges, edge_color='red', width=2, ax=ax2)
            nx.draw_networkx_labels(graph_adapter.nx_graph, pos, labels=node_labels, ax=ax2)
            st.pyplot(fig2)
