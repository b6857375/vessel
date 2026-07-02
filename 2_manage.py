import streamlit as st
from streamlit_sortables import sort_items
from storage import load, save

st.title("⚙️ 航線管理 + 拖曳排序")

config = load()

for ship, data in config.items():

    st.subheader(ship)

    routes = data["routes"]

    # 變成可拖曳清單
    items = [r["name"] for r in routes]

    new_order = sort_items(items)

    # 重新排序
    ordered_routes = []

    for name in new_order:
        for r in routes:
            if r["name"] == name:
                ordered_routes.append(r)

    config[ship]["routes"] = ordered_routes

    if st.button(f"💾 儲存 {ship}"):
        save(config)
        st.success("已更新排序")