
import streamlit as st
import matplotlib.pyplot as plt
import networkx as nx
from visual.networkx_adapter import NetworkXAdapter
from sim.simulation import Simulation # Asumiendo que Simulation maneja la lógica de ruteo
from model.graph import Graph # Asumiendo que Graph se encarga de la estructura del grafo

def explore_network_tab(simulation_instance: Simulation):
    st.title("Explore Network")

    if simulation_instance is None or simulation_instance.graph is None:
        st.warning("Please start a simulation first in the 'Run Simulation' tab.")
        return

    graph_adapter = NetworkXAdapter(simulation_instance.graph)
    pos = nx.spring_layout(graph_adapter.nx_graph) # O puedes usar otra disposición si prefieres

    # Mapeo de roles a colores para la visualización
    node_colors = []
    node_labels = {}
    for node_id, node_data in simulation_instance.graph.vertices.items():
        if node_data.role == "almacenamiento":
            node_colors.append('blue')
        elif node_data.role == "recarga":
            node_colors.append('green')
        elif node_data.role == "cliente":
            node_colors.append('red')
        else:
            node_colors.append('gray') # Default color for unknown roles
        node_labels[node_id] = f"{node_id} ({node_data.role[0].upper()})" # Add initial for clarity

    fig, ax = plt.subplots(figsize=(10, 8))
    nx.draw_networkx_nodes(graph_adapter.nx_graph, pos, node_color=node_colors, ax=ax)
    nx.draw_networkx_edges(graph_adapter.nx_graph, pos, ax=ax, alpha=0.5)
    nx.draw_networkx_labels(graph_adapter.nx_graph, pos, labels=node_labels, font_size=8, ax=ax)
    plt.title("Network of Drones")
    st.pyplot(fig)

    st.subheader("Calculate Route")

    # Selectbox para nodo origen
    source_node_id = st.selectbox("Select Origin Node", options=list(simulation_instance.graph.vertices.keys()), key="origin_node_select")
    # Selectbox para nodo destino
    destination_node_id = st.selectbox("Select Destination Node", options=list(simulation_instance.graph.vertices.keys()), key="destination_node_select")

    if st.button("Calculate Route", key="calculate_route_button"):
        if source_node_id and destination_node_id:
            # Validación de existencia de nodos
            if source_node_id not in simulation_instance.graph.vertices or destination_node_id not in simulation_instance.graph.vertices:
                st.error("One or both selected nodes do not exist in the graph. Please select existing nodes.")
                return

            # Llama a la función de cálculo de ruta en la clase Simulation
            # Esta función debe manejar la lógica de la batería y la recarga.
            path_info = simulation_instance.find_route_with_recharge(source_node_id, destination_node_id, max_autonomy=50)

            if path_info and path_info["path"]:
                path_str = " → ".join(path_info["path"])
                st.text_area("Route Found:", f"Path: {path_str}\nCost: {path_info['cost']}", height=100)

                # Dibuja la ruta en rojo
                path_edges = [(path_info["path"][i], path_info["path"][i+1]) for i in range(len(path_info["path"])-1)]

                fig_route, ax_route = plt.subplots(figsize=(10, 8))
                nx.draw_networkx_nodes(graph_adapter.nx_graph, pos, node_color=node_colors, ax=ax_route)
                nx.draw_networkx_edges(graph_adapter.nx_graph, pos, ax=ax_route, alpha=0.5)
                nx.draw_networkx_edges(graph_adapter.nx_graph, pos, edgelist=path_edges, edge_color='red', width=2, ax=ax_route)
                nx.draw_networkx_labels(graph_adapter.nx_graph, pos, labels=node_labels, font_size=8, ax=ax_route)
                plt.title(f"Route from {source_node_id} to {destination_node_id}")
                st.pyplot(fig_route)

                if st.button("Complete Delivery and Create Order", key="complete_delivery_button"):
                    # Aquí puedes agregar la lógica para completar la entrega y crear la orden.
                    # Esto probablemente implicaría llamar a un método en la instancia de `simulation`.
                    order_id = simulation_instance.create_order_from_route(source_node_id, destination_node_id, path_info)
                    st.success(f"Order {order_id} created and delivery completed!")
            else:
                st.warning("No route found between the selected nodes with the current battery limits.")

    # Leyenda de colores (puedes hacerla más elaborada si lo deseas)
    st.sidebar.markdown("### Node Types Legend")
    st.sidebar.markdown("<span style='color:blue;'>🔵</span> Almacenamiento", unsafe_allow_html=True)
    st.sidebar.markdown("<span style='color:green;'>🟢</span> Recarga", unsafe_allow_html=True)
    st.sidebar.markdown("<span style='color:red;'>🔴</span> Cliente", unsafe_allow_html=True)