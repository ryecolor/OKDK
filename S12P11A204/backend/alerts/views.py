from django.shortcuts import render
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from urllib.parse import unquote
from datetime import datetime, timedelta
from .models import WeatherData

def get_wind_direction(degree):
    directions = ['북', '북동', '동', '남동', '남', '남서', '서', '북서']
    index = round(degree / 45) % 8
    return directions[index]

def get_sky_condition(code):
    conditions = {1: '맑음', 3: '구름많음', 4: '흐림'}
    return conditions.get(code, '알 수 없음')

def get_precipitation_type(code):
    types = {0: '없음', 1: '비', 2: '비/눈', 3: '눈', 4: '소나기'}
    return types.get(code, '알 수 없음')

def calculate_feels_like(temperature, wind_speed):
    return round(13.12 + 0.6215 * temperature - 11.37 * (wind_speed ** 0.16) + 0.3965 * temperature * (wind_speed ** 0.16), 1)

def get_latest_base_time():
    now = datetime.now()
    current_hour = int(now.strftime('%H'))
    
    if current_hour < 2:
        return (now - timedelta(days=1)).strftime("%Y%m%d"), "2300"
    elif current_hour < 5:
        return now.strftime("%Y%m%d"), "0200"
    elif current_hour < 8:
        return now.strftime("%Y%m%d"), "0500"
    elif current_hour < 11:
        return now.strftime("%Y%m%d"), "0800"
    elif current_hour < 14:
        return now.strftime("%Y%m%d"), "1100"
    elif current_hour < 17:
        return now.strftime("%Y%m%d"), "1400"
    elif current_hour < 20:
        return now.strftime("%Y%m%d"), "1700"
    elif current_hour < 23:
        return now.strftime("%Y%m%d"), "2000"
    else:
        return now.strftime("%Y%m%d"), "2300"

def try_get_weather():
    now = datetime.now()
    print(f"현재 시각: {now.strftime('%Y-%m-%d %H:%M')}")
    
    base_date, base_time = get_latest_base_time()
    print(f"요청하는 시각: {base_date} {base_time}")
    
    api_url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
    api_key = unquote(settings.WEATHER_API_KEY)
    
    params = {
        "serviceKey": api_key,
        "numOfRows": "350",
        "pageNo": "1",
        "dataType": "JSON",
        "base_date": base_date,
        "base_time": base_time,
        "nx": "37",
        "ny": "127"
    }
    
    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if 'response' in data and 'body' in data['response'] and 'items' in data['response']['body']:
            items = data['response']['body']['items']['item']
            
            weather_data = {
                'current': {},
                'after_3h': {},
                'after_24h': {},
            }
            
            for item in items:
                forecast_date = item['fcstDate']
                forecast_time = item['fcstTime']
                category = item['category']
                value = item['fcstValue']

                forecast_datetime = datetime.strptime(f"{forecast_date} {forecast_time}", "%Y%m%d %H%M")
                time_diff = forecast_datetime - now

                if time_diff.days == 0 and time_diff.seconds < 3600:
                    target = 'current'
                elif time_diff.days == 0 and 3*3600 <= time_diff.seconds < 4*3600:
                    target = 'after_3h'
                elif time_diff.days == 1 and time_diff.seconds < 3600:
                    target = 'after_24h'
                else:
                    continue

                if category == 'TMP':
                    weather_data[target]['temperature'] = float(value)
                elif category == 'RN1':
                    weather_data[target]['precipitation'] = value
                elif category == 'REH':
                    weather_data[target]['humidity'] = int(value)
                elif category == 'WSD':
                    weather_data[target]['wind_speed'] = float(value)
                elif category == 'VEC':
                    weather_data[target]['wind_direction'] = get_wind_direction(float(value))
                elif category == 'SKY':
                    weather_data[target]['sky_condition'] = get_sky_condition(int(value))
                elif category == 'PTY':
                    weather_data[target]['precipitation_type'] = get_precipitation_type(int(value))

            required_fields = ['temperature', 'humidity', 'wind_speed', 'sky_condition']
            all_data_present = all(
                all(field in data for field in required_fields)
                for data in weather_data.values()
                if data
            )
            
            if all_data_present:
                for target in weather_data:
                    if 'temperature' in weather_data[target] and 'wind_speed' in weather_data[target]:
                        weather_data[target]['feels_like'] = calculate_feels_like(
                            weather_data[target]['temperature'], 
                            weather_data[target]['wind_speed']
                        )
                weather_data['base_date'] = base_date
                weather_data['base_time'] = base_time
                weather_data['current_time'] = now
                return weather_data
                            
        return None
        
    except requests.RequestException:
        return None

@api_view(['GET'])
def get_weather(request):
    """데이터베이스에서 저장된 날씨 데이터 조회"""
    try:
        # 각 시간대별 최신 데이터 조회
        current_data = WeatherData.objects.get(forecast_type='current')
        after_3h_data = WeatherData.objects.get(forecast_type='after_3h')
        after_24h_data = WeatherData.objects.get(forecast_type='after_24h')

        # 응답 데이터 구성
        weather_data = {
            'current': {
                'temperature': current_data.temperature,
                'precipitation': current_data.precipitation,
                'humidity': current_data.humidity,
                'wind_speed': current_data.wind_speed,
                'wind_direction': current_data.wind_direction,
                'sky_condition': current_data.sky_condition,
                'precipitation_type': current_data.precipitation_type,
                'feels_like': current_data.feels_like,
            },
            'after_3h': {
                'temperature': after_3h_data.temperature,
                'precipitation': after_3h_data.precipitation,
                'humidity': after_3h_data.humidity,
                'wind_speed': after_3h_data.wind_speed,
                'wind_direction': after_3h_data.wind_direction,
                'sky_condition': after_3h_data.sky_condition,
                'precipitation_type': after_3h_data.precipitation_type,
                'feels_like': after_3h_data.feels_like,
            },
            'after_24h': {
                'temperature': after_24h_data.temperature,
                'precipitation': after_24h_data.precipitation,
                'humidity': after_24h_data.humidity,
                'wind_speed': after_24h_data.wind_speed,
                'wind_direction': after_24h_data.wind_direction,
                'sky_condition': after_24h_data.sky_condition,
                'precipitation_type': after_24h_data.precipitation_type,
                'feels_like': after_24h_data.feels_like,
            },
            'base_date': current_data.base_date,
            'base_time': current_data.base_time,
        }
        
        return Response(weather_data)
        
    except WeatherData.DoesNotExist:
        return Response(
            {"error": "날씨 데이터가 없습니다."}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['GET'])
def initialize_weather_data(request):
    """초기 날씨 데이터 수집 및 저장"""
    weather_data = try_get_weather()
    
    if weather_data:
        # 각 시간대별 데이터 저장
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
        
        return Response({"message": "날씨 데이터가 성공적으로 저장되었습니다."})
    
    return Response(
        {"error": "날씨 데이터를 가져오는데 실패했습니다."}, 
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
