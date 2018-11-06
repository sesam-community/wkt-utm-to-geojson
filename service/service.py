import json
import logging
import os

import utm
from flask import Flask, Response, request
from shapely.geometry import LineString
from shapely.wkt import loads
from shapely_geojson import dumps

app = Flask(__name__)

logger = logging.getLogger('service')

source_property = os.environ.get("SOURCE_PROPERTY", "wkt")
target_property = os.environ.get("TARGET_PROPERTY", "geojson")
zone_number = int(os.environ.get("ZONE_NUMBER", "33"))
northern = bool(os.environ.get("NORTHERN", "true"))


def utm_to_latlon(easting, northing):
    (lat, lon) = utm.to_latlon(easting, northing, zone_number=zone_number, northern=northern)
    return [lon, lat]


def transform(entity):
    wkt_3d = entity.get(source_property)
    if wkt_3d:
        try:
            utm_3d = loads(wkt_3d)
            latlon_2d = LineString([utm_to_latlon(xy[0], xy[1]) for xy in list(utm_3d.coords)])
            entity[target_property] = json.loads(dumps(latlon_2d))
        except utm.OutOfRangeError as e:
            logger.warning("Failed to convert entity '%s': %s", entity.get("_id"), e)
    return entity


@app.route('/transform', methods=["POST"])
def post():
    entities = request.json
    return Response(json.dumps([transform(e) for e in entities]), mimetype='application/json', )


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
