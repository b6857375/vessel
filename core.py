import requests

def get_vessel_data(vessel_code):

    url = f"https://www.yangming.com/api/VesselTracking/GetVesselStatus?vesselCode={vessel_code}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        return {
            "vessel_name": None,
            "vessel_code": vessel_code,
            "lane": None,
            "voyage": None,
            "status": None,
            "route": [],
            "error": str(e)
        }

    pos = data.get("latestVesselPosition") or {}

    # 🚢 這裡就是你要的完整航線資料
    route = (
        data.get("detailedVesselPosition", {})
        .get("berthDetail", [])
        or []
    )

    return {
        "vessel_name": data.get("vesselName"),
        "vessel_code": data.get("vesselCode"),

        "lane": pos.get("currentLane"),
        "voyage": pos.get("currentComnVoyage"),
        "status": pos.get("status"),

        # ⭐ 完整航線（包含 seq / portName / arrival / departure / lastPosition）
        "route": route
    }

def refresh_saved_route(vessel_code, saved_routes):
    """
    用最新 API 更新已儲存航線（依 seq 對齊）
    """

    data = get_vessel_data(vessel_code)

    latest_map = {
        str(p.get("seq")): p
        for p in data.get("route", [])
    }

    updated_routes = []

    for p in saved_routes:
        seq = str(p.get("seq"))

        if seq in latest_map:
            api = latest_map[seq]

            p["arrivalDate"] = api.get("arrivalDate")
            p["arrivalStatus"] = api.get("arrivalStatus")

            p["berthDate"] = api.get("berthDate")
            p["berthStatus"] = api.get("berthStatus")

            p["departureDate"] = api.get("departureDate")
            p["departureStatus"] = api.get("departureStatus")

            p["lastPosition"] = api.get("lastPosition", False)

        updated_routes.append(p)

    return updated_routes