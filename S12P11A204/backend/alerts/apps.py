from django.apps import AppConfig
import psycopg2
import psycopg2.extensions
import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import threading

class AlertsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'alerts'

    def ready(self):
        # from drain.models import DrainRepair, Drain
        import alerts.signals
        
        try:
            conn = psycopg2.connect(
                dbname='postgres',
                user='postgres',
                password='postgres',
                host='db',
                port='5432'
            )
            conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
            
            cursor = conn.cursor()
            cursor.execute("LISTEN weather_change;")
            # cursor.execute("LISTEN drain_repair_change;")
            cursor.execute("LISTEN robot_repair_change;")

            def callback(conn, notify):
                try:
                    if not notify.payload:
                        return
                        
                    data = json.loads(notify.payload)
                    message = ""
                    
                    # 채널별 분기 처리 강화
                    if notify.channel == "weather_change":
                        forecast_type = data.get('forecast_type', 'unknown')
                        precipitation_type = data.get('precipitation_type', '알 수 없음')
                        forecast_type_names = {
                            'current': '현재',
                            'after_3h': '3시간 후',
                            'after_24h': '24시간 후'
                        }
                        message = f"{forecast_type_names.get(forecast_type)} {precipitation_type} 예보☔"
                        
                    # elif notify.channel == "drain_repair_change":
                    #     drain_id = data.get('drain_id')
                    #     try:
                    #         drain = Drain.objects.select_related('block').get(id=drain_id)
                    #         block = drain.block
                    #         drains = Drain.objects.filter(block=block).order_by('id')
                    #         idx = list(drains).index(drain)
                    #         message = f"{block.id}번 블록 {idx}번 배수구 문제 발생👷"
                    #     except Drain.DoesNotExist:
                    #         message = f"{drain_id}번 배수구 문제 발생👷 (블록 정보 없음)"

                        
                    elif notify.channel == "robot_repair_change":
                        message = f"{data.get('robot_id')}번 로봇 {data.get('repair_reason')}🤖"
                        
                    # 메시지 전송 로직
                    if message:
                        channel_layer = get_channel_layer()
                        async_to_sync(channel_layer.group_send)(
                            "alerts",
                            {"type": "send_notification", "message": message}
                        )
                        
                except Exception as e:
                    print(f"Error processing {notify.channel}: {str(e)}")


            def listen():
                while True:
                    conn.poll()
                    while conn.notifies:
                        notify = conn.notifies.pop()
                        callback(conn, notify)

            listener_thread = threading.Thread(target=listen, daemon=True)
            listener_thread.start()
            
        except Exception as e:
            print(f"DB 연결 오류: {str(e)}")