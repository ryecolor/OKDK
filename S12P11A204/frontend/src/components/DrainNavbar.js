import React, { useState, useEffect, useCallback, useRef } from 'react';
import '../styles/DrainNavbar.css';

function DrainNavbar({ blockId }) {
  // 상태 변수들 정의
  const [selectedTab, setSelectedTab] = useState('ALL');
  const [drains, setDrains] = useState([]);
  const [selectedDrainInfo, setSelectedDrainInfo] = useState(null);
  const [blockConditions, setBlockConditions] = useState([]);
  const [drainConditions, setDrainConditions] = useState([]);
  const [openDropdown, setOpenDropdown] = useState(null);
  const [lastImageUpdateTime, setLastImageUpdateTime] = useState(null);
  const wsRef = useRef(null);
  const [drainImages, setDrainImages] = useState({});
  const [imageExists, setImageExists] = useState(true);
  const getFloodImagePath = (blockId) => `/flood_block_${blockId}.png`;
  const fetchDrainConditions = async (drainId) => {
    try {
      const response = await fetch(`http://i12a204.p.ssafy.io:8000/drain/${blockId}/${drainId}/draincondition/`);
      const data = await response.json();
      setDrainConditions(data); // 🟢 상태 업데이트 → 리렌더링 트리거
    } catch (error) {
      console.error('Failed to fetch latest drain conditions:', error);
    }
  };

  
  useEffect(() => {
    const img = new Image();
    img.onload = () => setImageExists(true);
    img.onerror = () => setImageExists(false);
    img.src = getFloodImagePath(blockId);
  }, [blockId]);
  
  
  

  // WebSocket 연결 설정
  useEffect(() => {
    wsRef.current = new WebSocket('ws://i12a204.p.ssafy.io:8000/ws/drain_updates/');
  
    wsRef.current.onopen = () => {
      console.log('WebSocket 연결 성공');
    };
  
    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('WebSocket 메시지 수신:', data);
      if (data.type === 'drain_update') {
        updateDrainState(data.message);
      }
      fetchLatestImage(data.id);
      fetchDrainConditions(data.id);
      console.log('이미지 및 표 업데이트 완료')
    };
  
    wsRef.current.onerror = (error) => {
      console.error('WebSocket 오류:', error);
    };
  
    wsRef.current.onclose = () => {
      console.log('WebSocket 연결 종료');
    };
  
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  // WebSocket 메시지 수신 시 호출되는 함수
  const updateDrainState = (data) => {
    setDrainConditions(prevConditions => {
      const updatedConditions = prevConditions.map(condition => 
        condition.id === data.id ? {...condition, condition: data.condition} : condition
      );
      return updatedConditions;
    });
  
    if (selectedDrainInfo && selectedDrainInfo.id === data.id) {
      setSelectedDrainInfo(prevInfo => ({...prevInfo, state: data.condition}));
    }
  
    setLastImageUpdateTime(new Date().toISOString());
    
    // 이미지 URL 업데이트를 위한 API 호출
    fetchLatestImage(data.id);
    fetchDrainConditions(data.id);
  };

  // 최신 이미지 가져오는 함수
  const fetchLatestImage = async (drainId) => {
    try {
      const response = await fetch(`http://i12a204.p.ssafy.io:8000/drain/${blockId}/${drainId}/latest-image/`);
      const data = await response.json();
      if (data.state_img_url) {
        setDrainImages(prevImages => ({...prevImages, [drainId]: data.state_img_url}));
      }
    } catch (error) {
      console.error('Failed to fetch latest image:', error);
    }
  };

  // // 이미지를 주기적으로 업데이트하는 useEffect
  // useEffect(() => {
  //   const intervalId = setInterval(fetchLatestImage, 5000);
  //   return () => clearInterval(intervalId);
  // }, [fetchLatestImage]);

  // 탭 클릭 시 호출되는 함수
  const handleTabClick = async (drainId) => {
    localStorage.setItem(`drainTab_${blockId}`, drainId);
    setSelectedTab(drainId);

    if (drainId === 'ALL') {
      setSelectedDrainInfo(null);
      setDrainConditions([]);
    } else {
      const selectedDrain = drains.find(d => d.id === drainId);
      setSelectedDrainInfo(selectedDrain);
      
      try {
        const response = await fetch(`http://i12a204.p.ssafy.io:8000/drain/${blockId}/${drainId}/draincondition/`);
        const data = await response.json();
        setDrainConditions(data);
        fetchLatestImage(drainId);
      } catch (error) {
        console.error('Failed to fetch drain conditions:', error);
      }
    }
  };

  // 상태 변경 시 호출되는 함수
  const handleStateChange = async (drainConditionId, newState) => {
    if (!selectedDrainInfo) return;  
    try {
      const response = await fetch(
        `http://i12a204.p.ssafy.io:8000/drain/${blockId}/${selectedDrainInfo.id}/${drainConditionId}/state-correction/`, 
        {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ condition: newState })
        }
      );
      const responseData = await response.json();
      if (!response.ok) {
        throw new Error(responseData.error || '상태 업데이트 실패');
      }  
      const updatedResponse = await fetch(
        `http://i12a204.p.ssafy.io:8000/drain/${blockId}/${selectedDrainInfo.id}/draincondition/`
      );
      const updatedData = await updatedResponse.json();
      setDrainConditions(updatedData);
      fetchLatestImage(selectedDrainInfo.id);
    } catch (error) {
    }
  };

  // 이미지 렌더링 컴포넌트
  const ImageComponent = ({ src, alt }) => {
    const [loadError, setLoadError] = useState(false);

    const handleImageError = () => {
      console.error('이미지 로드 실패:', src);
      setLoadError(true);
    };

    useEffect(() => {
      setLoadError(false);
    }, [src]);
  
    if (loadError) {
      return <div>이미지 로드 실패</div>;
    }

    return (
      <img
        src={src}
        alt={alt}
        className="status-image"
        onError={handleImageError}
      />
    );
  };

  // 기타 유틸리티 함수들
  const toggleDropdown = (id) => {
    setOpenDropdown(openDropdown === id ? null : id);
  };

  const handleOptionSelect = (id, option) => {
    handleStateChange(id, option);
    setOpenDropdown(null);
  };

  const formatDateTime = (isoString) => {
    const dt = new Date(isoString);
    return `${dt.getFullYear()}년 ${dt.getMonth() + 1}월 ${dt.getDate()}일 ${dt.getHours()}시 ${dt.getMinutes()}분 ${dt.getSeconds()}초`;
  };

  // 데이터 로딩 함수
  const loadData = async () => {
    try {
      const [drainResponse, blockConditionResponse] = await Promise.all([
        fetch(`http://i12a204.p.ssafy.io:8000/drain/${blockId}/drains/`),
        fetch(`http://i12a204.p.ssafy.io:8000/region/${blockId}/blockcondition/`)
      ]);

      const [drainData, blockConditionData] = await Promise.all([
        drainResponse.json(),
        blockConditionResponse.json()
      ]);

      const sortedDrains = drainData.sort((a, b) => a.id - b.id);
      setDrains(sortedDrains);
      setBlockConditions(blockConditionData);

      const savedTab = localStorage.getItem(`drainTab_${blockId}`);
      if (savedTab && savedTab !== 'ALL') {
        const savedDrain = sortedDrains.find(d => d.id === parseInt(savedTab));
        if (savedDrain) {
          setSelectedTab(savedDrain.id);
          setSelectedDrainInfo(savedDrain);
          const drainConditionResponse = await fetch(`http://i12a204.p.ssafy.io:8000/drain/${blockId}/${savedDrain.id}/draincondition/`);
          const drainConditionData = await drainConditionResponse.json();
          setDrainConditions(drainConditionData);
          fetchLatestImage(savedDrain.id);
        } else {
          setSelectedTab('ALL');
          localStorage.setItem(`drainTab_${blockId}`, 'ALL');
        }
      }
    } catch (error) {
      console.error('Failed to fetch data:', error);
    }
  };

  // 초기 데이터 로딩
  useEffect(() => {
    setSelectedTab('ALL');
    setSelectedDrainInfo(null);
    setDrainConditions([]);
    localStorage.setItem(`drainTab_${blockId}`, 'ALL');
    loadData();
  }, [blockId]);

  // 디버깅을 위한 useEffect
  useEffect(() => {
  }, [drainImages, lastImageUpdateTime]);
  
  return (
    <div className="drain-nav-wrapper">
      <div className="drain-tabs">
        <button
          className={`tab-item ${selectedTab === 'ALL' ? 'active' : ''}`}
          onClick={() => handleTabClick('ALL')}
        >
          {`BLOCK ${blockId}`}
        </button>
        {drains.slice(1).map((drain, index) => (
          <button
            key={drain.id}
            className={`tab-item ${selectedTab === drain.id ? 'active' : ''}`}
            onClick={() => handleTabClick(drain.id)}
          >
            DRAIN {index + 1}
          </button>
        ))}
      </div>
      <div className="drain-container">
        <div className="drain-info">
          <div className="info-content">
            <div className="image-section">
              <h3>{selectedTab === 'ALL' ? 'Flood Image' : 'Check Status'}</h3>
                <div className="image-container">
                  {selectedTab === 'ALL' ? (
                    <>
                      <img 
                        src={getFloodImagePath(blockId)}
                        alt={`Block ${blockId} 침수 현황`} 
                        className="status-image"
                        onError={(e) => {
                          console.error(`Failed to load image for Block ${blockId}`);
                        }}
                      />
                    </>
                  ) : (
                    <>
                      <ImageComponent
                        src={drainImages[selectedTab] || selectedDrainInfo?.state_img_url}
                        alt="배수구 현황"
                      />
                    </>
                  )}
                </div>
            </div>
            
            <div className="table-section">
              <h3>{selectedTab === 'ALL' ? 'Total Scores' : 'Drain Results'}</h3>
              <div className="table-wrapper">
                <table className={selectedTab === 'ALL' ? 'condition-table block-condition' : 'condition-table'}>
                  <thead>
                    <tr>
                      <th>차수</th>
                      <th>점검 시간</th>
                      {selectedTab === 'ALL' ? (
                        <th>점수</th>
                      ) : (
                        <th>상태</th>
                      )}
                    </tr>
                  </thead>
                  <tbody className="condition-table">
                    {selectedTab === 'ALL' ? 
                      [...blockConditions]
                        .sort((a, b) => new Date(b.check_date) - new Date(a.check_date))
                        .map((condition, index) => {
                          const latestIndex = Math.max(...blockConditions.map((_, i) => blockConditions.length - i));
                          const isLatest = blockConditions.length - index === latestIndex;
                          return (
                          <tr
                            key={index}
                            className={isLatest ? 'latest-row' : ''}>
                            <td>{blockConditions.length - index}</td>
                            <td>{formatDateTime(condition.check_date)}</td>
                            <td>{condition.condition} / 100</td>
                          </tr>
                        );
                      })
                      : 
                      [...drainConditions]
                        .sort((a, b) => new Date(b.check_date) - new Date(a.check_date))
                        .map((condition, index) => {
                          const latestIndex = Math.max(...blockConditions.map((_, i) => blockConditions.length - i));
                          const isLatest = blockConditions.length - index === latestIndex;
                          return (
                          <tr
                            key={index}
                            className={isLatest ? 'latest-row' : ''}>
                            <td>{drainConditions.length - index}</td>
                            <td>{formatDateTime(condition.check_date)}</td>
                              <td className="custom-dropdown">
                                <div
                                  className={`dropdown-toggle condition-${
                                    condition.condition === '우수' ? 'excellent' :
                                    condition.condition === '양호' ? 'good' :
                                    condition.condition === '위험' ? 'danger' : ''
                                  }`}
                                  onClick={() => toggleDropdown(condition.id)}
                                >
                                  {condition.condition} <span className="dropdown-arrow">▼</span>
                                </div>
                                {openDropdown === condition.id && (
                                  <ul className="dropdown-menu">
                                    {['우수', '양호', '위험'].map((option) => (
                                      <li
                                        key={option}
                                        onClick={() => handleOptionSelect(condition.id, option)}
                                        className={`dropdown-item condition-${
                                          option === '우수' ? 'excellent' :
                                          option === '양호' ? 'good' :
                                          option === '위험' ? 'danger' : ''
                                        }`}
                                      >
                                        {option}
                                      </li>
                                    ))}
                                  </ul>
                                )}
                              </td>
                          </tr>
                        );
                      })
                    }
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default DrainNavbar;