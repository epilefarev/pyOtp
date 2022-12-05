import csv
import os

import utm

from source.otp import planner

dir = os.getcwd()
output_dir = os.path.join(dir, "output")
tmp_dir = os.path.join(dir, "tmp")
input_dir = os.path.join(dir, "input")

router_id = "santiago"


class Zone:
    def __init__(self, id_zone, id_comuna, comuna, x, y, lat, lon):
        self.zone_id = id_zone
        self.comuna_id = id_comuna
        self.comuna = comuna
        self.x = x
        self.y = y
        self.lat = lat
        self.lon = lon


origin = []
destination = []

with open('input\\zonificacion_santiago\\centroides_zonas_eod_santiago_2012.csv', encoding='utf-8') as f:
    reader = csv.reader(f, delimiter=',')
    n = 0
    for row in reader:
        if n == 0:
            n += 1
            continue

        zone_id = row[0]
        comuna_id = row[3]
        comuna = row[4]
        x = float(row[5])
        y = float(row[6])
        lat, lon = utm.to_latlon(x, y, 19, 'H')

        origin.append(Zone(zone_id, comuna_id, comuna, x, y, lat, lon))
        destination.append(Zone(zone_id, comuna_id, comuna, x, y, lat, lon))

modos = ['TRANSIT,WALK', 'CAR']

output_data = [
    ("id_consulta", "origen", "destino", "modo", "itinerario", "duration", "walkTime", "transitTime", "waitingTime",
     "walkDistance", "walkLimitExceeded", "transfers")]
# pares OD
n = 0
for zone_o in origin:
    for zone_d in destination:

        for mode in modos:
            data_planner = {
                'toPlace': '{},{}'.format(zone_d.lat, zone_d.lon),
                'fromPlace': '{},{}'.format(zone_o.lat, zone_o.lon),
                'arriveBy': 'TRUE',
                'mode': '{}'.format(mode),  # WALK, BICYCLE, CAR,TRANSIT, BUS, RAIL, TRAM, SUBWAY
                'date': '04-28-2020',
                'time': '03:00pm',
                'maxWalkDistance': 1600,
                'walkReluctance': 5,
                'minTransferTime': 600
            }
            request = planner.run(data_planner, router_id, output_dir)

            n += 1
            print(n)
            if n == 10000:

                with open('output_santiago.csv', 'w', newline='') as file:
                    writer = csv.writer(file)
                    for data in output_data:
                        writer.writerow(data)
                quit()

            duration = None
            walkTime = None
            transitTime = None
            waitingTime = None
            walkDistance = None
            walkLimitExceeded = None
            transfers = None

            if request.get('plan'):
                # print(request['plan'])
                if request['plan'].get('itineraries'):
                    iter = 0
                    for itinerario in request['plan']['itineraries']:
                        duration = itinerario['duration']
                        walkTime = itinerario['walkTime']
                        transitTime = itinerario['transitTime']
                        waitingTime = itinerario['waitingTime']
                        walkDistance = itinerario['walkDistance']
                        walkLimitExceeded = itinerario['walkLimitExceeded']
                        transfers = itinerario['transfers']
                        output_data.append(
                            (
                                n, zone_o.zone_id, zone_d.zone_id, mode, iter, duration, walkTime, transitTime,
                                waitingTime,
                                walkDistance, walkLimitExceeded, transfers))
                        iter += 1

            else:
                output_data.append(
                    (n, zone_o.zone_id, zone_d.zone_id, mode, 0, duration, walkTime, transitTime, waitingTime,
                     walkDistance, walkLimitExceeded, transfers))

