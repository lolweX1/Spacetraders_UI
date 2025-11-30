import requests as rq
from AccessAPI import *
import GlobalVariableAccess as gva
import re
from Prompts import *
from Authorize import *
from SystemCanvas import *
from Automation import *
from PromptBreakdown import *
# from PyQt6.QtCore import QTimer, Qt
# from PyQt6.QtWidgets import (QApplication, QWidget, QMainWindow, QPushButton, 
#                              QVBoxLayout, QLabel, QPushButton, QHBoxLayout, 
#                              QSizePolicy, QTabWidget, QLineEdit)
# from LoginWindow import *
# from Canvas import *
# from Window import *

# app = QApplication([])

# def init():
#     data = accessAgent(gva.current_auth_token)

# verify agent
# login = Login()
# if login.exec():
#     init()
#     window = MainWindow()
#     window.show()

# app.exec()

version = "0.401 beta"

commands_help = {
    "nav": "go into ship navigation mode",
    "engage": "actions that can be done while docked",
    "cmdqt": "exit the UI",
    "contract": "access contract functions",
    "subfunctions": "use \"-\" to call multiple subfunctions at once and use \"--\" to put in parameters for each subfunction\nex: nav -navigate --[name of destination]",
    "fetch": "call fetch -url to return the data from the url",
    "get": "fetches the ship's data, call get -attribute1 -attribute2... in order to get specific attribute(s). If you want all the data, just don't put in any arguments and call 'get'",
    "create": "create a window for give object",
    "nearby": "get nearby waypoints",
    "chart": "chart the current waypoint"
}
commands = ["nav", "engage", "contract", "create", "chart", "cmdqt", "help"]

if __name__ == "__main__":
    print(f"Welcome to Lolwe's UI for Space Trader API\nversion {version}\nTo find functions, please use command \"help\"")

    # Intialize all necessary data
    try:
        data = rq.get("https://api.spacetraders.io/v2/my/ships", headers = {"Authorization": "Bearer " + gva.current_auth_token})
        data = data.json()
        gva.system = data["data"][0]["nav"]["systemSymbol"] # CHANGE, have the ability to select different ships
        gva.ship = data["data"][0]["symbol"] # CHANGE
        gva.ship_data = data["data"][0] # CHANGE
        print("data retrieval successful")
    except:
        print("Unable to fetch agent data")

    # obtain all waypoints within system to make "create" faster
    fetch_waypoints()

    # begin the prompt process
    cmd = input("command> ")
    cmd_skip = False

    # prompt process
    while (cmd != "cmdqt"):
        cmd = determine_prompt(cmd)
        print(cmd)
        if (not cmd_skip):
            cmd = input("command> ")