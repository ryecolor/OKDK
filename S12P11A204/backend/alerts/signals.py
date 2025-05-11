# signals.py
# alerts/signals.py
from django.db.models.signals import post_save, post_migrate, pre_save
from django.dispatch import receiver
from .models import WeatherData
from .consumers import AlertConsumer
from drain.models import DrainRepair, Drain
from robot_info.models import RobotRepair
from channels.layers import get_channel_layer
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync
import asyncio
import logging


logger = logging.getLogger(__name__)

@receiver([pre_save, post_save], sender=WeatherData)
def send_weather_alert(sender, instance, **kwargs):
    logger.info(f"Signal triggered - precipitation_type: {instance.precipitation_type}")
    
    try:
        old_instance = WeatherData.objects.get(pk=instance.pk)
        old_precipitation_type = old_instance.precipitation_type
    except WeatherData.DoesNotExist:
        old_precipitation_type = None

    if instance.precipitation_type != '없음' and instance.precipitation_type != old_precipitation_type:
        forecast_type_names = {
            'current': '현재',
            'after_3h': '3시간 후',
            'after_24h': '24시간 후'
        }
        message = f"{forecast_type_names.get(instance.forecast_type)} {instance.precipitation_type} 예보"
        
        channel_layer = get_channel_layer()
        async_to_sync(send_delayed_message)("alerts", message)


@receiver(post_save, sender=DrainRepair)
def drain_repair_alert(sender, instance, created, **kwargs):
    logger.info(f'"DrainRepair" Signal triggered - drain_id: {instance.drain_id}')
    
    if created:
        try:
            drain = Drain.objects.select_related('block').get(id=instance.drain_id)
            block = drain.block
            drains_in_block = Drain.objects.filter(block=block).order_by('id')
            drain_index = list(drains_in_block).index(drain)

            message = f"{block.id}번 블록 {drain_index}번 배수구 문제 발생👷"
            
            channel_layer = get_channel_layer()
            async_to_sync(send_delayed_message)("alerts", message)

        except Drain.DoesNotExist:
            logger.error(f"Drain with id {instance.drain_id} does not exist")
        except Exception as e:
            logger.error(f"Error in drain_repair_alert: {str(e)}")

        

@receiver(post_save, sender=RobotRepair)
def robot_repair_alert(sender, instance, created, **kwargs):
    logger.info(f"RobotRepair Signal triggered - robot_id: {instance.robot_id}")
    
    if created:
        message = f"로봇 {instance.robot_id}번 수리: {instance.repair_reason}"
        channel_layer = get_channel_layer()
        async_to_sync(send_delayed_message)("alerts", message)


async def send_delayed_message(group, message):
    await asyncio.sleep(3)
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        group,
        {
            "type": "send_notification",
            "message": message
        }
    )