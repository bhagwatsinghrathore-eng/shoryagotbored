import streamlit as st, streamlit.components.v1 as c, urllib.request

st.set_page_config(layout="wide")
st.markdown(
    "<style>.block-container{padding:0!important;max-width:100%!important}"
    "header,footer,#MainMenu{visibility:hidden}"
    "iframe{position:fixed!important;inset:0!important;"
    "width:100vw!important;height:100vh!important;border:none!important}</style>",
    unsafe_allow_html=True,
)
c.html(open("index.html").read(), height=800)

