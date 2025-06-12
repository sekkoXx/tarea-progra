import streamlit as st
import matplotlib.pyplot as plt
import networkx as nx
import random
from visual.networkx_adapter import NetworkXAdapter
from sim.simulation import Simulation
from model.graph import Graph
from RouteManager import RouteManager
from RouteTracker import RouteTracker
from RouteOptimizer import RouteOptimizer
from OrderSimulator import OrderSimulator

def run_dashboard():
    st.set_page_config(layout="wide")
    st.title("Sistema de Drones Autónomos")

    # 6 pestañas
    p1, p2, p3, p4, p5 = st.tabs(["Run Simulation", "Explore Network","Clients & Orders", "Route Analytics", "General Statistics"])
    with p1:
        n_nodes = st.slider("Cantidad de nodos", min_value=10, max_value=150, value=15)
        m_edges = st.slider("Cantidad de aristas", min_value=10, max_value=300, value=14)
        n_orders = st.slider("Cantidad de órdenes", min_value=10, max_value=300, value=10)

        if st.button("Iniciar Grafo"):
            if n_nodes < 10 or m_edges < n_nodes - 1:
                st.error("El número de nodos debe ser al menos 10 y el número de aristas al menos n_nodes - 1.")
                return

            g = Graph()
            vertices = []
            roles = ['almacen'] * (n_nodes // 5) + ['estacion'] * (n_nodes // 5) + ['cliente'] * (n_nodes - 2 * (n_nodes // 5))
            random.shuffle(roles)

            for i in range(n_nodes):
                role = roles[i]
                v = g.insert_vertex({
                    'id': i,
                    'almacen': (role == 'almacen'),
                    'cliente': (role == 'cliente'),
                    'estacion': (role == 'estacion')
                })
                vertices.append(v)

            # Conexión tipo MST
            unconnected = vertices[:]
            connected = [unconnected.pop()]
            while unconnected:
                u = random.choice(connected)
                v = unconnected.pop(random.randint(0, len(unconnected) - 1))
                cost = random.randint(5, 20)
                g.insert_edge(u, v, cost)
                connected.append(v)

            # Aristas adicionales
            existing_edges = n_nodes - 1
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

            for _ in range(n_orders):
                order_simulator = OrderSimulator(g, st.session_state.sim.route_manager, st.session_state.sim.route_tracker, st.session_state.sim.route_optimizer)
                results = order_simulator.process_orders(1)
                for result in results:
                    st.session_state.sim.orders[result['order_id']] = {
                        "origin": result['origin'],
                        "dest": result['dest'],
                        "path": result['path'],
                        "cost": result['cost'],
                        "recharges": result['recharges'],
                        "status": "Por entregar"
                    }
            st.success(f"Órdenes procesadas: {len(st.session_state.sim.orders)}")
            print(st.session_state.sim.orders)

    # --------------------------
    # TAB 2: Explore Network
    # --------------------------
    with p2:
        st.header("🌍 Explorar Red de Transporte")

        if "sim" not in st.session_state:
            st.warning("Primero debes crear un grafo en la pestaña 'Run Simulation'.")
        else:
            sim = st.session_state.sim
            graph = sim.graph
            adapter = NetworkXAdapter(graph)
            G = adapter.get_networkx_graph()
            pos = nx.spring_layout(G, seed=42)

            # Dibujar red
            node_colors = []
            node_labels = {}
            for node_id, data in G.nodes(data=True):
                role = data["role"]
                if role == "almacenamiento":
                    node_colors.append("orange")
                elif role == "recarga":
                    node_colors.append("blue")
                else:
                    node_colors.append("green")
                node_labels[node_id] = f"{node_id} ({role[0].upper()})"

            fig, ax = plt.subplots(figsize=(10, 6))
            nx.draw(G, pos, node_color=node_colors, with_labels=False, ax=ax)
            nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=10, ax=ax)
            nx.draw_networkx_edge_labels(G, pos, edge_labels=nx.get_edge_attributes(G, 'weight'), font_size=8, ax=ax)
            st.pyplot(fig)

            # Selectbox
            node_ids = list(G.nodes)
            origen = st.selectbox("Nodo Origen", node_ids, key="origen")
            destino = st.selectbox("Nodo Destino", node_ids, key="destino")

            if st.button("✈ Calcular Ruta"):
                if origen == destino:
                    st.error("El nodo origen y destino no pueden ser iguales.")
                else:
                    resultado = sim.find_route_with_recharge(origen, destino, max_autonomy=50)
                    if resultado:
                        path = resultado["path"]
                        costo = resultado["cost"]
                        recs = resultado["recharge_stops"]

                        st.success(f"Ruta encontrada: {' → '.join(map(str, path))} | Costo: {costo}")
                        st.markdown(f"🚉 Recargas: {', '.join(map(str, recs)) if recs else 'No se usaron'}")

                        path_edges = [(path[i], path[i+1]) for i in range(len(path)-1)]
                        fig2, ax2 = plt.subplots(figsize=(10, 6))
                        nx.draw(G, pos, node_color=node_colors, ax=ax2)
                        nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=10, ax=ax2)
                        nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color="red", width=2, ax=ax2)
                        st.pyplot(fig2)

                        if st.button("✅ Completar Entrega y Crear Orden"):
                            oid = sim.create_order_from_route(origen, destino, resultado)
                            st.success(f"Orden {oid} creada exitosamente.")
                    else:
                        st.warning("No se encontró una ruta válida con la batería actual.")

            # Mostrar rutas anteriores
            if sim.orders:
                st.sidebar.subheader("📜 Rutas registradas")
                selected_order = st.sidebar.selectbox("Ver orden", list(sim.orders.keys()))
                od = sim.orders[selected_order]
                st.sidebar.write(f"De: {od['origin']}, A: {od['dest']}, Costo: {od['cost']}")
                if st.sidebar.button("Mostrar ruta registrada"):
                    path_edges = [(od["path"][i], od["path"][i+1]) for i in range(len(od["path"]) - 1)]
                    fig3, ax3 = plt.subplots(figsize=(10, 6))
                    nx.draw(G, pos, node_color=node_colors, ax=ax3)
                    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=10, ax=ax3)
                    nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color='red', width=2, ax=ax3)
                    st.pyplot(fig3)

            # Leyenda
            with st.expander("ℹ Leyenda de colores"):
                st.markdown("""
                - 🥚 **Naranja**: Almacenamiento  
                - 🔵 **Azul**: Recarga  
                - 🥾 **Verde**: Cliente  
                - 🔴 **Rojo**: Ruta calculada
                """)

    with p3:
        st.subheader("Clientes y Órdenes")

    with p4:
        st.subheader("Análisis de Rutas")

    with p5:
        st.subheader("Estadísticas Generales")
