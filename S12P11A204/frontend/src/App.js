import React, { useRef, useState, useEffect } from 'react';
import './styles/App.css';
import { register, login, logout, getCurrentUser, deleteAccount, setAuthToken } from './api';
import * as drainageMapComponent from './components/DrainageMapComponent';
import MapComponent from './components/MapComponent';
import InfoComponent from './components/InfoComponent';
import WeatherComponent from './components/WeatherComponent';
import logo from './assets/logo.png';
import userIcon from './assets/user.png';
import weatherIcon from './assets/weather-icon.png';
import AlertComponent from './components/AlertComponent';
import alertIcon from './assets/alert-icon.png';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import BlockNavbar from './components/BlockNavbar';
import DetailComponent from './components/DetailComponent';

function App() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [district, setDistrict] = useState('');
  const [isLogin, setIsLogin] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [isLoginView, setIsLoginView] = useState(true);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deletePassword, setDeletePassword] = useState('');
  const [showWeather, setShowWeather] = useState(false);
  const [ws, setWs] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [unreadAlerts, setUnreadAlerts] = useState(0);
  const [showAlerts, setShowAlerts] = useState(false);
  const websocketRef = useRef(null);
  const [selectedBlock, setSelectedBlock] = useState(() => {
    const saved = localStorage.getItem('selectedBlock');
    return saved ? saved : '전체 보기';
  });
  // 새로 추가할 상태
  const [activeBlocks, setActiveBlocks] = useState(() => {
    // localStorage에서 저장된 상태를 불러옵니다.
    const saved = localStorage.getItem('activeBlocks');
    return saved ? JSON.parse(saved) : [];
  });

  useEffect(() => {
    localStorage.setItem('activeBlocks', JSON.stringify(activeBlocks));
  }, [activeBlocks]);

  const handleToggleActivation = (blockId) => {
    setActiveBlocks(prev => {
      const newActiveBlocks = prev.includes(blockId) 
        ? prev.filter(id => id !== blockId) 
        : [...prev, blockId];
      return newActiveBlocks;
    });
  };

// newAlert 변수 정의
const newAlert = (message) => {
  toast(message);
};

// 저장된 알림을 불러오는 useEffect 추가
useEffect(() => {
  const savedAlerts = localStorage.getItem('weatherAlerts');
  if (savedAlerts) {
    const parsedAlerts = JSON.parse(savedAlerts);
    setAlerts(parsedAlerts);
    setUnreadAlerts(parsedAlerts.filter(alert => !alert.read).length);
  }
}, []);

// WebSocket 연결을 위한 useEffect
useEffect(() => {
  const token = localStorage.getItem('jwtToken');
  websocketRef.current = new WebSocket(`ws://i12a204.p.ssafy.io:8000/api/socket/alerts/`);
  
  websocketRef.current.onopen = () => {
    console.log("WebSocket 연결 성공!");
  };

  websocketRef.current.onmessage = (event) => {
    const data = JSON.parse(event.data);
    // drainageMapComponent.updateMarkerState(data.id, true, data.condition);
    const newAlert = {
      message: data.message,
      created_at: new Date().toISOString(),
      read: false
    };
    
    setAlerts(prevAlerts => {
      const updatedAlerts = [newAlert, ...prevAlerts].slice(0, 10);
      localStorage.setItem('weatherAlerts', JSON.stringify(updatedAlerts));
      return updatedAlerts;
    });
    
    setUnreadAlerts(prev => prev + 1);
    toast(data.message, {
      onClick: () => {
        setAlerts(prevAlerts => {
          const updatedAlerts = prevAlerts.map((alert, index) => 
            index === 0 ? { ...alert, read: true } : alert
          );
          localStorage.setItem('weatherAlerts', JSON.stringify(updatedAlerts));
          return updatedAlerts;
        });
        setUnreadAlerts(prev => Math.max(0, prev - 1));
      }
    });
  };

  websocketRef.current.onerror = (error) => {
    console.error("WebSocket 에러:", error);
  };

  websocketRef.current.onclose = () => {
    console.log("WebSocket 연결 종료");
  };

  if (token) {
    setAuthToken(token);
    setIsLogin(true);
    setUser(getCurrentUser());
  }

  return () => {
    if (websocketRef.current) {
      websocketRef.current.close();
    }
  };
}, []);

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    if (!username || !password || !district) {
      setError('모든 필드를 입력해 주세요.');
      setLoading(false);
      return;
    }

    try {
      const response = await register(username, password, district);
      console.log('Registration successful:', response);
      // 회원가입 성공 후 바로 로그인 시도
      await handleLogin(e);
    } catch (error) {
      console.error('Registration failed:', error);
      setError(error.response?.data?.message || '회원 가입에 실패했습니다. 다시 시도해 주세요.');
      setLoading(false);
    }
  };


  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
  
    if (!username || !password) {
      setError('아이디와 비밀번호를 입력해 주세요.');
      setLoading(false);
      return;
    }
  
    try {
      const response = await login(username, password);
      console.log('Login successful:', response);
      setAuthToken(response.data.access);
      setIsLogin(true);
      setUser({ username: username });
      localStorage.setItem('user', JSON.stringify({ username: username }));
    } catch (error) {
      console.error('Login failed:', error);
      setError(error.response?.data?.message || '로그인에 실패했습니다. 다시 시도해 주세요.');
    } finally {
      setLoading(false);
    }
  };
  

  const handleLogout = () => {
    logout();
    setIsLogin(false);
    setUser(null);
    setAuthToken(null);
    setSelectedBlock('전체 보기'); // 추가
    localStorage.removeItem('selectedBlock'); // 추가
  };
  

  const handleWithdraw = async () => {
    try {
      if (!deletePassword) {
        setError('비밀번호를 입력해 주세요.');
        return;
      }
  
      const result = await deleteAccount(deletePassword);
      
      // 성공적인 응답인 경우에만 탈퇴 처리
      if (result.success) {
        alert('회원 탈퇴가 완료되었습니다.');
        handleLogout();
        setShowDeleteModal(false);
        setDeletePassword('');
        setError('');
        setIsLoginView(true);
      }
    } catch (error) {
      alert('비밀번호가 올바르지 않습니다.');
      setError(error.message);
      setDeletePassword('');
    }
  };
  

  // App.js에서 새로운 state 추가
  const [deleteWarning, setDeleteWarning] = useState('');

  // 회원 탈퇴 버튼 클릭 핸들러 수정
  const handleDeleteClick = () => {
    if (showDeleteModal) {
      setDeleteWarning('버튼 하단에 PW를 입력해 주세요.');
    } else {
      setShowDeleteModal(true);
      setDeleteWarning('');
    }
  };

  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  useEffect(() => {
    localStorage.setItem('selectedBlock', selectedBlock);
  }, [selectedBlock]);
  

  useEffect(() => {
    const handleResize = () => {
      if (isLogin) {
        setIsSidebarCollapsed(window.innerWidth <= 768);
      }
    };

    window.addEventListener('resize', handleResize);
    handleResize(); // 초기 실행

    return () => {window.removeEventListener('resize', handleResize);
      // if (websocket) {
      //   websocket.close();
      // }
    };
  }, [isLogin]);

  const toggleWeather = () => {
    setShowWeather(prev => !prev);
    setShowAlerts(false); // Alert 창 즉시 닫기
  };

  const toggleAlerts = () => {
    setShowAlerts(prev => !prev);
    setShowWeather(false); // Weather 창 즉시 닫기
  };

  // 클릭 핸들러 수정
  const handleWeatherClick = (e) => {
    e.preventDefault();
    toggleWeather(); // 수정된 toggle 함수 호출
  };

  const handleAlertClick = () => {
    toggleAlerts(); // 직접 상태 변경 대신 toggle 함수 사용
    if (!showAlerts) {
      setUnreadAlerts(0);
      setAlerts(prevAlerts => prevAlerts.map(alert => ({...alert, read: true})));
    }
  };

  const resetHome = () => {
    setUsername('');
    setPassword('');
    setError('');
    setShowDeleteModal(false);
    setDeletePassword('');
    setShowWeather(false);
    setSelectedBlock('전체 보기');
    localStorage.setItem('selectedBlock', '전체 보기');
  };

  return (
    <>
      <div className="layout-container">
        <div className={`user-panel ${isSidebarCollapsed ? 'collapsed' : ''}`}>
          <div className="logo-container" onClick={resetHome}>
            <img src={logo} alt="Logo" className="logo" />
          </div>
          {isLogin ? (
            <>
              <div className='user-box'>
                <div className="user-info">
                  <img src={userIcon} alt="User Profile" className="profile-img" />
                  <div className='greeting'>
                    <p>안녕하세요,</p>
                    <p>{user.username} 관리자님!</p>
                  </div>
                </div>
                <div>
                  <div className="button-group">
                    <button onClick={handleLogout} className="primary-button">로그아웃</button>
                    {!isSidebarCollapsed && (
                    <button onClick={handleDeleteClick} className="secondary-button">회원 탈퇴</button>
                    )}
                  </div>
                  {deleteWarning && <p className="warning-text">{deleteWarning}</p>}
                </div>
                {isSidebarCollapsed && (
                    <div className='signout-message'>
                      <p>*회원 탈퇴는</p>
                      <p>전체 화면에서만</p>
                      <p>가능합니다.</p>
                    </div>
                  )}
              </div>
              {showDeleteModal && (
              <div className="delete-confirm">
                <div className="form-group password-input">
                  <label htmlFor="password">Password</label>
                  <input
                    type="password"
                    id="password"
                    value={deletePassword}
                    onChange={(e) => setDeletePassword(e.target.value)}
                    required
                    placeholder='Enter your PW'
                  />
                </div>
                <p className="warning-text">정말로 탈퇴하시겠습니까?</p>
                <p className="warning-text">이 작업은 되돌릴 수 없습니다.</p>
                <div className="button-group">
                  <button onClick={handleWithdraw} className="primary-button inline-button">탈퇴하기</button>
                  <button onClick={() => {
                    setShowDeleteModal(false);
                    setDeleteWarning('');
                  }} className="secondary-button inline-button">취소</button>
                </div>
              </div>
              )}
              <div className={`sidebar ${isSidebarCollapsed ? 'collapsed' : ''}`}>
                {isLogin && !showDeleteModal && (
                  <BlockNavbar
                    blocks={['전체 보기', '1', '2', '3', '4', '5']}
                    selectedBlock={selectedBlock}
                    setSelectedBlock={setSelectedBlock}
                    isSidebarCollapsed={isSidebarCollapsed}
                    activeBlocks={activeBlocks}
                    onToggleActivation={handleToggleActivation}
                  />
                )}
              </div>
            </>
          ) : (
            <>
              <h1 className='main-text'>{isLoginView ? 'LOG IN' : 'SIGN UP'}</h1>
              {isLoginView ? (
                <form onSubmit={handleLogin}>
                  <div className="form-group">
                    <label htmlFor="username">ID</label>
                    <input
                      type="text"
                      id="username"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      required
                      placeholder='Enter your ID'
                    />
                  </div>
                  <div className="form-group">
                    <label htmlFor="password">PW</label>
                    <input
                      type="password"
                      id="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                      placeholder='Enter your PW'
                    />
                  </div>
                  <button type="submit" disabled={loading} className="primary-button">
                    {loading ? '로그인 중...' : '로그인'}
                  </button>
                </form>
              ) : (
                <form onSubmit={handleRegister}>
                  <div className="form-group">
                    <label htmlFor="username">ID</label>
                    <input
                      type="text"
                      id="username"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      required
                      placeholder='Enter your ID'
                    />
                  </div>
                  <div className="form-group">
                    <label htmlFor="password">PW</label>
                    <input
                      type="password"
                      id="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                      placeholder='Enter your PW'
                    />
                  </div>
                  <div className="form-group">
                    <label htmlFor="district">DISTRICT</label>
                    <input
                      type="text"
                      id="district"
                      value={district}
                      onChange={(e) => setDistrict(e.target.value)}
                      required
                      placeholder='Ex. 강남구'
                    />
                  </div>
                  <button type="submit" disabled={loading} className="primary-button">
                    {loading ? '실행 중...' : '회원가입'}
                  </button>
                </form>
              )}
              {loading && <p className="load-message">처리 중입니다. 잠시만 기다려 주세요...</p>}
              {error && <p className="error-message">{error}</p>}
              <div className="auth-links">
                <button
                  onClick={() => {
                    setIsLoginView(!isLoginView);
                    setError('');
                    setUsername('');
                    setPassword('');
                    setDistrict('');
                  }}
                  className="secondary-button"
                >
                  {isLoginView ? '계정이 없으신가요?' : '이미 계정이 있으신가요?'}
                </button>
              </div>
            </>
          )}
        </div>
        <div className="main-contents">
          {isLogin ? (
            <>
              <ToastContainer
                position="top-right"
                autoClose={5000}
                hideProgressBar={false}
                closeOnClick={true}
                pauseOnHover={true}
                className="custom-toast-container"
                toastClassName="custom-toast"
              />
              {showWeather && <WeatherComponent />}
              {showAlerts && <AlertComponent 
                                alerts={alerts} 
                                setAlerts={setAlerts}
                                setUnreadAlerts={setUnreadAlerts}
                              />}
              {selectedBlock === '전체 보기' ? (
                <MapComponent />
              ) : (
                <DetailComponent
                  block={selectedBlock}
                  onActivate={handleToggleActivation}
                  isActive={activeBlocks.includes(selectedBlock)}
                />
              )}
            </>
          ) : (
            <InfoComponent />
          )}
        </div>
      </div>
      {isLogin && (
        <div className="icons-container">
          <div className="weather-icon">
            <button 
              onClick={handleWeatherClick} 
              style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}
            >
              <img src={weatherIcon} alt="Weather" style={{ pointerEvents: 'none' }} />
            </button>
          </div>
          <div className="alert-icon">
            <button 
              onClick={handleAlertClick} 
              style={{ 
                background: 'none', 
                border: 'none', 
                cursor: 'pointer', 
                padding: 0,
                position: 'relative'
              }}
            >
              <img src={alertIcon} alt="Alert" style={{ pointerEvents: 'none' }} />
              {unreadAlerts > 0 && (
                <span>
                  {unreadAlerts}
                </span>
              )}
            </button>
          </div>
        </div>
      )}
    </>
  );
}

export default App;