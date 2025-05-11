import React, { useState, useEffect, useRef, useCallback } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

mapboxgl.setRTLTextPlugin(
  'https://api.mapbox.com/mapbox-gl-js/plugins/mapbox-gl-rtl-text/v0.2.3/mapbox-gl-rtl-text.js',
  null,
  true
);

const BaseMapComponent = React.memo(({ mapConfig, customConfig, customLayers = [], onStyleLoad }) => {
  const mapContainer = useRef(null);
  const map = useRef(null);
  const [isMapLoaded, setIsMapLoaded] = useState(false);

  const addBaseLayers = useCallback(() => {
    if (!map.current) return;

    map.current.addSource('mapbox-dem', {
      type: 'raster-dem',
      url: 'mapbox://mapbox.mapbox-terrain-dem-v1',
      tileSize: 512,
      maxzoom: 14
    });

    map.current.setTerrain({
      source: 'mapbox-dem',
      exaggeration: 1
    });

    map.current.addLayer({
      'id': '3d-buildings',
      'source': 'composite',
      'source-layer': 'building',
      'filter': ['==', 'extrude', 'true'],
      'type': 'fill-extrusion',
      'minzoom': 15,
      'paint': {
        'fill-extrusion-color': '#242424',
        'fill-extrusion-base': ['get', 'min_height'],
        'fill-extrusion-opacity': 0
      }
    });

    map.current.addLayer({
      'id': 'sky',
      'type': 'sky',
      'paint': {
        'sky-type': 'atmosphere',
        'sky-atmosphere-sun': [0.0, 90.0],
        'sky-atmosphere-sun-intensity': 15,
        'sky-atmosphere-color': '#2E3034',
        'sky-atmosphere-halo-color': '#DFE27C',
        'sky-gradient': [
          'interpolate',
          ['linear'],
          ['sky-radial-progress'],
          0.8,
          'rgba(46, 48, 52, 1)',
          1,
          'rgba(46, 48, 52, 0.1)'
        ],
        'sky-opacity': [
          'interpolate',
          ['exponential', 0.1],
          ['zoom'],
          5,
          0,
          22,
          1
        ]
      }
    });
  }, []);

  useEffect(() => {
    if (!mapContainer.current || !mapConfig || map.current) return;

    const finalConfig = {
      ...mapConfig.config,
      ...(customConfig || {}),
      zoom: 17.2,
      pitch: 0,
      bearing: 0,
      maxZoom: 22
    };

    mapboxgl.accessToken = finalConfig.access_token;
    
    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/dark-v11',
      center: [finalConfig.center_lng, finalConfig.center_lat],
      zoom: finalConfig.zoom,
      minZoom: finalConfig.min_zoom,
      maxZoom: finalConfig.maxZoom,
      pitch: finalConfig.pitch,
      bearing: finalConfig.bearing,
      antialias: true,
      projection: 'mercator'
    });

    map.current.addControl(
      new mapboxgl.NavigationControl({ visualizePitch: true }),
      'top-left'
    );

    map.current.once('load', () => {
      const point = map.current.project([finalConfig.center_lng, finalConfig.center_lat]);
      point.x += 15;
      point.y -= 100;
      const newCenter = map.current.unproject(point);
    
      map.current.flyTo({
        center: newCenter,
        zoom: finalConfig.zoom,
        pitch: finalConfig.pitch,
        bearing: finalConfig.bearing,
        essential: true
      });
      
      setIsMapLoaded(true);
      addBaseLayers();
      
      customLayers.forEach(layer => {
        setTimeout(() => {
          if (map.current.getSource(layer.sourceId)) {
            map.current.removeSource(layer.sourceId);
          }
      
          if (layer.source) {
            map.current.addSource(layer.sourceId, layer.source);
          }
      
          if (map.current.getLayer(layer.layer.id)) {
            map.current.removeLayer(layer.layer.id);
          }
      
          map.current.addLayer({
            ...layer.layer,
            source: layer.sourceId
          });
        }, 3); // 딜레이
      });
      
  

      if (onStyleLoad) {
        onStyleLoad(map.current);
      }
    });

    return () => {
      if (map.current) {
        map.current.remove();
        map.current = null;
      }
    };
  }, [mapConfig, customConfig, customLayers, onStyleLoad, addBaseLayers]);

  return (
    <div className="map-layout">
      <div ref={mapContainer} className="map-container" />
    </div>
  );
});

export default BaseMapComponent;
