import streamlit as st
from streamlit_folium import st_folium
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
import folium

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
                    'estacion': (role == 'estacion'),
                    'lat': random.uniform(-38.8, -38.6),  # Latitudes de Temuco
                    'lon': random.uniform(-72.7, -72.5)   # Longitudes de Temuco
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
        st.header("🌍 Explore Network (Geolocalizado)")

        if "sim" not in st.session_state:
            st.warning("Primero debes crear un grafo en la pestaña 'Run Simulation'.")
        else:
            sim = st.session_state.sim
            graph = sim.graph

            # 1) Prepara la lista de vértices por rol
            almacenes = [v for v in graph.vertices() if v.is_warehouse]
            clientes  = [v for v in graph.vertices() if v.is_client]
            estaciones = [v for v in graph.vertices() if v.is_recharge]

            # 2) Controles de selección
            origen = st.selectbox(
                "Nodo Origen (📦 Almacén)",
                options=[v.element()["id"] for v in almacenes],
                format_func=lambda x: f"Almacén {x}"
            )
            destino = st.selectbox(
                "Nodo Destino (👤 Cliente)",
                options=[v.element()["id"] for v in clientes],
                format_func=lambda x: f"Cliente {x}"
            )
            algoritmo = st.radio(
                "Algoritmo de ruta",
                ("Dijkstra", "Floyd-Warshall")
            )

            col1, col2, col3 = st.columns([1,1,1])
            calculate_btn = col1.button("✈️ Calculate Route")
            mst_btn       = col2.button("🌲 Show MST")
            complete_btn  = col3.button("✅ Complete Delivery and Create Order")

            # 3) Crea el mapa centrado en Temuco
            m = folium.Map(location=[-38.7359, -72.5904], zoom_start=13)

            # 4) Dibuja todos los nodos
            def draw_vertex(v):
                lat, lon = v.element()["lat"], v.element()["lon"]
                role = ("almacenamiento" if v.is_warehouse 
                        else "recarga" if v.is_recharge 
                        else "cliente")
                color = {"almacenamiento":"orange","recarga":"blue","cliente":"green"}[role]
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=6,
                    color=color,
                    fill=True,
                    fill_opacity=0.9,
                    popup=f"{v.element()['id']} ({role})"
                ).add_to(m)

            for v in graph.vertices():
                draw_vertex(v)

            # 5) Dibuja todas las aristas
            for edge in graph.edges():
                u, v = edge.endpoints()
                data = edge.cost()

                lat1, lon1 = u.element()["lat"], u.element()["lon"]
                lat2, lon2 = v.element()["lat"], v.element()["lon"]
                folium.PolyLine(
                    locations=[(lat1, lon1), (lat2, lon2)],
                    weight=2,
                    opacity=0.6,
                    dash_array=None,
                    popup=f"Cost: {data}"
                ).add_to(m)

            # 6) Si piden MST
            if mst_btn:
                # Obtener lista de aristas del MST (Kruskal)
                mst_edges = sim.route_optimizer.kruskal_mst(graph)
                for u, v, w in mst_edges:
                    lat1, lon1 = u.element()["lat"], u.element()["lon"]
                    lat2, lon2 = v.element()["lat"], v.element()["lon"]
                    folium.PolyLine(
                        locations=[(lat1, lon1), (lat2, lon2)],
                        weight=3,
                        opacity=0.4,
                        color="gray",
                        dash_array="5,5",
                        popup=f"MST Edge {u.element()['id']}–{v.element()['id']} (w={w})"
                    ).add_to(m)

            # 7) Si piden ruta
            if calculate_btn:
                # Eligir método
                if algoritmo == "Dijkstra":
                    res = sim.route_manager.find_route_with_recharge(
                        origen, destino, battery_limit=50, method="dijkstra"
                    )
                else:
                    res = sim.route_manager.find_route_with_recharge(
                        origen, destino, battery_limit=50, method="floyd-warshall"
                    )

                if not res:
                    st.error("No se encontró ruta válida con la batería actual y estaciones.")
                else:
                    path, cost, recs = res["path"], res["total_cost"], res["recharge_stops"]
                    # Dibuja ruta en rojo
                    for i in range(len(path)-1):
                        u = graph.get_vertex(path[i])
                        v = graph.get_vertex(path[i+1])
                        folium.PolyLine(
                            locations=[
                                (u.element()["lat"], u.element()["lon"]),
                                (v.element()["lat"], v.element()["lon"])
                            ],
                            weight=4,
                            color="red",
                            popup=f"{path[i]}→{path[i+1]}"
                        ).add_to(m)
                    # Informe de vuelo
                    st.markdown(f"*Ruta:* {' → '.join(map(str,path))}")
                    st.markdown(f"*Distancia/Costo total:* {cost}")
                    st.markdown(f"*Paradas recarga:* {recs if recs else 'Ninguna'}")
                    # Guardar resultado en sesión para completar
                    st.session_state.last_route = res

            # 8) Completar entrega
            if complete_btn:
                if "last_route" not in st.session_state:
                    st.error("Primero calcula una ruta válida antes de crear la orden.")
                else:
                    lr = st.session_state.last_route
                    oid = sim.create_order_from_route(origen, destino, lr)
                    st.success(f"Orden {oid} creada: {origen} → {destino}")

            # 9) Renderiza el mapa en Streamlit
            st_folium(m, width=800, height=600)

        # ------------------------
       
    # PESTAÑA 3: Clients & Orders
    
    # ------------------------
    with p3:
        st.subheader("📑 Clientes y Órdenes")

        if "sim" not in st.session_state:
            st.info("Ejecuta primero la simulación en la pestaña 'Run Simulation'.")
        else:
            sim = st.session_state.sim

            # Lista de clientes (vértices que son clientes)
            st.markdown("### 👤 Lista de Clientes")
            clientes_data = []
            for v in sim.graph.vertices():
                if v.is_client:
                    vid = v.element()["id"]
                    total_ordenes = sum(1 for o in sim.orders.values() if o["dest"] == vid)
                    clientes_data.append({
                        "Cliente ID": vid,
                        "Nombre": f"Cliente {vid}",
                        "Tipo": "cliente",
                        "Total de Órdenes": total_ordenes
                    })
            st.dataframe(clientes_data, use_container_width=True)

            # Lista de órdenes registradas
            st.markdown("### 📦 Lista de Órdenes")
            ordenes_data = []
            for oid, orden in sim.orders.items():
                ordenes_data.append({
                    "ID": oid,
                    "Cliente ID": orden["dest"],
                    "Origen": orden["origin"],
                    "Destino": orden["dest"],
                    "Estado": orden.get("status", "Desconocido"),
                    "Prioridad": orden.get("priority", "Normal"),
                    "Costo Total": orden["cost"]
                })
            st.dataframe(ordenes_data, use_container_width=True)

    with p4:
        st.subheader("📈 Análisis de Rutas")

        # Verificar que la simulación se haya ejecutado
        if 'sim' not in st.session_state:
            st.warning("Debes ejecutar la simulación y procesar órdenes antes de ver el análisis de rutas.")
        else:
            sim = st.session_state.sim
            rt = st.session_state.sim.route_tracker
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

                def compute_tree_positions(node, x=0, y=0, pos=None, depth_spacing=1.5, x_step=1.0):
                    """
                    Asigna posiciones (x,y) a cada nodo basado en recorrido in-order.
                    - depth_spacing controla la separación vertical entre niveles.
                    - x_step controla la separación horizontal mínima.
                    """
                    if pos is None:
                        pos = {}
                    # Recorrer subárbol izquierdo
                    if node.left:
                        compute_tree_positions(node.left, x, y - depth_spacing, pos, depth_spacing, x_step)
                    # Posición del nodo actual: 
                    # Usamos un contador almacenado en pos['_x_counter']
                    xc = pos.get('_x_counter', 0)
                    label = f"{node.key}\\nFreq: {node.value}"
                    pos[label] = (xc * x_step, y)
                    pos['_x_counter'] = xc + 1
                    # Recorrer subárbol derecho
                    if node.right:
                        compute_tree_positions(node.right, x, y - depth_spacing, pos, depth_spacing, x_step)
                    return pos

                # Invocación del conjuro
                # Inicializa contador
                positions = compute_tree_positions(tracker.avl.root, y=0)
                # Elimina la llave interna
                positions.pop('_x_counter', None)

                # 3) Dibujar
                fig, ax = plt.subplots(figsize=(12, 8))
                nx.draw(avl_graph,
                        pos=positions,
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


