import streamlit as st
from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=100000,  # 60000 毫秒 = 60 秒
    key="refresh")
from core import get_vessel_data, refresh_saved_route
from storage import load_config, save_config, init_ship, touch
from streamlit_sortables import sort_items
import json

st.set_page_config(page_title="船舶航線系統   禎❤️翰", layout="wide")

st.title("🚢 船舶航線管理系統")

# session state（關鍵）
# =========================
if "vessel_selected" not in st.session_state:
    st.session_state.vessel_selected = False

if "vessel_code" not in st.session_state:
    st.session_state.vessel_code = None
# =========================
# 記憶設定
config = load_config()
routes_all = config.get("my_routes", [])


# =========================
# 船舶清單
# =========================
ships = {
    "W333": "晴春輪 WAN HAI 333",
    "YCPT": "川明輪 YM CAPACITY",
    "YCST": "永明輪 YM CONSTANCY",
    "YCRT": "好明輪 YM CERTAINTY",
    "YCNU": "存明輪 YM CONTINUITY",
    "YCNL": "百明輪 YM  CENTENNIAL",
    "YCPR": "長明輪 YM COOPERATION",
    "YCNT": "洋明輪 YM CONTINENT",
    "YCDL": "聚明輪 YM CREDENTIAL",
    "YCLI": "譽明輪 YM CREDIBILITY"
}

label_to_code = {f"{name} ({code})": code for code, name in ships.items()}

# 🚢 1. 先選船（未進入系統前）
# =========================================================
if not st.session_state.vessel_selected:

    st.subheader("🚢 進入航線系統")

    # ✅ 一定要選船
    selected_label = st.selectbox(
        "選擇船舶",
        list(label_to_code.keys())
    )

    if st.button("進入航線系統"):

        st.session_state.vessel_code = label_to_code[selected_label]
        st.session_state.vessel_selected = True

        st.rerun()

     # 🟡 已儲存航線 PREVIEW（新增）
    # =========================
    st.divider()
    st.subheader("📦 所有已儲存航線（完整資料）")

    if not routes_all:
        st.info("尚未有任何航線")
        st.stop()

    for i, r in enumerate(routes_all):

        st.markdown(f"## 🚢 {r['vessel']} - {ships.get(r['vessel'], r['vessel'])}")

        for p in r["routes"]:

            with st.container(border=True):

                st.markdown(f"### {p.get('seq')} - {p.get('portName')}")

                st.write("⛵ Arrival:", p.get("arrivalDate"), f"[{p.get('arrivalStatus')}]")
                st.write("⚓ Berth:", p.get("berthDate"), f"[{p.get('berthStatus')}]")
                st.write("🚀 Departure:", p.get("departureDate"), f"[{p.get('departureStatus')}]")

                if p.get("lastPosition"):
                    st.success("⭐ CURRENT POSITION")

        st.divider()
   

    st.stop()

# =========================================================
# 🚢 2. 進入主系統
# =========================================================
selected_label = st.selectbox(
    "🚢 選擇船舶",
    list(label_to_code.keys()),
    index=0 if st.session_state.vessel_code is None else
    list(label_to_code.values()).index(st.session_state.vessel_code)
    if st.session_state.vessel_code in label_to_code.values() else 0
)

vessel_code = label_to_code[selected_label]
st.session_state.vessel_code = vessel_code

st.markdown(f"### 🚢 {ships[vessel_code]}")


# =========================
# API
# =========================
data = get_vessel_data(vessel_code)
route = data["route"]

st.write("航線:", data["lane"])
st.write("狀態:", data["status"])

if not route:
    st.warning("⚠️ 無航線資料")
    st.stop()

# =========================
# FILTER（進階功能）
# =========================
col1, col2 = st.columns(2)

with col1:
    show_actual = st.checkbox("只看 Actual", value=False)

with col2:
    show_planned = st.checkbox("只看 Estimated", value=False)



# =========================
# 航段選擇（UI升級版）
# =========================
st.subheader("📍 航線列表（可勾選）")

selected = []

for p in route:

    arrival_status = p.get("arrivalStatus", "")

    # filter
    if show_actual and arrival_status != "Actual":
        continue

    if show_planned and arrival_status != "Estimated":
        continue

    # 是否為目前位置
    is_current = p.get("lastPosition", False)

    # UI卡片
    with st.container(border=True):

        title = f"{p.get('seq')} - {p.get('portName')}"
        if is_current:
            title += " ⭐ CURRENT"

        st.markdown(f"### {title}")

        st.write("⛵ Arrival:", p.get("arrivalDate"), f"[{arrival_status}]")
        st.write("⚓ Berth:", p.get("berthDate"), f"[{p.get('berthStatus')}]")
        st.write("🚀 Departure:", p.get("departureDate"), f"[{p.get('departureStatus')}]")

        checked = st.checkbox("加入航線", key=f"{vessel_code}_{p.get('seq')}")

        if checked:
            selected.append(p)

# =========================
# 航線名稱
# =========================
st.divider()
route_name = st.text_input("航線名稱", "My Route")

# =========================
# 儲存
# =========================
if st.button("💾 儲存航線"):

    if not selected:
        st.error("請選擇航段")
        st.stop()

    config["my_routes"].append({
    "vessel": vessel_code,
    "vessel_name": ships[vessel_code],
    "name": route_name,
    "routes": selected
    })
    
    save_config(config)

    st.success("已儲存（已永久保存）")

# =========================
# 已儲存航線（進階顯示）
# =========================
st.divider()
st.subheader("📦 已儲存航線（完整資訊）")

config = load_config()

routes = config.get("my_routes", [])

updated_routes = []

for r in routes:
    refreshed = refresh_saved_route(r["vessel"], r["routes"])

    updated_routes.append({
        **r,
        "routes": refreshed
    })

config["my_routes"] = updated_routes
save_config(config)


# =========================
# 🚢 顯示區
# =========================
for i, r in enumerate(updated_routes):

    with st.container(border=True):

        st.markdown(f"## 🚢 {r['vessel']} - {ships.get(r['vessel'])}")

        for p in r["routes"]:

            with st.container(border=True):

                st.markdown(f"### {p.get('seq')} - {p.get('portName')}")

                st.write("🛬 Arrival:", p.get("arrivalDate"), f"[{p.get('arrivalStatus')}]")
                st.write("⚓ Berth:", p.get("berthDate"), f"[{p.get('berthStatus')}]")
                st.write("🚢 Departure:", p.get("departureDate"), f"[{p.get('departureStatus')}]")

                if p.get("lastPosition"):
                    st.success("⭐ CURRENT POSITION")

        # =========================
        # 操作（這裡才會真的生效）
        # =========================
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🗑 刪除", key=f"del_{i}"):

                config["my_routes"].pop(i)
                save_config(config)
                st.rerun()

        with col2:
            if i > 0 and st.button("⬆ 上移", key=f"up_{i}"):

                config["my_routes"][i], config["my_routes"][i-1] = \
                    config["my_routes"][i-1], config["my_routes"][i]

                save_config(config)
                st.rerun()

        with col3:
            if i < len(config["my_routes"]) - 1 and st.button("⬇ 下移", key=f"down_{i}"):

                config["my_routes"][i], config["my_routes"][i+1] = \
                    config["my_routes"][i+1], config["my_routes"][i]

                save_config(config)
                st.rerun()
# =========================
# Debug
# =========================
with st.expander("🔧 Debug JSON"):
    st.json(data)