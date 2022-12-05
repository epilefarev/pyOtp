from source.otp import isochrone
import os

dir = os.getcwd()
output_dir = os.path.join(dir, "output")
tmp_dir = os.path.join(dir, "tmp")
input_dir = os.path.join(dir, "input")

data_isocrone_query_ex = {
    'toPlace': '53.3627432, -2.2729342',
    'fromPlace': '53.3627432, -2.2729342',
    'arriveBy': 'TRUE',
    'mode': 'WALK,TRANSIT',
    'date': '04-28-2020',
    'time': '08:00am',
    'maxWalkDistance': 1600,
    'walkReluctance': 5,
    'minTransferTime': 600,
    'cutoffSec': [900, 1800, 2700, 3600, 4500, 5400],
}

data_isocrone_query_coquimbo = {
    'toPlace': '-29.9263098,-71.2745143',
    'fromPlace': '-29.9263098,-71.2745143',
    'arriveBy': 'TRUE',
    'mode': 'CAR',#WALK, BICYCLE, CAR,TRANSIT, BUS, RAIL, TRAM, SUBWAY, (WALK, TRANSIT) sin parentesis la ultima
    'date': '04-28-2020',
    'time': '08:00am',
    'maxWalkDistance': 1600,
    'walkReluctance': 5,
    'minTransferTime': 600,
    'cutoffSec': [60, 120, 180, 240, 300, 360],
}
router_id = "coquimbo"

isochrone.run(data_isocrone_query_coquimbo, router_id, output_dir)


# data_planner_coquimbo = {
#     'toPlace': '-29.9644126,-71.336642',
#     'fromPlace': '-29.9263098,-71.2745143',
#     'arriveBy': 'TRUE',
#     'mode': 'TRANSIT,WALK',#WALK, BICYCLE, CAR,TRANSIT, BUS, RAIL, TRAM, SUBWAY
#     'date': '04-28-2020',
#     'detail': 'TRUE',
#     'time': '12:00am',
#     'maxWalkDistance': 1600,
#     'walkReluctance': 5
# }
#
# for i in range(1000000):
#     print(i)
#     planner.run(data_planner_coquimbo, router_id, output_dir)
