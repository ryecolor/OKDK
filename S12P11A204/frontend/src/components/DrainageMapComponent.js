import React, { useEffect, useState, useRef, useCallback, useMemo, Suspense } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import '../styles/DrainageMap.css';
import playIcon from '../assets/play-icon.png';
import stopIcon from '../assets/stop-icon.png';
import homeIcon from '../assets/home-icon.png';
import robotImage from '../assets/robot.png';
import axios from 'axios';
import { toast } from 'react-toastify';

const BaseMapComponent = React.lazy(() => import('./BaseMapComponent'));

const DrainageMapComponent = React.memo(({ mapConfig: initialMapConfig, drainData, blockId, onActivate, activeBlocks }) => {
  const [isMapLoaded, setIsMapLoaded] = useState(false);
  const [isActive, setIsActive] = useState(() => {
    const savedState = localStorage.getItem(`isActive_${blockId}`);
    return savedState ? JSON.parse(savedState) : false;
  });
  const [selectedDrains, setSelectedDrains] = useState(drainData.slice(1).map(drain => drain.id));
  const [robotPosition, setRobotPosition] = useState(() => {
    const savedPosition = localStorage.getItem(`robotPosition_${blockId}`);
    return savedPosition ? JSON.parse(savedPosition) : null;
  });  
  const mapRef = useRef(null);
  const markersRef = useRef({});
  const wsRef = useRef(null);
  const [showRoute, setShowRoute] = useState(() => {
    const saved = localStorage.getItem(`showRoute_${blockId}`);
    return saved ? JSON.parse(saved) : false;
  });
  

  useEffect(() => {
    setIsActive(activeBlocks.includes(blockId));
  }, [activeBlocks, blockId]);  

  useEffect(() => {
    localStorage.setItem(`isActive_${blockId}`, JSON.stringify(isActive));
  }, [isActive, blockId]);

  useEffect(() => {
    if (robotPosition !== null) {
      localStorage.setItem(`robotPosition_${blockId}`, JSON.stringify(robotPosition));
    }
  }, [robotPosition, blockId]);
  

  const calculateAverageCoordinates = useCallback((drains) => {
    if (drains.length === 0) return [0, 0];
    const sumY = drains.reduce((sum, drain) => sum + drain.location_y, 0);
    const sumX = drains.reduce((sum, drain) => sum + drain.location_x, 0);
    return [sumY / drains.length, sumX / drains.length];
  }, []);

  const mapCenter = useMemo(() => {
    const [avgLng, avgLat] = calculateAverageCoordinates(drainData);
    return {
      center_lng: avgLng,
      center_lat: avgLat,
      zoom: 16
    };
  }, [drainData, calculateAverageCoordinates]);

  const updateMarkerState = useCallback((drainId, isActive, condition) => {
    const marker = markersRef.current[drainId];
    if (marker) {
      const el = marker.getElement().querySelector('.drain-marker');
      el.classList.toggle('inactive', !isActive);
      if (condition) {
        el.classList.remove('good', 'medium', 'bad');
        el.classList.add(condition === '우수' ? 'good' : condition === '양호' ? 'medium' : 'bad');
      }
    }
  }, []);

  const toggleDrain = useCallback((drainId) => {
    if (isActive) return; // 媛��� 以묒씪 �뚮뒗 �좉� 湲곕뒫 鍮꾪솢�깊솕
    setSelectedDrains(prevDrains => {
      const isSelected = prevDrains.includes(drainId);
      const newDrains = isSelected 
        ? prevDrains.filter(id => id !== drainId)
        : [...prevDrains, drainId];

      updateMarkerState(drainId, !isSelected);
      return newDrains;
    });
  }, [updateMarkerState]);

  
  const addMarkers = useCallback((map) => {
    if (!map || !map.getCanvas()) return;
    
    Object.values(markersRef.current).forEach(marker => marker.remove());
    markersRef.current = {};
    
    drainData.forEach((drain, index) => {
      const el = document.createElement('div');
      el.className = 'drain-marker-container';
      const inner = document.createElement('div');
      inner.className = 'drain-marker';
      
      if (index === 0) {
        const imgElement = document.createElement('img');
        imgElement.src = homeIcon;
        imgElement.alt = 'Home';
        imgElement.className = 'home-icon';
        inner.appendChild(imgElement);
        inner.classList.add('home-base');
      } else {
        inner.textContent = index;
        if (!isActive) {
          el.addEventListener('click', () => toggleDrain(drain.id));
        }
      }
      
      el.appendChild(inner);

      const marker = new mapboxgl.Marker(el)
        .setLngLat([drain.location_y, drain.location_x])
        .addTo(map);

      markersRef.current[drain.id] = marker;
      updateMarkerState(drain.id, selectedDrains.includes(drain.id));
    });
  }, [drainData, selectedDrains, updateMarkerState, toggleDrain]);

  const handleMapLoad = useCallback((map) => {
    mapRef.current = map;
    const [avgLng, avgLat] = calculateAverageCoordinates(drainData);
    map.setCenter([avgLng, avgLat - 0.0014]);
    map.setZoom(mapCenter.zoom);
    addMarkers(map);
    setIsMapLoaded(true);
  }, [calculateAverageCoordinates, drainData, mapCenter, addMarkers]);

  const getRoute = useCallback(async (coordinates) => {
    if (!initialMapConfig || !initialMapConfig.config || !initialMapConfig.config.access_token) return null;
    const accessToken = initialMapConfig.config.access_token;
    const url = `https://api.mapbox.com/directions/v5/mapbox/walking/${coordinates.join(';')}?geometries=geojson&access_token=${accessToken}`;
  
    try {
      const response = await fetch(url);
      const data = await response.json();
      return data.routes[0].geometry;
    } catch (error) {
      console.error('Error fetching route:', error);
      return null;
    }
  }, [initialMapConfig]);
  

  const drawRoute = useCallback(async (map, coordinates) => {
    if (!map) return;
  
    // 기존에 추가된 source와 layer를 제거
    coordinates.forEach((_, i) => {
      const sourceId = `route-${i}`;
      const layerId = `route-layer-${i}`;
  
      if (map.getSource(sourceId)) {
        map.removeLayer(layerId);
        map.removeSource(sourceId);
      }
    });
  
    // 새 경로 추가
    for (let i = 0; i < coordinates.length - 1; i++) {
      const start = coordinates[i];
      const end = coordinates[i + 1];
      const routeGeometry = await getRoute([start, end]);
      if (routeGeometry && routeGeometry.type === 'LineString' && Array.isArray(routeGeometry.coordinates)) {
        const sourceId = `route-${i}`;
        const layerId = `route-layer-${i}`;
  
        // 중복 방지: 기존 source 삭제 후 추가
        if (map.getSource(sourceId)) {
          map.removeLayer(layerId);
          map.removeSource(sourceId);
        }
  
        map.addSource(sourceId, {
          type: 'geojson',
          lineMetrics: true,
          data: {
            type: 'Feature',
            properties: {},
            geometry: routeGeometry,
          }
        });
  
        map.addLayer({
          id: layerId,
          type: 'line',
          source: sourceId,
          layout: {
            'line-join': 'round',
            'line-cap': 'round'
          },
          paint: {
            'line-width': 5,
            'line-opacity': 0.7,
            'line-gradient': [
              'interpolate',
              ['linear'],
              ['line-progress'],
              0, '#6e99c4',
              0.3, '#8691a9',
              0.7, '#99c7db',
              1, '#6e99c4'
            ]
          }
        });
      }
    }
  }, [getRoute]);
  

  useEffect(() => {
    if (showRoute && mapRef.current) {
      const homeBase = drainData[0];
      const selectedDrainData = drainData
        .filter(drain => selectedDrains.includes(drain.id) && drain.index !== 0)
        .sort((a, b) => a.index - b.index);
  
      const circularRouteCoordinates = [
        [homeBase.location_y, homeBase.location_x],
        ...selectedDrainData.map(drain => [drain?.location_y, drain?.location_x]),
        [homeBase.location_y, homeBase.location_x],
      ];
  
      drawRoute(mapRef.current, circularRouteCoordinates);
    }
  }, [showRoute, drainData, drawRoute, selectedDrains]);
  

  const connectWebSocket = useCallback(() => {
    if (wsRef.current) return;
    console.log('Attempting to connect WebSocket...');
    wsRef.current = new WebSocket('ws://i12a204.p.ssafy.io:8000/ws/drain_updates/');
  
    wsRef.current.onopen = (event) => {
      console.log('WebSocket connected successfully', event);
    };
  
    wsRef.current.onmessage = (event) => {
      console.log('WebSocket message received:', event.data);
      try {
        const data = JSON.parse(event.data);
        console.log('Parsed WebSocket data:', data);
        if (data.arrive === true && data.id == null) {
          console.log(`Block inspection completed for block ${blockId}`);
          toast.dismiss(); // 모든 기존 토스트 제거
          toast.success(`${blockId}번 블록 점검이 완료되었습니다.`);
          handleActivate();
        } else if (data.arrive === true && data.id) {
          console.log(`Robot position updated to ${data.id}`);
          setRobotPosition(data.id);
        } else if (data.id) {
          console.log(`Drain state updated for id ${data.id}, condition: ${data.condition}`);
          updateMarkerState(data.id, true, data.condition);
        }
      } catch (error) {
        console.error('WebSocket message parsing error:', error);
        console.error('Raw message data:', event.data);
      }
    };
  
    wsRef.current.onerror = (error) => {
      console.error('WebSocket error occurred:', error);
      console.error('WebSocket readyState:', wsRef.current.readyState);
    };
  
    wsRef.current.onclose = (event) => {
      console.log('WebSocket connection closed', event);
      console.log('Close event code:', event.code);
      console.log('Close event reason:', event.reason);
      console.log('WebSocket readyState:', wsRef.current.readyState);
      // Uncomment the following line to enable auto-reconnect
      // setTimeout(() => connectWebSocket(), 5000);
      wsRef.current = null;
    }
  }, [blockId, onActivate, updateMarkerState, setRobotPosition]);
  
  useEffect(() => {
    if (isActive&& !wsRef.current) {
      connectWebSocket();
    }
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [isActive]);  

  const handleActivate = useCallback(async () => {
    if (isActive) {
      // 🚨 활성화 상태일 때 비활성화 처리 추가 🚨
      await axios.post(
        `http://i12a204.p.ssafy.io:8000/region/${blockId}/deactivate_robot/`,
        {},
        {
          headers: { 'Content-Type': 'application/json' }
        }
      );
      setIsActive(false);
      setShowRoute(false);
      onActivate(blockId, false);
      // WebSocket 종료
      if (wsRef.current) {
        wsRef.current.close();
      }
      setRobotPosition(null);
      localStorage.removeItem(`robotPosition_${blockId}`);
      // 로봇 마커 제거
      if (markersRef.current['robot']) {
        markersRef.current['robot'].remove();
        delete markersRef.current['robot'];
      }
      // 지도에서 기존 경로 제거
      if (mapRef.current) {
        for (let i = 0; mapRef.current.getLayer(`route-layer-${i}`); i++) {
          mapRef.current.removeLayer(`route-layer-${i}`);
          mapRef.current.removeSource(`route-${i}`);
        }
      }
      return;
    }

    if (selectedDrains.length < 2) {
      alert("2개 이상의 배수구를 선택해 주세요.");
      return;
    }

    try {
      await axios.post(
        'http://i12a204.p.ssafy.io:8000/region/select-robot/',
        {
          district_id: 1,
          block_id: parseInt(blockId),
          drain_ids: selectedDrains
        },
        {
          headers: { 'Content-Type': 'application/json' }
        }
      );

      // 🚀 활성화 처리
      setIsActive(true);
      setShowRoute(true);
      onActivate(blockId, true);
      connectWebSocket();
      setRobotPosition(drainData[0].id);

      const homeBase = drainData[0];
      const selectedDrainData = drainData
        .filter(drain => selectedDrains.includes(drain.id) && drain.index !== 0)
        .sort((a, b) => a.index - b.index);

      const circularRouteCoordinates = [
        [homeBase.location_y, homeBase.location_x],
        ...selectedDrainData.map(drain => [drain?.location_y, drain?.location_x]),
        [homeBase.location_y, homeBase.location_x],
      ];

      if (mapRef.current) {
        await drawRoute(mapRef.current, circularRouteCoordinates);

        drainData.forEach((drain, index) => {
          const isSelected = selectedDrains.includes(drain.id);
          updateMarkerState(drain.id, isSelected);

          const marker = markersRef.current[drain.id];
          if (marker) {
            const el = marker.getElement().querySelector('.drain-marker');
            if (index === 0) {
              el.classList.add('home-base');
            } else {
              el.textContent = index;
            }
          }
        });
      }
    } catch (error) {
      console.error('오류 발생:', error);
      if (error.response) {
        console.error('서버 응답 오류:', error.response.data);
      } else {
        console.error('클라이언트 오류:', error.message);
      }
      alert("활성화 중 오류가 발생했습니다. 다시 시도해 주세요.");
    }
  }, [isActive, blockId, selectedDrains, onActivate, connectWebSocket, drainData, drawRoute, updateMarkerState]);
  
  useEffect(() => {
    if (mapRef.current && robotPosition !== null) {
      // 기존 로봇 마커 제거
      const robotMarker = markersRef.current['robot'];
      if (robotMarker) robotMarker.remove();
  
      // 로봇 위치를 localStorage에서 가져오기
      const savedRobotPosition = localStorage.getItem(`robotPosition_${blockId}`);
      const parsedRobotPosition = savedRobotPosition ? JSON.parse(savedRobotPosition) : robotPosition;
  
      if (parsedRobotPosition !== null) {
        setRobotPosition(parsedRobotPosition); // 상태 업데이트
  
        const el = document.createElement('div');
        el.className = 'robot-marker';
        
        const img = document.createElement('img');
        img.src = robotImage;
        img.alt = 'Robot';
        el.appendChild(img);
  
        const robotDrain = drainData.find(drain => drain.id === parsedRobotPosition);
        if (robotDrain) {
          const newMarker = new mapboxgl.Marker(el)
            .setLngLat([robotDrain.location_y, robotDrain.location_x])
            .addTo(mapRef.current);
          markersRef.current['robot'] = newMarker;
        }
      }
    }
  }, [robotPosition, isActive, drainData, blockId, mapRef]);
  

  const memoizedMapConfig = useMemo(() => ({
    ...initialMapConfig,
    config: {
      ...initialMapConfig.config,
      ...mapCenter
    }
  }), [initialMapConfig, mapCenter]);

  return (
    <div className={`drainage-map-container ${isMapLoaded ? 'loaded' : ''}`}>
      <Suspense fallback={<div className="map-skeleton"></div>}>
        <BaseMapComponent 
          mapConfig={memoizedMapConfig}
          onStyleLoad={handleMapLoad}
        />
      </Suspense>
      {isMapLoaded && (
        <button className="activate-button" onClick={handleActivate}>
          <img 
            src={isActive ? stopIcon : playIcon} 
            alt={isActive ? "Deactivate" : "Activate"} 
            className={`activate-icon ${isActive ? 'active' : ''}`} 
          />
        </button>
      )}
    </div>
  );
});

export default DrainageMapComponent;