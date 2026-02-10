import streamlit as st
import pandas as pd

tab1, tab2, tab3 = st.tabs(["Pestaña 1", "Pestaña 2", "Pestaña 3"])

with tab1:
    st.write("Contenido de la pestaña 1")

with tab2:
    st.write("Contenido de la pestaña 2")

with tab3:
    st.write("Contenido de la pestaña 3")
