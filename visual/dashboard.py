import streamlit as st
import matplotlib.pyplot as plt
import networkx as nx
from visual.networkx_adapter import NetworkXAdapter
from sim.simulation import Simulation
from model.graph import Graph
from RouteManager import RouteManager
from RouteTracker import RouteTracker
from RouteOptimizer import RouteOptimizer
from OrderSimulator import OrderSimulator
import random

def run_dashboard():
    st.set_page_config(layout="wide")
    st.title("Sistema de Drones Autónomos - Explore Network")

    # 6 pestañas
    p1, p2, p3, p4, p5 = st.tabs(["Run Simulation", "Explore Network","Clients & Orders", "Route Analytics", "General Statistics"])
    with p1:
        n_nodes = st.slider("Cantidad de nodos", min_value=10, max_value=150, value=15)
        m_edges = st.slider("Cantidad de aristas", min_value=10, max_value=300, value=14)
        n_orders = st.slider("Cantidad de ordenes", min_value=10, max_value=300, value=10)

        if st.button("Iniciar Grafo"):
            if n_nodes < 10 or m_edges < n_nodes - 1:
                st.error("El número de nodos debe ser al menos 10 y el número de aristas debe ser al menos igual a n_nodes - 1 para asegurar conectividad.")
                return

            g = Graph()
            vertices = []
            roles = ['almacen'] * (n_nodes // 5) + ['estacion'] * (n_nodes // 5) + ['cliente'] * (n_nodes - 2 * (n_nodes // 5))
            random.shuffle(roles)

            # Insertar nodos
            for i in range(n_nodes):
                role = roles[i]
                v = g.insert_vertex({
                    'id': i,
                    'almacen': (role == 'almacen'),
                    'cliente': (role == 'cliente'),
                    'estacion': (role == 'estacion')
                })
                vertices.append(v)

            # Paso 1: conectar todos los nodos con al menos un MST-like (árbol generador)
            unconnected = vertices[:]
            connected = [unconnected.pop()]

            while unconnected:
                u = random.choice(connected)
                v = unconnected.pop(random.randint(0, len(unconnected) - 1))
                cost = random.randint(5, 20)
                g.insert_edge(u, v, cost)
                connected.append(v)

            # Paso 2: añadir más aristas aleatorias hasta llegar a m_edges
            existing_edges = n_nodes - 1  # ya agregamos estas
            max_possible_edges = n_nodes * (n_nodes - 1) // 2
            remaining_edges = min(m_edges - existing_edges, max_possible_edges - existing_edges)

            attempts = 0
            while remaining_edges > 0 and attempts < 10 * m_edges:
                u = random.choice(vertices)
                v = random.choice(vertices)
                if u != v and not g.get_edge(u, v):
                    cost = random.randint(5, 20)
                    g.insert_edge(u, v, cost)
                    remaining_edges -= 1
                attempts += 1

            st.session_state.sim = Simulation(g)
            st.success(f"Grafo creado con {n_nodes} nodos y {m_edges} aristas.")

            # Crear ordenes
            st.session_state.sim.order_simulator.process_orders(n_orders)
            print(st.session_state.sim.orders)  # Ahora falta que guarde las ordenes aca


    with p2:
        if "sim" not in st.session_state:
            st.error("Por favor, ejecute la simulación primero.")
            return
        st.subheader("Explorar Red de Drones")

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
            resultado = sim.route_manager.find_route_with_recharge(origen, destino, max_autonomy=50)
            if resultado:
                path = resultado["path"]
                costo = resultado["cost"]
                recs = resultado["recharge_stops"]
                st.text_area("Ruta encontrada:", f"Path: {' → '.join(path)}\nCosto: {costo}\nRecargas: {recs}")
                if st.button("✅ Completar Entrega y Crear Orden"):
                    oid = sim.order_simulator.create_order_from_route(origen, destino, resultado)
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

    with p3:
        st.subheader("Clientes y Órdenes")

    with p4:
        st.subheader("Análisis de Rutas")
    
    with p5:
        st.subheader("Estadísticas Generales")