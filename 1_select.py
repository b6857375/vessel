import streamlit as st
from core import get_vessel
from storage import load, save

st.title("🚢 選擇航線")

ships = ["YCPT"]

ship = st.selectbox("選船", ships)

data = get_vessel(ship)
route = data["latestVesselPosition"]["berthDetail"]

config = load()

if ship not in config:
    config[ship] = {"routes": []}

st.subheader("勾選航線")

selected = []

for p in route:
    if st.checkbox(p["portName"]):
        selected.append(p["portName"])

name = st.text_input("航線名稱")

if st.button("儲存"):
    config[ship]["routes"].append({
        "name": name,
        "ports": selected,
        "order": len(config[ship]["routes"])
    })

    save(config)
    st.success("已儲存")