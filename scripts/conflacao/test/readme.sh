exit 1

# @see https://github.com/mapsme/osm_conflate
# conflate <profile.py> -o result.osm

conflate profile_random.py -o out/result.osm
conflate --output out/result.osm random.py.py
conflate \
  --osm=out/overpass-result.osm \
  --changes=out/preview-changes.geojson \
  --output=out/result.osm \
  velobike.py