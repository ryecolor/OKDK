import React, { useEffect } from 'react';
import '../styles/Alert.css';

const AlertComponent = ({ alerts, setAlerts, setUnreadAlerts }) => {
    useEffect(() => {
        // 알림창이 열리면 모든 알림을 읽음 처리
        const markAllAsRead = () => {
            const updatedAlerts = alerts.map(alert => ({
                ...alert,
                read: true
            }));
            setAlerts(updatedAlerts);
            localStorage.setItem('weatherAlerts', JSON.stringify(updatedAlerts));
            setUnreadAlerts(0);
        };

        markAllAsRead();
    }, []);  // 컴포넌트가 마운트될 때 실행

    return (
        <div className="alert-section">
            <div className="alert-container">
                <div className="alert-box">
                    <h5>· 알림</h5>
                    <div className="alert-list">
                        {alerts.length > 0 ? (
                            alerts.map((alert, index) => (
                                <div key={index} className="alert-item">
                                    <div className="alert-content">
                                        <strong>주요 내용</strong> {alert.message}
                                    </div>
                                    <div className="alert-content">
                                        <strong>시간</strong> {new Date(alert.created_at).toLocaleString()}
                                    </div>
                                </div>
                            ))
                        ) : (
                            <div className="alert-content">알림이 없습니다.</div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AlertComponent;
