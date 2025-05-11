from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.utils.dateparse import parse_datetime
from django.db import IntegrityError
from .models import Robot, RobotLog, RobotRepair, LogEntry
from drain.models import Drain
from drain.serializers import DrainSerializer
import json
from datetime import timezone
import logging
from .serializers import RobotSerializer

logger = logging.getLogger(__name__)

# 로봇 정보를 반환하는 함수
@api_view(['GET'])
def get_robot_info(request, robot_id):
    try:
        # 로봇 객체 가져오기
        robot = get_object_or_404(Robot, id=robot_id)
        
        # 로봇 데이터를 직렬화하여 반환
        serializer = RobotSerializer(robot)
        return Response(serializer.data, status=200)
    
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
def receive_log(request, robot_id):
    try:
        log_data = json.loads(request.body)
        
        # 타임스탬프 처리
        timestamp = parse_datetime(log_data.get('timestamp'))
        if not timestamp:
            timestamp = timezone.now()  # 타임스탬프가 없거나 잘못된 경우 현재 시간 사용
        
        LogEntry.objects.create(
            robot_id=robot_id,
            timestamp=timestamp,
            data=log_data
        )

        logger.info(f"Robot {robot_id} log received: {log_data}")

        send_reach_info(log_data)

        return JsonResponse({'message': '로그를 성공적으로 받았습니다.', "data": log_data}, status=status.HTTP_201_CREATED)
    
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON format for robot {robot_id}")
        return JsonResponse({'error': '유효하지 않은 JSON형식입니다.'}, status=status.HTTP_400_BAD_REQUEST)
    except IntegrityError as e:
        logger.error(f"Database integrity error for robot {robot_id}: {str(e)}")
        return JsonResponse({'error': '데이터베이스 무결성 오류가 발생했습니다.'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Unexpected error for robot {robot_id}: {str(e)}")
        return JsonResponse({'error': '예기치 못한 오류가 발생했습니다.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
def send_reach_info(info):
    response_data = {
        'arrive': True,
        'id': info.get('node_id')
    }
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "drain_updates",
        {
            "type": "drain_update",
            "message": response_data
        }
    )


# 로봇의 배수구 탐색 큐를 저장하는 함수
@api_view(['POST'])
def SelectDrain(request):
    try:
        data = json.loads(request.body)
        robot_id = data.get('robot_id')
        drain_ids = data.get('drain_ids', [])
        
        # 로봇 인스턴스 가져오기
        robot = Robot.objects.get(id=robot_id)
        
        # 드레인 ID 리스트를 JSON 문자열로 변환
        drain_queue_str = json.dumps(drain_ids)
        
        # 로봇의 selected_drain 필드 업데이트
        robot.selected_drain = drain_queue_str
        robot.save()
        
        return JsonResponse({"message": "배수구 탐색 큐가 성공적으로 저장되었습니다."}, status=201)
    except Robot.DoesNotExist:
        return JsonResponse({"error": "해당 ID의 로봇을 찾을 수 없습니다."}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
    
# 프론트에서 요청 예시    
# fetch('http://i12a204.p.ssafy.io:8000/robot_info/select-drain/', {
#     method: 'POST',
#     headers: {
#         'Content-Type': 'application/json',
#     },
#     body: JSON.stringify({
#         robot_id: 1,
#         drain_ids: [1, 3, 2, 5, 4]
#     }),
# })
# .then(response => response.json())
# .then(data => console.log(data))
# .catch((error) => console.error('Error:', error));    


@api_view(['GET'])
def get_queue(request, robot_id):
    try:
        # 로봇 객체 조회
        robot = get_object_or_404(Robot, pk=robot_id)
        
        # selected_drain이 None이 아닌 경우에만 JSON 파싱
        if robot.selected_drain:
            drain_queue = json.loads(robot.selected_drain)
        else:
            return Response({
                'robot_id': robot.pk,
                'queue_data': [],
                'drain_details': []
            })    
            # 큐에 있는 배수구들의 정보 조회
        drains = Drain.objects.filter(id__in=drain_queue).select_related('block')
        serializer = DrainSerializer(drains, many=True)
            
        return Response({
            'robot_id': robot.pk,
            'queue_data': drain_queue,
            'drain_details': serializer.data
        })
            
    except json.JSONDecodeError:
        return Response({
            'error': 'Invalid queue data format'
        }, status=400)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=500)

    

    