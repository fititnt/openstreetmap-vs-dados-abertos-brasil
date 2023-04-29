[out:xml][timeout:25];
//{{geocodeArea:Rio Grande do Sul}}->.searchArea;
area(id:3600242620)->.searchArea;
(
  //nwr["ref:CNES"](area.searchArea);
  nwr["amenity"="fire_station"](area.searchArea);
  nwr["building"="fire_station"](area.searchArea);
  //nwr["amenity"="social_facility"](area.searchArea);
  //nwr["amenity"="pharmacy"](area.searchArea);
  //nwr["amenity"="doctors"](area.searchArea);
);
out body;
>;
out skel qt;
