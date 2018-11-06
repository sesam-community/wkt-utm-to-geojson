# Convert 3D WKT UTM LINESTRING to geojson

Example system config:
```
{
  "_id": "my-geojson-transformer",
  "type": "system:microservice",
  "docker": {
    "environment": {
      "SOURCE_PROPERTY": "wkt",
      "TARGET_PROPERTY": "geojson",
      "ZONE_NUMBER": "33",
      "NORTHERN": "true"
    },
    "image": "sesamcommunity/wkt-utm-to-geojson",
    "port": 5000
  }
}
```