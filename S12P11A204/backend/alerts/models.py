# alerts/models.py
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import logging

logger = logging.getLogger(__name__)

class WeatherData(models.Model):
    FORECAST_TYPE_CHOICES = [
        ('current', '현재'),
        ('after_3h', '3시간 후'),
        ('after_24h', '24시간 후'),
    ]

    forecast_type = models.CharField(max_length=10, choices=FORECAST_TYPE_CHOICES)
    temperature = models.FloatField()
    precipitation = models.CharField(max_length=10)
    humidity = models.IntegerField()
    wind_speed = models.FloatField()
    wind_direction = models.CharField(max_length=10)
    sky_condition = models.CharField(max_length=10)
    precipitation_type = models.CharField(max_length=10)
    feels_like = models.FloatField()
    base_date = models.CharField(max_length=8)
    base_time = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.forecast_type} - {self.base_date} {self.base_time}"
    
    def save(self, *args, **kwargs):
        logger.info(f"Save method called - precipitation_type: {self.precipitation_type}")  # 디버깅용 로그
        super().save(*args, **kwargs)
        
        # precipitation_type이 '없음'이 아닐 때 알림 전송
        if self.precipitation_type != '없음':
            try:
                channel_layer = get_channel_layer()
                forecast_type_names = {
                    'current': '현재',
                    'after_3h': '3시간 후',
                    'after_24h': '24시간 후'
                }
                message = f"{forecast_type_names.get(self.forecast_type)} {self.precipitation_type} 예보"
                
                async_to_sync(channel_layer.group_send)(
                    "alerts",
                    {
                        "type": "send_notification",
                        "message": message
                    }
                )
                logger.info(f"알림 전송 성공 (모델): {message}")
            except Exception as e:
                logger.error(f"알림 전송 실패 (모델): {str(e)}")
