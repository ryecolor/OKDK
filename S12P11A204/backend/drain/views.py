from django.shortcuts import get_object_or_404
from django.core.serializers import serialize
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from django.conf import settings
from django.http import JsonResponse
from django.db.models import Max
from .models import Drain, DrainCondition, DrainRepair
from robot_info.models import Robot
from robot_info.serializers import RobotSerializer
from region.models import Block
from .serializers import DrainSerializer, DrainConditionSerializer 
from region.serializers import BlockSerializer
import boto3
import uuid
import base64
import json
import logging
from datetime import datetime, timedelta, timezone
from django.db.models import Max

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BlockDrainListView(APIView):
    def get(self, request, block_id):
        block = get_object_or_404(Block, id=block_id)
        drains = Drain.objects.filter(block_id=block_id).select_related('block')
        serializer = DrainSerializer(drains, many=True)
        return Response(serializer.data)


# 해당 블록에 할당된 로봇 정보를 조회하는 함수
@api_view(['GET'])
def selected_robot(request, block_id):
    block = get_object_or_404(Block, id=block_id)
    serializer = BlockSerializer(block)
    return Response(serializer.data)

# 배수구 상태를 변경하는 함수
def map_condition(condition):
    condition = condition.lower()
    if '우수' in condition or 'good' in condition:
        return '우수'
    elif '양호' in condition or 'medium' in condition:
        return '양호'
    elif '위험' in condition or 'bad' in condition:
        return '위험'
    else:
        return '양호'  # 기본값

@api_view(['POST'])
def receive_img(request, block_id, drain_id):
    try:
        data = json.loads(request.body)
        base64_img = data.get('image')
        drain_condition = data.get('condition')
        district_id = data.get('district_id')
        robot_id = data.get('robot_id')

        if not all([base64_img, drain_condition, district_id, robot_id]):
            return Response({'error': '필수 데이터가 누락되었습니다.'}, status=400)

        mapped_condition = map_condition(drain_condition)

        # Block과 Drain 객체 가져오기
        block = get_object_or_404(Block, id=block_id)
        drain = get_object_or_404(Drain, id=drain_id, block=block)

        # 이미지 데이터 처리
        image_data = base64.b64decode(base64_img)
        file_name = f"drain_{drain_id}_{uuid.uuid4()}.jpg"

        # S3에 이미지 업로드
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )

        s3_client.put_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=file_name,
            Body=image_data,
            ContentType='image/jpeg'
        )

        # S3 URL 생성
        s3_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{file_name}"

        # Drain 모델 업데이트
        drain.state_img_url = s3_url
        drain.save()

        # DrainCondition 생성
        DrainCondition.objects.create(
            drain=drain,
            condition=mapped_condition
        )

        # 조건이 위험일 경우 DrainRepair에 조치 필요 내역 추가
        if mapped_condition.lower() == '위험':
            create_drain_repair(drain)

        # WebSocket을 통해 로봇 상태 업데이트 전송
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "drain_updates",  # 이 그룹 이름은 consumer에서 사용할 것입니다
            {
                "type": "drain_update",
                "message": {
                    "arrive": False,
                    "id" : drain_id,
                    "condition": mapped_condition,
                }
            }
        )

        # 큐 업데이트
        if process_queue_update(district_id, robot_id, drain_id, block_id):
            return Response({
                'state_img_url': s3_url,
                'condition': mapped_condition,
                'check_date': datetime.now(timezone(timedelta(hours=9)))
            }, status=200)

        return Response({'error': '큐 업데이트 실패'}, status=500)

    except Exception as e:
        return Response({'error': str(e)}, status=500)


# process_queue_update 및 create_drain_repair 함수는 이전과 동일하게 유지

def process_queue_update(district_id, robot_id, drain_id, block_id):
    """큐 업데이트를 처리하는 내부 함수"""
    try:
        # district_id와 robot_id가 일치하는 로봇 조회
        robot = Robot.objects.get(id=robot_id, district__id=district_id)
        block = Block.objects.get(id=block_id, district__id=district_id)
        
        if robot.selected_drain:
            drain_queue = json.loads(robot.selected_drain)
            
            if drain_id in drain_queue:
                drain_queue.remove(drain_id)
                
                # 큐가 비어 있으면 로봇을 사용 가능 상태로 전환
                robot.selected_drain = json.dumps(drain_queue) if drain_queue else None
                
                if not drain_queue:
                    robot.is_robot_available = True
                    robot.robot_unavailable_reason = None
                    block.selected_robot = None
                
                # # WebSocket을 통해 로봇에게 정지 명령 전송
                #     channel_layer = get_channel_layer()
                #     async_to_sync(channel_layer.group_send)(
                #         f"robot_{robot_id}",
                #         {
                #             "type": "robot_deactivate",
                #             "message": {
                #                 "content" : "Queue is empty. Stop the robot.",
                #                 "robot_id": robot_id
                #             }
                #         }
                #     )
                robot.save()
                block.save()
                return True
        
        return False
    
    except Robot.DoesNotExist:
        return False

def create_drain_repair(drain):
    """DrainRepair 모델에 조치 필요 내역을 추가하는 함수"""   
    DrainRepair.objects.create(
        drain=drain,
        repair_result='위험 상태 감지. 조치 필요.'
    )

# 누적 배수구 상태를 조회
@api_view(['GET'])
def drain_condition(request, block_id, drain_id):
    block = get_object_or_404(Block, id=block_id)
    drain = get_object_or_404(Drain, id=drain_id, block=block)
    
    if request.method == 'GET':
        conditions = DrainCondition.objects.filter(drain=drain).order_by('-check_date')
        serializer = DrainConditionSerializer(conditions, many=True)
        return Response(serializer.data)
    
    return Response(status=405)

# '우수', '양호', '위험'
# 배수구 상태를 수정하는 함수
@api_view(['PUT'])
def state_correction(request, block_id, drain_id, draincondition_id):
    block = get_object_or_404(Block, id=block_id)
    drain = get_object_or_404(Drain, id=drain_id, block=block)
    drain_condition = get_object_or_404(DrainCondition, id=draincondition_id, drain=drain)

    if request.method == 'PUT':
        serializer = DrainConditionSerializer(drain_condition, data=request.data, partial=True)
        if serializer.is_valid():
            if 'condition' in request.data:
                condition = request.data['condition']
                if condition not in ['우수', '양호', '위험']:
                    return Response({'error': '유효하지 않은 상태입니다. 우수, 양호, 위험 중 하나를 선택하세요.'}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@csrf_exempt    
def get_latest_image(request, block_id, drain_id):
    try:
        logger.debug(f"Attempting to fetch latest condition for block_id: {block_id}, drain_id: {drain_id}")
        
        latest_condition = Drain.objects.filter(
            block_id=block_id,
            id=drain_id
        ).first()  # 첫 번째 객체 선택
        
        logger.info(f"Query result: {latest_condition}")

        if latest_condition and hasattr(latest_condition, 'state_img_url'):
            logger.info(f"Found state_img_url: {latest_condition.state_img_url}")
            return JsonResponse({
                'state_img_url': latest_condition.state_img_url
            })
        else:
            logger.warning("No image found or invalid drain")
            return JsonResponse({'error': 'No image found or invalid drain'}, status=404)
    except Exception as e:
        logger.exception(f"An error occurred: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)