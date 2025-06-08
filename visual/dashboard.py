# Dashboard con pestañas en Streamlit
import streamlit as st

def run_dashboard():
    st.set_page_config(page_title='Sistema de Drones')
    st.title('Sistema Logístico Autónomo con Drones')
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        '🔄 Run Simulation',
        '🌍 Explore Network',
        '🌐 Clients & Orders',
        '📋 Route Analytics',
        '📈 General Statistics'])

    with tab1:
        st.write('Parámetros de simulación')

    with tab2:
        st.write('Visualización del grafo y cálculo de rutas')

    with tab3:
        st.write('Clientes y órdenes generadas')

    with tab4:
        st.write('Rutas más utilizadas (AVL)')

    with tab5:
        st.write('Estadísticas generales del sistema')