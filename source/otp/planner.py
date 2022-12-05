import json
import os
import urllib.request

from source.otp.build_query import query_str


# documentation parameters: http://dev.opentripplanner.org/apidoc/1.4.0/resource_PlannerResource.html
def download_url(url, output_dir):
    with urllib.request.urlopen(url) as dl_file:
        with open(os.path.join(output_dir, "trip_planner.json"), 'wb') as out_file:
            json_obj = json.loads(dl_file.read())
            return json_obj


def run(data_query, router_id, output_dir):
    myurl = 'http://localhost:8080/otp/routers/{}/plan?{}'.format(router_id, query_str(data_query))
    return download_url(myurl, output_dir)
