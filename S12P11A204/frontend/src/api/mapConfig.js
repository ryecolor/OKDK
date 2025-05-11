// src/api/mapConfig.js
import axios from 'axios';

const blockViewConfigs = {
  1: { center_lng: 127.0286, center_lat: 37.4979, zoom: 17.5 },
  2: { center_lng: 127.0366, center_lat: 37.5009, zoom: 17.5 },
  3: { center_lng: 127.0232, center_lat: 37.5042, zoom: 17.5 },
  4: { center_lng: 127.0277, center_lat: 37.4941, zoom: 17.5 },
  5: { center_lng: 127.0412, center_lat: 37.5032, zoom: 17.5 }
};

export const fetchMapConfig = async (blockId = null) => {
  try {
    const response = await axios.get('http://i12a204.p.ssafy.io:8000/api/map-config/config/');
    if (blockId && blockViewConfigs[blockId]) {
      return {
        ...response.data,
        config: {
          ...response.data.config,
          ...blockViewConfigs[blockId]
        }
      };
    }
    return response.data;
  } catch (error) {
    console.error('Map config fetch error:', error);
    return null;
  }
};
