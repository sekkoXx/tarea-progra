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
                    resultado = sim.route_manager.find_route_with_recharge(origen, destino, battery_limit=50)
                    if resultado:
                        path = resultado["path"]
                        costo = resultado["total_cost"]
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

    # Pestaña de clientes y órdenes
    with p3:
        st.subheader("📑 Clientes y Órdenes")

            # Verificar simulación
        if "sim" not in st.session_state:
            st.info("Ejecuta primero la simulación en la pestaña 'Run Simulation'.")
        else:
            sim = st.session_state.sim

            # 1) Tabla de clientes registrados
            st.markdown("### 👤 Clientes Registrados")
            client_rows = []
            for v in sim.order_simulator.clients:
                elem = v.element()
                client_rows.append({
                    "Cliente ID": elem["id"],
                    "Cantidad de ordenes": 0
                })
            st.dataframe(client_rows, use_container_width=True)

            # 2) Resumen de órdenes por cliente
            st.markdown("### 📦 Órdenes Totales por Cliente")
            counts = {}
            for order in sim.orders.values():
                cid = order["dest"]
                counts[cid] = counts.get(cid, 0) + 1

            summary = []
            for v in sim.order_simulator.clients:
                cid = v.element()["id"]
                summary.append({
                    "Cliente ID": cid,
                    "Tipo de Orden": "Entrega",
                    "Órdenes Asociadas": counts.get(cid, 0)
                })
            st.dataframe(summary, use_container_width=True)

            # 3) Detalle interactivo para un cliente
            st.markdown("### 🔍 Detalle de Órdenes por Cliente")
            cliente_sel = st.selectbox(
                "Selecciona Cliente ID", 
                sorted(counts.keys()), 
                help="Muestra todas las órdenes entregadas a este cliente"
            )
            detalle = [o for o in sim.orders.values() if o["dest"] == cliente_sel]
            if detalle:
                st.table(detalle)
            else:
                st.warning(f"El cliente {cliente_sel} no ha recibido órdenes.")
    
    with p4:
        st.subheader("📈 Análisis de Rutas")

        # Verificar que la simulación se haya ejecutado
        if 'sim_data' not in st.session_state:
            st.warning("Debes ejecutar la simulación y procesar órdenes antes de ver el análisis de rutas.")
        else:
            _, sim, rt, _, _ = st.session_state.sim_data
            tracker: RouteTracker = rt

            # 1) Selección de cuántas rutas frecuentes mostrar
            top_n = st.slider("Cantidad de rutas frecuentes a mostrar", 1, 20, 10)

            # 2) Obtener y ordenar rutas
            routes = tracker.get_most_frequent_routes(n=top_n)
            if not routes:
                st.warning("No hay rutas registradas todavía.")
            else:
                sorted_routes = sorted(routes, key=lambda x: x[0])

                # 3) Tabla de rutas frecuentes
                st.markdown("#### 📋 Rutas Más Frecuentes")
                df_routes = [
                    {"Ruta": path, "Frecuencia": freq}
                    for path, freq in sorted_routes
                ]
                st.dataframe(df_routes, use_container_width=True)

                # 4) Estadísticas de visitas por nodo
                st.markdown("#### 📍 Visitas por Nodo")
                visitas = tracker.get_node_visit_stats()
                df_visitas = [
                    {"Nodo ID": nid, "Visitas": cnt}
                    for nid, cnt in visitas.items()
                ]
                st.dataframe(df_visitas, use_container_width=True)
                st.bar_chart(visitas)

                # 5) Detalle interactivo de ruta o nodo
                st.markdown("#### 🔍 Detalle Interactivo")
                modo = st.radio("Ver detalle por:", ("Ruta", "Nodo"))
                if modo == "Ruta":
                    rutas_list = [r for r, _ in sorted_routes]
                    ruta_sel = st.selectbox("Selecciona una Ruta", rutas_list)
                    segmentos = ruta_sel.split("→")
                    seg_rows = [
                        {"Segmento": f"{segmentos[i]} → {segmentos[i+1]}"}
                        for i in range(len(segmentos)-1)
                    ]
                    st.table(seg_rows)
                else:
                    nodo_sel = st.selectbox("Selecciona Nodo ID", list(visitas.keys()))
                    st.markdown(f"**Visitas al nodo {nodo_sel}:** {visitas[nodo_sel]}")
                    st.markdown("Rutas frecuentes que incluyen este nodo:")
                    rutas_con_nodo = [
                        path for path, _ in sorted_routes
                        if str(nodo_sel) in path.split("→")
                    ]
                    if rutas_con_nodo:
                        for r in rutas_con_nodo:
                            st.write(f"- {r}")
                    else:
                        st.write("— Ninguna de las rutas frecuentes incluye este nodo.")

                # 6) Visualizar el árbol AVL que guarda las rutas
                st.markdown("#### 🌳 Estructura AVL de Rutas")
                import networkx as nx
                import matplotlib.pyplot as plt

                def build_avl_graph(node, g):
                    if not node:
                        return
                    label = f"{node.key}\\nFreq: {node.value}"
                    g.add_node(label)
                    if node.left:
                        left_label = f"{node.left.key}\\nFreq: {node.left.value}"
                        g.add_edge(label, left_label)
                        build_avl_graph(node.left, g)
                    if node.right:
                        right_label = f"{node.right.key}\\nFreq: {node.right.value}"
                        g.add_edge(label, right_label)
                        build_avl_graph(node.right, g)

                avl_graph = nx.DiGraph()
                build_avl_graph(tracker.avl.root, avl_graph)
                fig, ax = plt.subplots(figsize=(12, 8))
                pos = nx.nx_agraph.graphviz_layout(avl_graph, prog="dot")
                nx.draw(avl_graph, pos,
                        with_labels=True,
                        arrows=False,
                        node_size=3000,
                        node_color="#90caf9",
                        font_size=10,
                        ax=ax)
                st.pyplot(fig)


    with p5:
        st.subheader("Estadísticas Generales")

        if "sim" not in st.session_state:
            st.warning("Primero debes ejecutar una simulación para ver las estadísticas.")
        else:
            sim = st.session_state.sim
            tracker = sim.route_tracker
            graph = sim.graph

            # Contar roles de nodos
            role_counts = {"cliente": 0, "almacenamiento": 0, "recarga": 0}
            for v in graph.vertices():
                if v.is_client:
                    role_counts["cliente"] += 1
                elif v.is_warehouse:
                    role_counts["almacenamiento"] += 1
                elif v.is_recharge:
                    role_counts["recarga"] += 1

            # Gráfico de torta (proporción por rol)
            st.markdown("### Proporción de nodos por tipo")
            fig_pie, ax_pie = plt.subplots()
            ax_pie.pie(role_counts.values(), labels=role_counts.keys(), autopct='%1.1f%%', startangle=140)
            ax_pie.axis('equal')
            st.pyplot(fig_pie)

            # Gráfico de barras (nodos más visitados por tipo)
            visit_stats = tracker.get_node_visit_stats()
            client_visits = {}
            warehouse_visits = {}
            recharge_visits = {}

            for node_id, count in visit_stats.items():
                v = graph.get_vertex(node_id)
                if v:
                    if v.is_client:
                        client_visits[node_id] = count
                    elif v.is_warehouse:
                        warehouse_visits[node_id] = count
                    elif v.is_recharge:
                        recharge_visits[node_id] = count

            st.markdown("### Nodos más visitados por tipo")
            fig_bar, ax_bar = plt.subplots()
            width = 0.25
            labels = list(set(client_visits.keys()) | set(warehouse_visits.keys()) | set(recharge_visits.keys()))
            labels.sort()
            x = range(len(labels))
            c_vals = [client_visits.get(i, 0) for i in labels]
            w_vals = [warehouse_visits.get(i, 0) for i in labels]
            r_vals = [recharge_visits.get(i, 0) for i in labels]

            ax_bar.bar([i - width for i in x], c_vals, width, label='Clientes', color='green')
            ax_bar.bar(x, w_vals, width, label='Almacenes', color='orange')
            ax_bar.bar([i + width for i in x], r_vals, width, label='Estaciones', color='blue')
            ax_bar.set_xticks(x)
            ax_bar.set_xticklabels(labels)
            ax_bar.set_ylabel("Visitas")
            ax_bar.set_title("Visitas por Nodo")
            ax_bar.legend()
            st.pyplot(fig_bar)
