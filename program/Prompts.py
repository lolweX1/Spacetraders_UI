import requests as rq
from AccessAPI import *
import GlobalVariableAccess as gva
import re
from Prompts import *
from Authorize import *
from SystemCanvas import *

nav_cmd = ["orbit", "navigate", "dock", "status", "exit"]
scan_cmd = ["waypoints", "ships", "systems", "exit"]
engage_cmd = ["extract", "cooldown", "market", "buy", "sell", "exit"]
contract_cmd = ["access", "accept", "negotiate", "fulfill", "completion", "exit"]

def navigate(funcs):
    for cmd in funcs:
        cmd = re.split(r'(?<!-)\-\-(?!-)', cmd.replace(" ", ""))
        if cmd[0] in nav_cmd:
            if cmd[0] == "status":
                print(f"STATUS: {gva.ship_data["nav"]["status"]}")
            elif cmd[0] == "exit":
                return True
            else:
                authorize_ship_nav(cmd[0], cmd[1] if len(cmd) > 1 else None)
                if (cmd[0] == "navigate"):
                    call_generic_action(f"https://api.spacetraders.io/v2/my/ships/{gva.ship}/chart")
        else:
            return False
        update_ship_data()
    return True

def engage(funcs):
    for cmd in funcs:
        cmd = cmd.replace(" ", "").split("--")
        if cmd[0] in engage_cmd:
            if cmd[0] == "cooldown":
                print(f"COOLDOWN: {gva.ship_data["cooldown"]}")
            elif cmd[0] == "buy":
                for i in range(int((len(cmd)-1)/2)):
                    data = authorize_ship_market(f"https://api.spacetraders.io/v2/my/ships/{gva.ship}/purchase", cmd[1+i*2], cmd[2+i*2])
            elif cmd[0] == "sell":
                for i in range(int((len(cmd)-1)/2)):
                    data = authorize_ship_market(f"https://api.spacetraders.io/v2/my/ships/{gva.ship}/sell", cmd[1+i*2], cmd[2+i*2])
            elif cmd[0] == "market":
                data = auth_access(f"https://api.spacetraders.io/v2/systems/{gva.ship_data['nav']['systemSymbol']}/waypoints/{gva.ship_data['nav']['waypointSymbol']}/market")
                print(f"exports: {data["data"]["exports"]}")
                print(f"imports: {data["data"]["imports"]}")
                print(f"exchange:\n {"".join(f"    {i["symbol"]}: {i["description"]}\n" for i in data["data"]["exchange"])}")
                print(f"trading goods:\n {"".join(f"    {i["symbol"]} ({i["type"]}): trade volume-{i["tradeVolume"]}, supply-{i["supply"]}\n       price-{i["purchasePrice"]}, sell value-{i["sellPrice"]}\n" for i in data["data"]["tradeGoods"])}")
            elif cmd[0] == "exit":
                return True
            else:
                authorize_ship_engage(cmd[0])
        else:
            return False
        update_ship_data()
    return True

def contract(funcs):
    print(funcs)
    for cmd in funcs:
        if cmd in contract_cmd:
            if cmd == "access":
                data = auth_access("https://api.spacetraders.io/v2/my/contracts")
                print("".join(
                    f"Contract {contracts}:\n" +
                    "".join(
                        f"    {detail}: {data['data'][contracts][detail]}\n"
                        for detail in data["data"][contracts]
                    )
                    for contracts in range(len(data["data"]))
                ))
            elif cmd == "accept":
                data = auth_access("https://api.spacetraders.io/v2/my/contracts")
                for contracts in data["data"]:
                    auth_access(f"https://api.spacetraders.io/v2/my/contracts/{contracts["id"]}/accept", True)
            elif cmd == "negotiate":
                data = call_generic_action(f"https://api.spacetraders.io/v2/my/ships/{gva.ship}/negotiate/contract")
                print(data)
            elif cmd == "fulfill":
                print("function currently unavailable")
            elif cmd[0] == "exit":
                return True
        else:
            return False
        update_ship_data()
    return True

def create(funcs):
    app = QtWidgets.QApplication([])
    print(funcs)
    if (funcs[0] =="system"):
        window = CanvasWindow()
        window.show()
        systems = {
        "Earth": [100, 150],
        "Mars": [800, 200],
        "Venus": [1200, 900],
        "Jupiter": [300, 1200],
        "Saturn": [1500, 500],
        }
        window.set_points(gva.system_waypoints)
    app.exec()

def calc_nearby_waypoints(funcs):
    dist = int(funcs.replace(" ", ""))
    print(dist)
    curr_ship_pos = [gva.ship_data["nav"]["route"]["destination"]["x"], gva.ship_data["nav"]["route"]["destination"]["y"]]
    retval = {}
    min = ["", 0]
    for i in gva.system_waypoints:
        dist_from = math.sqrt(math.pow((curr_ship_pos[0]-gva.system_waypoints[i][0]), 2) + math.pow((curr_ship_pos[1]-gva.system_waypoints[i][1]), 2))
        if dist_from < dist and dist_from > 0:
            retval[i] = dist_from
            if (min[0] == "" or dist_from < min[1]):
                min[0] = i
                min[1] = dist_from
    retval["closest"] = min
    print(retval)
    return retval