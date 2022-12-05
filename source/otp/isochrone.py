import os
import urllib.request
# import zipfile
# from json import dumps
#
# import shapefile

from source.otp.build_query import query_str

# documentacion: http://dev.opentripplanner.org/apidoc/1.4.0/resource_LIsochrone.html

def download_url_iso(url, output_dir, name_file):
    with urllib.request.urlopen(url) as dl_file:
        with open(os.path.join(output_dir, name_file), 'wb') as out_file:
            # print(dl_file.read())
            out_file.write(dl_file.read())


def run(data_query, router_id, output_dir, name_file='iso.json'):
    myurl = 'http://localhost:8080/otp/routers/{}/isochrone?{}'.format(router_id, query_str(data_query))
    download_url_iso(myurl, output_dir, name_file)
    print("archivo isocrona generado")

    # password = None
    #
    # # open and extract all files in the zip
    # z = zipfile.ZipFile("iso.zip", "r")
    # try:
    #     z.extractall(pwd=password)
    # except:
    #     print('Error extraer zip')
    #     pass
    # z.close()

    # read the shapefile
    # reader = shapefile.Reader("null.shp")
    # fields = reader.fields[1:]
    # field_names = [field[0] for field in fields]
    # buffer = []
    # for sr in reader.shapeRecords():
    #     atr = dict(zip(field_names, sr.record))
    #     geom = sr.shape.__geo_interface__
    #     buffer.append(dict(type="Feature", geometry=geom, properties=atr))
    #
    # # write the GeoJSON file
    # geojson = open(os.path.join(output_dir, "isochrone.json"), "w")
    # geojson.write(dumps({"type": "FeatureCollection", "features": buffer}, indent=2) + "\n")
    # geojson.close()
