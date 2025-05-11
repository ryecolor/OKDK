from background_task import background
from django.utils import timezone
from .models import WeatherData
from .views import try_get_weather
import logging

# 로깅 설정
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)  # 로깅 레벨 설정

@background(schedule=3600)
def update_weather_data():
    current_time = timezone.now()
    print(f"=== 날씨 데이터 업데이트 체크: {current_time} ===")
    logger.info(f"날씨 데이터 업데이트 체크 시작: {current_time}")
    
    weather_data = try_get_weather()
    
    if weather_data:
        print(f"데이터 수신 성공: {weather_data['base_date']} {weather_data['base_time']}")
        logger.info(f"날씨 데이터 수신 성공: {weather_data['base_date']} {weather_data['base_time']}")
        
        for forecast_type in ['current', 'after_3h', 'after_24h']:
            if forecast_type in weather_data and weather_data[forecast_type]:
                data = weather_data[forecast_type]
                WeatherData.objects.update_or_create(
                    forecast_type=forecast_type,
                    defaults={
                        'temperature': data['temperature'],
                        'precipitation': data.get('precipitation', '0'),
                        'humidity': data['humidity'],
                        'wind_speed': data['wind_speed'],
                        'wind_direction': data['wind_direction'],
                        'sky_condition': data['sky_condition'],
                        'precipitation_type': data['precipitation_type'],
                        'feels_like': data['feels_like'],
                        'base_date': weather_data['base_date'],
                        'base_time': weather_data['base_time']
                    }
                )
                print(f"{forecast_type} 데이터 업데이트 완료")
                logger.info(f"{forecast_type} 데이터 업데이트 완료")
        return True
    return False
