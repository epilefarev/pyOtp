from collections import defaultdict
import collections
from procesamiento_input_paper import get_viajes_xy_paradas_subidas_bajadas, read_consolidado_parada, \
    read_consolidado_parada_metro
import pandas as pd
from typing import Tuple
import json

viajes = get_viajes_xy_paradas_subidas_bajadas(1000)
# leemos consolidado de paradas
paradas, dic_paradas = read_consolidado_parada()
# leemos consolidado de parada de metro
paradas_metro, dic_paradas_metro = read_consolidado_parada_metro()


def distancia_puntos_latlon(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    return (((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2) ** 0.5) * 111100


def get_bufferes_paraderos(dic_paradas: collections.defaultdict,
                           dic_parada_metro: collections.defaultdict) -> collections.defaultdict:
    paraderos = list(set(list(dic_paradas.keys()) + list(dic_parada_metro.keys())))
    output = defaultdict(list)
    no_output = defaultdict(list)
    n = 1
    for p1 in paraderos:
        print(n)
        n += 1

        try:
            lon1, lat1 = dic_paradas[p1]
        except Exception:
            try:
                lon1, lat1 = dic_parada_metro[p1]
            except Exception:
                continue
        for p2 in paraderos:
            if p1 == p2:
                no_output[p1].append(p2)
                continue
            elif p2 in output[p1]:
                continue
            elif p2 in no_output[p1]:
                continue
            else:
                try:
                    lon2, lat2 = dic_paradas[p2]
                except Exception:
                    try:
                        lon2, lat2 = dic_parada_metro[p2]
                    except Exception:
                        continue
                d = distancia_puntos_latlon(lat1, lon1, lat2, lon2)
                if d <= 500:
                    output[p1].append(p2)
                    output[p2].append(p1)
                else:
                    no_output[p1].append(p2)
                    no_output[p2].append(p1)

    return output


dic_buffer = get_bufferes_paraderos(dic_paradas, dic_paradas_metro)
a_file = open("buffers.json", "w")
json.dump(dic_buffer, a_file, indent=4)
a_file.close()
