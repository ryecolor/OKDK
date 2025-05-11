import React, { useState, useEffect, useMemo, useCallback } from 'react';
import DrainageMapComponent from './DrainageMapComponent';
import { fetchMapConfig } from '../api/mapConfig';
import '../styles/Detail.css';
import DrainNavbar from './DrainNavbar';
import LoadingOverlay from './LoadingOverlay';

const DetailComponent = React.memo(function DetailComponent({ block, onActivate }) {
  const [mapConfig, setMapConfig] = useState(null);
  const [blockDrains, setBlockDrains] = useState([]);
  const [isInitialLoad, setIsInitialLoad] = useState(true);
  const blockId = parseInt(block.replace(/\D/g, ''));
  const [isActive, setIsActive] = useState(() => {
    const saved = localStorage.getItem(`isActive_${block}`);
    return saved ? JSON.parse(saved) : false;
  });
  const [activeBlocks, setActiveBlocks] = useState(() => {
    const saved = localStorage.getItem('activeBlocks');
    return saved ? JSON.parse(saved) : [];
  });

  useEffect(() => {
    localStorage.setItem('activeBlocks', JSON.stringify(activeBlocks));
  }, [activeBlocks]);

  useEffect(() => {
    localStorage.setItem(`isActive_${block}`, JSON.stringify(isActive));
  }, [isActive, block]);

  useEffect(() => {
    let isMounted = true;
    
    const loadResources = async () => {
      try {
        if (isMounted) {
          setIsInitialLoad(true);
        }

        const [config, drainsResponse] = await Promise.all([
          fetchMapConfig(),
          fetch(`http://i12a204.p.ssafy.io:8000/drain/${blockId}/drains/`)
        ]);
        
        const drainsData = await drainsResponse.json();
        
        if (isMounted) {
          setMapConfig(config);
          setBlockDrains(drainsData);
          setIsInitialLoad(false);
        }
      } catch (error) {
        console.error('Resource Load Error:', error);
        if (isMounted) {
          setIsInitialLoad(false);
        }
      }
    };

    loadResources();
    
    return () => {
      isMounted = false;
    };
  }, [blockId]);

  const memoizedMapConfig = useMemo(() => mapConfig, [mapConfig]);

  const handleActivate = useCallback((blockId, isActive) => {
    setActiveBlocks((prev) =>
      isActive 
        ? [...prev, blockId]
        : prev.filter((id) => id !== blockId)
    );
    onActivate(block, isActive);
    console.log("🟢", isActive, onActivate);
  }, [block, blockId, onActivate]);
  

  if (isInitialLoad || !mapConfig || !blockDrains.length) {
    return <LoadingOverlay />;
  }

  return (
    <div className="detail-container">
      <div className="map-section">
        <DrainageMapComponent 
          mapConfig={memoizedMapConfig}
          drainData={blockDrains}
          blockId={blockId}
          activeBlocks={activeBlocks}
          onActivate={handleActivate}
        />
      </div>
      <DrainNavbar blockId={blockId} />
    </div>
  );
});

export default DetailComponent;
