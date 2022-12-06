import os
from collections import defaultdict
from typing import List, Tuple
import utm

import pandas as pd

enlace_input_tesis = "G:\Mi unidad\descarga_chrome\paper_tesis"
directorio = r"C:\Users\fvera\PycharmProjects\pyOtp"


def read_input() -> pd.DataFrame:
    print("Leyendo input")
    df = pd.read_csv(os.path.join(enlace_input_tesis, "datos_jacque.csv"))
    print(list(df.columns))
    print(df.describe())
    print("Filtramos ids None")
    df = df[df['id'] != "-"]
    print(df.describe())
    return df


def read_input_small() -> pd.DataFrame:
    print("Leyendo input")
    dfs = pd.read_csv(os.path.join(enlace_input_tesis, "datos_jacque.csv"), chunksize=50000)
    for df in dfs:
        print(list(df.columns))
        print(df.describe())
        print("Filtramos ids None")
        df = df[df['id'] != "-"]
        print(df.describe())
        return df


def contar_observaciones_id(df):
    print("Contando ids")
    id_counts = df['id'].value_counts().tolist()
    return id_counts


def read_consolidado_parada():
    df = pd.read_csv(
        os.path.join(
            os.path.join(directorio, 'input', 'dtpm2016', "2016-04-30_consolidado_paradas.csv")), sep=";")
    print(df.columns)
    dic_nombre_xy = defaultdict(None)
    xs, ys, nombres = list(df['x']), list(df['y']), list(df['Código paradero TS'])
    for i in range(len(xs)):
        nombre, x, y = nombres[i], xs[i], ys[i]
        try:
            dic_nombre_xy[nombre] = (float(x), float(y))
        except Exception as e:
            print(e, " No se pudo obtener coordenada paradero ", nombre)
            continue
    return df, dic_nombre_xy


def read_consolidado_parada_metro():
    df = pd.read_csv(
        os.path.join(
            os.path.join(directorio, 'input', 'metro', "stops.txt")), sep=",")
    print(df.columns)
    dic_nombre_xy = defaultdict(None)
    xs, ys, nombres = list(df['stop_lon']), list(df['stop_lat']), list(df['stop_name'])
    for i in range(len(xs)):
        nombre, x, y = nombres[i], xs[i], ys[i]
        nombre = nombre.upper().replace("Ñ", "N").replace("Á", "A").replace("É", "E").replace("Í", "I").replace("Ó", "O").replace("Ú", "U").replace(" (L3-L1)", "").replace(" (L1-L5)", "")
        x, y, _, _ = utm.from_latlon(y, x)
        try:
            dic_nombre_xy[nombre] = (float(x), float(y))
        except Exception as e:
            print(e, " No se pudo obtener coordenada paradero ", nombre)
            continue
    return df, dic_nombre_xy


def join_x_y_paradero_subida_bajada(viajes, dic_paradas, dic_paradas_metro):
    l_ps = list(viajes['paraderosubida'])
    l_pb = list(viajes['paraderobajada'])
    paraderos_not_match = []
    for i in range(len(viajes)):
        ps = l_ps[i]
        pb = l_pb[i]
        try:
            xs, ys = dic_paradas[ps]
        except Exception as e:
            try:
                xs, ys = dic_paradas_metro[ps]
            except Exception as e:
                paraderos_not_match.append(ps)
                continue
        try:
            xb, yb = dic_paradas[pb]
        except Exception as e:
            try:
                xb, yb = dic_paradas_metro[pb]
            except Exception as e:
                paraderos_not_match.append(pb)
                continue
    paraderos_not_match = list(set(paraderos_not_match))
    print(paraderos_not_match)


viajes = read_input_small()
paradas, dic_paradas = read_consolidado_parada()
paradas_metro, dic_paradas_metro = read_consolidado_parada_metro()
id_counts = contar_observaciones_id(viajes)

print(viajes['paraderosubida'])
print(paradas['Código paradero TS'])

join_x_y_paradero_subida_bajada(viajes, dic_paradas, dic_paradas_metro)


# graficar OD
    # ¿buffers?
# graficar viajes
    #
