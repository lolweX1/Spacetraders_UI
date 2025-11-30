import requests as rq
from AccessAPI import *
import GlobalVariableAccess as gva
import re
from Prompts import *
from Authorize import *
from SystemCanvas import *
from PromptBreakdown import *

def withinCompletition(**kwargs):
    pass

def navigate_to_closest_waypoint(**kwargs):
    waypoints = calc_nearby_waypoints(str(kwargs["dist"]))
    del waypoints["closest"]
    print(waypoints)
    origin = gva.ship_data["nav"]["route"]["origin"]["symbol"]
    min = None
    for i in waypoints:
        if withinCompletition(waypoint=i) and (i != origin and (min is None or waypoints[i] < waypoints[min])):
            min = i
    determine_prompt("nav -orbit")
    print(min + ": " + str(waypoints[min]))