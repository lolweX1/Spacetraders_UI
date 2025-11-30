import requests as rq
from AccessAPI import *
import GlobalVariableAccess as gva
import re
from Prompts import *
import math

def auth_access(li, post = False, bd = None):
    try:
        headers = {"Authorization": f"Bearer {gva.current_auth_token}"}

        if bd is not None:
            headers["Content-Type"] = "application/json"

        if post:
            response = rq.post(li, headers=headers, json=bd)
        else:
            response = rq.get(li, headers=headers)

        data = response.json()

        if "error" in data:
            print(f"Error {data['statusCode']}: {data['error']} - {data['message']}")
            return None

        return data
    except Exception as e:
        print("Unable to fetch data:", e)
        return None

def authorize_ship_engage(op):
    return auth_access(f"https://api.spacetraders.io/v2/my/ships/{gva.ship}/{op}", True)

def authorize_ship_nav(op, loc = None):
    def access(post=True, navi = None):
        try:
            url = f"https://api.spacetraders.io/v2/my/ships/{gva.ship}/{op}"
            headers = {"Authorization": f"Bearer {gva.current_auth_token}"}

            if navi:  # for navigate
                headers["Content-Type"] = "application/json"
                data = {"waypointSymbol": navi}
                response = rq.post(url, headers=headers, json=data)
            else:
                if post:
                    response = rq.post(url, headers=headers)
                else:
                    response = rq.get(url, headers=headers)

            data = response.json()
            if "error" in data:
                print(f"Error {data["error"]["code"]}: {data["error"]["message"]} ")
                return None
            return data
        except Exception as e:
            print("Unable to fetch data:", e)
            return None
    if (loc):
        success = access(True, loc)
    elif (op == "navigate"):
        cmd = input("location> ")
        success = access(True, cmd)
    else: success = access()
    return success

def get_generic_data(url):
    try:
        headers = {"Authorization": f"Bearer {gva.current_auth_token}"}

        response = rq.get(url, headers=headers)

        data = response.json()

        if "error" in data:
            print(f"Error {data['statusCode']}: {data['error']} - {data['message']}")
            return None

        return data
    except Exception as e:
        print("Unable to fetch data:", e)
        return None

def call_generic_action(url):
    try:
        headers = {"Authorization": f"Bearer {gva.current_auth_token}"}

        response = rq.post(url, headers=headers)

        data = response.json()

        if "error" in data:
            print(f"{data}")
            return None

        return data
    except Exception as e:
        print("Unable to fetch data:", e)
        return None

def authorize_ship_market(url, gd, am):
    try:
        headers = {"Authorization": f"Bearer {gva.current_auth_token}"}

        options = {
            "symbol":gd, "units":int(am)
        }
        print(f"{gd}: {am}")

        response = rq.post(url, headers=headers, json=options)
        data = response.json()
        print(data)
        if "error" in data:
            print(f"Error {data["error"]["code"]}: {data["error"]["message"]} ")
            return None
        return data
    except Exception as e:
        print("Unable to fetch data:", e)
        return None

def update_ship_data():
    gva.ship_data = auth_access(f"https://api.spacetraders.io/v2/my/ships/{gva.ship}")["data"]

def fetch_waypoints():
    print(gva.system)
    data = get_generic_data(f"https://api.spacetraders.io/v2/systems/{gva.system}/waypoints?page=1&limit=20")
    print(data)
    for waypoint in data["data"]:
        gva.system_waypoints[waypoint["symbol"]] = [waypoint["x"], waypoint["y"], {"orbitals": waypoint["orbitals"]}]
    pages_max = math.ceil(data["meta"]["total"]/20)
    page = 1
    while page < pages_max:
        page += 1
        data = get_generic_data(f"https://api.spacetraders.io/v2/systems/{gva.system}/waypoints?page={page}&limit=20")
        for waypoint in data["data"]:
            gva.system_waypoints[waypoint["symbol"]] = [waypoint["x"], waypoint["y"]]
