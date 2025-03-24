import streamlit as st


LOGO="src/ff_logo.png"

st.link_button("Ping openzaken", "http://localhost:8080/openzaak", icon=":material/open_in_new:")
st.link_button("Ping openformulieren", "http://localhost:8080/openforms", icon=":material/open_in_new:")
st.logo(LOGO)