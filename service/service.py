import json
import logging
import os

import utm
from flask import Flask, Response, request
from shapely.geometry import LineString
from shapely.geometry import Point
from shapely.wkt import loads
from shapely_geojson import dumps

app = Flask(__name__)

logger = logging.getLogger('service')

source_property = os.environ.get("SOURCE_PROPERTY", "wkt")
target_property = os.environ.get("TARGET_PROPERTY", "geojson")
zone_number = int(os.environ.get("ZONE_NUMBER", "33"))
northern = json.loads(os.environ.get("NORTHERN", "true").lower())
strict = json.loads(os.environ.get("STRICT_UTM_TO_LATLON", "false").lower())

path = source_property.split(".")


def utm_to_latlon(easting, northing):
    (lat, lon) = utm.to_latlon(easting, northing, zone_number=zone_number, northern=northern, strict=strict)
    return [lon, lat]


def resolve(entity):
    value = entity
    for p in path:
        value = value.get(p)
        if value is None:
            return
    return value


def transform(entity):
    wkt_3d = resolve(entity)
    if wkt_3d:
        try:
            entity[target_property] = convert(wkt_3d)
        except Exception as e:
            logger.warning("Failed to convert entity '%s': %s", entity.get("_id"), e)
    return entity


def convert(wkt):
    utm = loads(wkt)
    if isinstance(utm, LineString):
        latlon_2d = LineString([utm_to_latlon(xy[0], xy[1]) for xy in list(utm.coords)])
    elif isinstance(utm, Point):
        latlon_2d = Point([utm_to_latlon(xy[0], xy[1]) for xy in list(utm.coords)][0])
    else:
        raise Exception("unknown geometry: %s" % type(utm))
    return json.loads(dumps(latlon_2d))


@app.route('/transform', methods=["POST"])
def post():
    entities = request.json
    return Response(json.dumps([transform(e) for e in entities]), mimetype='application/json', )


def test(wkt, geojson):
    assert geojson == convert(wkt)


test('POINT Z (254631.55006 6704438.93804 206.62321)', {'type': 'Point', 'coordinates': [10.544572456687401, 60.40159704735351]})
test('POINT Z (254631.55006 6704438.93804)', {'type': 'Point', 'coordinates': [10.544572456687401, 60.40159704735351]})
test('LINESTRING Z (82250.94971 6516530.80762 182.79739, 82266.24023 6516542.28027 182.66)', {'type': 'LineString', 'coordinates': [[7.805882285564546, 58.58734116188372], [7.8061221286595295, 58.58745806374288]]})
test('LINESTRING Z (82250.94971 6516530.80762, 82266.24023 6516542.28027)', {'type': 'LineString', 'coordinates': [[7.805882285564546, 58.58734116188372], [7.8061221286595295, 58.58745806374288]]})

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
