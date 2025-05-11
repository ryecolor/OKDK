import React, { useState, useEffect } from 'react';
import axios from 'axios';
import '../styles/Weather.css';

const Weather = () => {
  const [weatherData, setWeatherData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchWeatherData = async () => {
      try {
        const response = await axios.get('http://i12a204.p.ssafy.io:8000/api/alerts/weather/');
        setWeatherData(response.data);
      } catch (error) {
        console.error('날씨 데이터 가져오기 실패:', error);
        setError('날씨 정보를 불러오는 데 실패했습니다. 잠시 후 다시 시도해 주세요.');
      }
    };

    fetchWeatherData();
  }, []);

  if (error) return <div className="error">{error}</div>;
  if (!weatherData) return null;

  const shouldHighlight = (precipitation, precipitationType) => {
    return precipitation !== "0" || (precipitationType === "눈" || precipitationType === "비");
  };

  return (
    <div className="weather-section">
      <h5>· 강남구 날씨</h5>
      <div className="weather-table">
        <table>
          <thead>
            <tr>
              <th></th>
              <th>현재</th>
              <th>3시간 후</th>
              <th>내일</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>기온</td>
              <td>{weatherData.current.temperature}°C</td>
              <td>{weatherData.after_3h.temperature}°C</td>
              <td>{weatherData.after_24h.temperature}°C</td>
            </tr>
            <tr>
              <td>체감 온도</td>
              <td>{weatherData.current.feels_like}°C</td>
              <td>{weatherData.after_3h.feels_like}°C</td>
              <td>{weatherData.after_24h.feels_like}°C</td>
            </tr>
            <tr>
              <td>습도</td>
              <td>{weatherData.current.humidity}%</td>
              <td>{weatherData.after_3h.humidity}%</td>
              <td>{weatherData.after_24h.humidity}%</td>
            </tr>
            <tr>
            <td>강수량</td>
              <td className={shouldHighlight(weatherData.current.precipitation, weatherData.current.precipitation_type) ? 'highlight' : ''}>
                {weatherData.current.precipitation_type === "없음" ? "0" : weatherData.current.precipitation}mm
              </td>
              <td className={shouldHighlight(weatherData.after_3h.precipitation, weatherData.after_3h.precipitation_type) ? 'highlight' : ''}>
                {weatherData.after_3h.precipitation_type === "없음" ? "0" : weatherData.after_3h.precipitation}mm
              </td>
              <td className={shouldHighlight(weatherData.after_24h.precipitation, weatherData.after_24h.precipitation_type) ? 'highlight' : ''}>
                {weatherData.after_24h.precipitation_type === "없음" ? "0" : weatherData.after_24h.precipitation}mm
              </td>
            </tr>
            <tr>
              <td>강수 형태</td>
              <td className={shouldHighlight(weatherData.current.precipitation, weatherData.current.precipitation_type) ? 'highlight' : ''}>
                {weatherData.current.precipitation_type}
              </td>
              <td className={shouldHighlight(weatherData.after_3h.precipitation, weatherData.after_3h.precipitation_type) ? 'highlight' : ''}>
                {weatherData.after_3h.precipitation_type}
              </td>
              <td className={shouldHighlight(weatherData.after_24h.precipitation, weatherData.after_24h.precipitation_type) ? 'highlight' : ''}>
                {weatherData.after_24h.precipitation_type}
              </td>
            </tr>
            <tr>
              <td>하늘 상태</td>
              <td>{weatherData.current.sky_condition}</td>
              <td>{weatherData.after_3h.sky_condition}</td>
              <td>{weatherData.after_24h.sky_condition}</td>
            </tr>
            <tr>
              <td>풍속</td>
              <td>{weatherData.current.wind_speed}m/s</td>
              <td>{weatherData.after_3h.wind_speed}m/s</td>
              <td>{weatherData.after_24h.wind_speed}m/s</td>
            </tr>
            <tr>
              <td>풍향</td>
              <td>{weatherData.current.wind_direction}</td>
              <td>{weatherData.after_3h.wind_direction}</td>
              <td>{weatherData.after_24h.wind_direction}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Weather;
