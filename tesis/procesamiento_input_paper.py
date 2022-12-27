import os
from collections import defaultdict

import pandas as pd
import utm
import logging

enlace_input_tesis = "G:\Mi unidad\descarga_chrome\paper_tesis"

# directorio = r"C:\Users\fvera\PycharmProjects\pyOtp"
directorio = r"D:\Pycharm free\pythonOtp"


def read_input() -> pd.DataFrame:
    logging.info("Leyendo input")
    df = pd.read_csv(os.path.join(enlace_input_tesis, "datos_jacque.csv"))
    logging.info(list(df.columns))
    logging.info(df.describe())
    logging.info("Filtramos ids None")
    df = df[df['id'] != "-"]
    logging.info(df.describe())
    return df


def read_input_small(chunksize=50000) -> pd.DataFrame:
    if chunksize == -1:
        return read_input()
    logging.info("Leyendo input")
    dfs = pd.read_csv(os.path.join(enlace_input_tesis, "datos_jacque.csv"), chunksize=chunksize)
    for df in dfs:
        logging.info(list(df.columns))
        logging.info(df.describe())
        logging.info("Filtramos ids None")
        df = df[df['id'] != "-"]
        logging.info(df.describe())
        return df


def contar_observaciones_id(df):
    logging.info("Contando ids")
    id_counts = df['id'].value_counts().tolist()
    return id_counts


def read_consolidado_parada():
    logging.info("LEyendo consolidado de paradas")
    df = pd.read_csv(
        os.path.join(
            os.path.join(directorio, 'input', 'dtpm2016', "2016-04-30_consolidado_paradas.csv")), sep=";")
    logging.info(df.columns)
    dic_nombre_xy = defaultdict(None)
    xs, ys, nombres = list(df['x']), list(df['y']), list(df['Código paradero TS'])
    paradero_sin_coordenadas = []
    for i in range(len(xs)):
        nombre, x, y = nombres[i], xs[i], ys[i]

        try:
            y, x = utm.to_latlon(x, y, 19, "H")
            dic_nombre_xy[nombre] = (float(x), float(y))
        except Exception as e:
            if (e, nombre) not in paradero_sin_coordenadas:
                paradero_sin_coordenadas.append((e, nombre))
            continue
    for e, nombre in paradero_sin_coordenadas:
        logging.error("{} {} {}".format(e, " No se pudo obtener coordenada paradero ", nombre))

    return df, dic_nombre_xy


def read_consolidado_parada_metro():
    logging.info("Leyendo coordenadas paraderos de metro")
    df = pd.read_csv(
        os.path.join(
            os.path.join(directorio, 'input', 'metro', "stops.txt")), sep=",")
    logging.info(df.columns)
    dic_nombre_xy = defaultdict(None)
    xs, ys, nombres = list(df['stop_lon']), list(df['stop_lat']), list(df['stop_name'])
    paradero_sin_coordenadas = []
    for i in range(len(xs)):
        nombre, x, y = nombres[i], xs[i], ys[i]
        nombre = nombre.upper().replace("Ñ", "N").replace("Á", "A").replace("É", "E").replace("Í", "I").replace("Ó",
                                                                                                                "O").replace(
            "Ú", "U").replace(" (L3-L1)", "").replace(" (L1-L5)", "")
        try:
            dic_nombre_xy[nombre] = (float(x), float(y))
        except Exception as e:
            if (e, nombre) not in paradero_sin_coordenadas:
                paradero_sin_coordenadas.append((e, nombre))
            continue
    for e, nombre in paradero_sin_coordenadas:
        logging.error("{} {} {}".format(e, " No se pudo obtener coordenada paradero metro ", nombre))
    return df, dic_nombre_xy


def join_x_y_paradero_subida_bajada(viajes, dic_paradas, dic_paradas_metro):
    """
    returna tabla de viajes con coordenadas de paradero de subida y bajada, omite aquellos datos que no tienen coordenadas
    :param viajes:
    :param dic_paradas:
    :param dic_paradas_metro:
    :return:
    """
    l_ps = list(viajes['paraderosubida'])
    l_pb = list(viajes['paraderobajada'])
    oxs, oys, oxb, oyb = [], [], [], []
    paraderos_not_match = []
    for i in range(len(viajes)):
        ps = l_ps[i]
        pb = l_pb[i]
        xs, ys, xb, yb = None, None, None, None
        try:
            xs, ys = dic_paradas[ps]
        except Exception as e:
            try:
                xs, ys = dic_paradas_metro[ps]
            except Exception as e:
                paraderos_not_match.append(ps)
        try:
            xb, yb = dic_paradas[pb]
        except Exception as e:
            try:
                xb, yb = dic_paradas_metro[pb]
            except Exception as e:
                paraderos_not_match.append(pb)
        oxs.append(xs)
        oys.append(ys)
        oxb.append(xb)
        oyb.append(yb)
    paraderos_not_match = list(set(paraderos_not_match))
    logging.error("Paraderos no reconocidos de tabla viajes")
    logging.error(paraderos_not_match)
    viajes["xs"] = oxs
    viajes["ys"] = oys
    viajes["xb"] = oxb
    viajes["yb"] = oyb
    viajes = viajes[(viajes['xs'].notna()) & (viajes['ys'].notna()) & (viajes['xb'].notna()) & (viajes['yb'].notna())]
    logging.info("{} {}".format("Numero de viajes con paradero de subida y bajada con coordenadas ", len(viajes)))
    return viajes


def get_viajes_xy_paradas_subidas_bajadas(chunksize=-1) -> pd.DataFrame:
    """
    retorna tabla de viajes con coordenadas de paradero de subida y bajada, omite aquellos datos que no tienen coordenadas
    :param chunksize:
    :return:
    """
    # leemos datos de jacque
    viajes = read_input_small(chunksize=chunksize)
    # leemos consolidado de paradas
    paradas, dic_paradas = read_consolidado_parada()
    # leemos consolidado de parada de metro
    paradas_metro, dic_paradas_metro = read_consolidado_parada_metro()
    # agregamos x,y a paradero de subida y bajada
    viajes = join_x_y_paradero_subida_bajada(viajes, dic_paradas, dic_paradas_metro)
    return viajes

# graficar OD
## ¿buffers?
## click on O or D and intensify color OD PAIR
# graficar viajes
#
