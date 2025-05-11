from django.core.management.base import BaseCommand
from alerts.views import try_get_weather
from alerts.models import WeatherData
from alerts.tasks import update_weather_data

class Command(BaseCommand):
    help = '초기 날씨 데이터 수집'

    def handle(self, *args, **options):
        weather_data = try_get_weather()
        
        if weather_data:
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
            self.stdout.write(self.style.SUCCESS('날씨 데이터 초기화 완료'))
            
            # 백그라운드 태스크 등록
            update_weather_data(repeat=3600)
            self.stdout.write(self.style.SUCCESS('백그라운드 태스크 등록 완료'))
        else:
            self.stdout.write(self.style.ERROR('날씨 데이터 초기화 실패'))
