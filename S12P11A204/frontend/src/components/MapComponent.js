import React, { useState, useEffect, useRef } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import { fetchMapConfig } from '../api/mapConfig';
import '../styles/Map.css';

const MapComponent = ({ resetTrigger }) => {
  const [opacity, setOpacity] = useState(0.7);
  const [isMapLoaded, setIsMapLoaded] = useState(false);
  const [mapConfig, setMapConfig] = useState(null);
  const mapContainer = useRef(null);
  const map = useRef(null);
  const floodLayerRef = useRef(null);
  const [legendWarn] = useState("*해당 지역의 현 시점 위험도를 의미하지 않습니다.");

  // Map config 초기화
  useEffect(() => {
    const loadConfig = async () => {
      const config = await fetchMapConfig();
      if (config) {
        setMapConfig(config);
      }
    };
    loadConfig();
  }, []);

  // 맵 초기화
  useEffect(() => {
    if (!mapContainer.current || !mapConfig) return;

    const initializeMap = async () => {
      try {
        mapboxgl.accessToken = mapConfig.config.access_token;
        
        map.current = new mapboxgl.Map({
          container: mapContainer.current,
          style: 'mapbox://styles/mapbox/dark-v11',
          center: [mapConfig.config.center_lng, mapConfig.config.center_lat],
          zoom: mapConfig.config.zoom,
          minZoom: mapConfig.config.min_zoom,
          maxZoom: mapConfig.config.max_zoom,
          pitch: mapConfig.config.pitch,
          bearing: mapConfig.config.bearing,
          antialias: true,
          projection: 'mercator',
          logoPosition: 'top-left',
          terrain: {
            source: 'mapbox-dem',
            exaggeration: 1
          },
        });

        map.current.addControl(
          new mapboxgl.NavigationControl({ visualizePitch: true }),
          'top-left'
        );

        map.current.on('error', (e) => {
          if (!e.error.message.includes('terrain')) {
            console.error('Map error:', e);
          }
        });

        map.current.on('style.load', () => {
          setIsMapLoaded(true);

          // Terrain 소스 추가
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

          // 3D 빌딩 레이어
          map.current.addLayer({
            'id': '3d-buildings',
            'source': 'composite',
            'source-layer': 'building',
            'filter': ['==', 'extrude', 'true'],
            'type': 'fill-extrusion',
            'minzoom': 15,
            'paint': {
              'fill-extrusion-color': '#242424',
              'fill-extrusion-height': [
                'interpolate',
                ['linear'],
                ['zoom'],
                15,
                0,
                15.05,
                ['get', 'height']
              ],
              'fill-extrusion-base': ['get', 'min_height'],
              'fill-extrusion-opacity': 0.8
            }
          });

          // 침수 레이어
          map.current.addSource('flood-source', {
            type: 'raster',
            tiles: [mapConfig.config.flood_layer_url],
            tileSize: 256
          });

          map.current.addLayer({
            id: 'flood-layer',
            type: 'raster',
            source: 'flood-source',
            paint: {
              'raster-opacity': opacity,
              'raster-opacity-transition': { duration: 0 }
            }
          });

          floodLayerRef.current = 'flood-layer';

          // Sky 레이어
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
        });

      } catch (error) {
        console.error('Map initialization error:', error);
      }
    };

    initializeMap();

    return () => {
      if (map.current) {
        map.current.remove();
      }
    };
  }, [mapConfig]);

  // 투명도 업데이트
  useEffect(() => {
    if (!isMapLoaded || !map.current || !floodLayerRef.current) return;
    
    try {
      map.current.setPaintProperty(floodLayerRef.current, 'raster-opacity', opacity);
    } catch (error) {
      console.error('Opacity update error:', error);
    }
  }, [opacity, isMapLoaded]);

  // 리셋 트리거
  useEffect(() => {
    if (!isMapLoaded || !map.current) return;
    
    map.current.flyTo({
      center: [mapConfig.config.center_lng, mapConfig.config.center_lat],
      zoom: mapConfig.config.zoom
    });
  }, [resetTrigger, isMapLoaded, mapConfig]);

  const updateOpacity = (event) => {
    setOpacity(Number(event.target.value));
  };

  return (
    <div className="map-layout">
      <div ref={mapContainer} className="map-container" />
      <div className="map-controls">
        <div className="control-box opacity-control">
          <label htmlFor="opacity">침수 레이어 투명도</label>
          <input 
            type="range" 
            id="opacity" 
            value={opacity} 
            onChange={updateOpacity}
            min="0" 
            max="1" 
            step="0.1"
          />
        </div>
        
        {mapConfig?.legends && (
          <div className="control-box legend-control">
            <h4>침수 흔적도 기준 등급</h4>
            <div className="legend-items">
              {mapConfig.legends.map((item, index) => (
                <div key={index} className="legend-item">
                  <div 
                    className="legend-color" 
                    style={{ 
                      backgroundColor: item.color,
                      width: '20px',
                      height: '20px',
                      borderRadius: '4px'
                    }}
                  />
                  <div>{item.name} ({item.range})</div>
                </div>
              ))}
            </div>
            <div className="legend-warn">{legendWarn}</div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MapComponent;
