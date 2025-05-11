import React, { useState, useEffect, useRef } from 'react';
import '../styles/BlockNavbar.css';
import viewIcon from '../assets/view.png';
import smallViewIcon from '../assets/small_view.png';

function BlockNavbar({ blocks, selectedBlock, setSelectedBlock, isSidebarCollapsed, activeBlocks }) {
  const [videoStream, setVideoStream] = useState(() => {
    // localStorage에서 저장된 비디오 스트림 상태를 불러옵니다.
    const saved = localStorage.getItem('videoStream');
    return saved ? JSON.parse(saved) : null;
  });
  const [expandedView, setExpandedView] = useState(null);
  const wsRef = useRef(null);

  // videoStream 상태가 변경될 때마다 localStorage에 저장합니다.
  useEffect(() => {
    localStorage.setItem('videoStream', JSON.stringify(videoStream));
  }, [videoStream]);
  
  
  // WebSocket 연결 코드 (기존과 동일)
  useEffect(() => {
    // WebSocket 연결 설정
    wsRef.current = new WebSocket('ws://i12a204.p.ssafy.io:8000/ws/video_stream/');
    
    wsRef.current.onopen = () => {
      console.log("WebSocket 연결 성공");
    };

    wsRef.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.frame) {
          setVideoStream(`data:image/jpeg;base64,${data.frame}`);
        }
      } catch (error) {
        console.error("비디오 프레임 처리 중 오류:", error);
      }
    };

    wsRef.current.onerror = (error) => {
      console.error("WebSocket 오류:", error);
    };

    wsRef.current.onclose = () => {
      console.log("WebSocket 연결 종료");
    };

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const handleViewClick = (e, block) => {
    e.stopPropagation();
    setExpandedView(expandedView === block ? null : block);
  };

  const handleBlockClick = (block) => {
    setSelectedBlock(block);
  };

  return (
    <div key={activeBlocks.join('-')} className={`block-navbar ${isSidebarCollapsed ? 'collapsed' : ''}`}>
      {blocks.map((block) => (
        <button
          key={block}
          className={`block-item ${selectedBlock === block ? 'current' : ''} ${activeBlocks.some(b => b == block) ? 'activated' : ''} ${isSidebarCollapsed ? 'collapsed' : ''}`}
          onClick={() => handleBlockClick(block)}
          data-block={block}
        >
          {!isSidebarCollapsed ? (
            // 큰 화면
            <>
              {block === '전체 보기' ? '강남구 전체 보기' :
                block === '1' ? 'BLOCK 1 : 삼성생명 서초타워' :
                block === '2' ? 'BLOCK 2 : 삼성전자 서초사옥' :
                block === '3' ? 'BLOCK 3 : 현대성우빌딩' :
                block === '4' ? 'BLOCK 4 : 삼성스토어 강남' :
                block === '5' ? 'BLOCK 5 : 강남지웰타워' : block}
              {activeBlocks.some(b => b == block) && block !== '전체 보기' && (
                <div className="video-container">
                  <div className="robot-status">
                    1번 로봇 🟢
                  </div>
                  {videoStream ? (
                    <img 
                      src={videoStream} 
                      alt="Live Stream" 
                      className="live-video"
                    />
                  ) : (
                    <div className="video-loading loading-detail">스트림 연결 중...</div>
                  )}
                </div>
              )}
            </>
          ) : (
            // 작은 화면
            <>
              {block === '전체 보기' ? (
                <span className="block-id"></span>
              ) : activeBlocks.some(b => b == block) ? (
                <img 
                  src={expandedView === block ? smallViewIcon : viewIcon} 
                  alt="View" 
                  className="view-icon"
                  onClick={(e) => handleViewClick(e, block)}
                />
              ) : (
                <span className="block-id">{block}</span>
              )}
              {expandedView === block && activeBlocks.some(b => b == block) && block !== '전체 보기' && (
                <div className="stream-container">
                  <div className="robot-status">
                    1번 로봇 🟢
                  </div>
                  <div className="video-container">
                    {videoStream ? (
                      <img 
                        src={videoStream} 
                        alt="Live Stream" 
                        className="live-video"
                      />
                    ) : (
                      <div className="video-loading loading-detail">스트림 연결 중...</div>
                    )}
                  </div>
                </div>
              )}
            </>
          )}
        </button>
      ))}
    </div>
  );
}

export default BlockNavbar;
