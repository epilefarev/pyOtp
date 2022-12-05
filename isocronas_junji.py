from source.otp import isochrone
import os
import csv

dir = os.getcwd()
output_dir = os.path.join(dir, "output")
tmp_dir = os.path.join(dir, "tmp")
input_dir = os.path.join(dir, "input")


class Jardin:
    def __init__(self, keys, **kwargs):
        allowed_keys = list(set(
            keys + ['\ufeffCODIGO', 'NOM_ESTABLEC', 'COD_NOM', 'COD_REGION', 'DESC_REGION', 'COD_PROV', 'DESC_PROV',
                    'COD_COMUN', 'DESC_COMUNA', 'AREA', 'LONGITUD', 'LATITUD']))
        self.__dict__.update((key, False) for key in allowed_keys)
        self.__dict__.update((key, value) for key, value in kwargs.items() if key in allowed_keys)


def read_data_junji():
    output = []
    with open(os.path.join('input/JUNJI', 'junji_coquimbo.csv'), encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f, delimiter=';')

        for row in reader:
            output.append(Jardin(keys=list(row.keys()), **row))
    return output


jardines = read_data_junji()

for jardin in jardines:
    if jardin.AREA == "URBANO":
        lat, lon = jardin.LATITUD, jardin.LONGITUD
        modo = 'WALK'  # WALK, BICYCLE, CAR,TRANSIT, BUS, RAIL, TRAM, SUBWAY, (WALK, TRANSIT) sin parentesis la ultima
        data_isocrone_query_coquimbo = {
            'toPlace': '{},{}'.format(lat, lon),
            'fromPlace': '{},{}'.format(lat, lon),
            'arriveBy': 'TRUE',
            'mode': modo,
            'date': '04-28-2020',
            'time': '08:00am',
            'maxWalkDistance': 1600,
            'walkReluctance': 5,
            'minTransferTime': 600,
            'cutoffSec': [300, 600, 900],
        }
        router_id = "coquimbo"
        carpeta = "{}\\{}".format(router_id, modo)
        os.makedirs(os.path.join(output_dir, carpeta), exist_ok=True)
        print(jardin.COD_NOM)
        isochrone.run(data_isocrone_query_coquimbo, router_id, output_dir,
                      name_file='{}/{}.json'.format(carpeta, jardin.COD_NOM))
