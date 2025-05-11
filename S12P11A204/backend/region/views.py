from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import District, Block, BlockCondition
from .serializers import BlockConditionSerializer
from drain.models import DrainCondition , Drain
from robot_info.models import Robot
from collections import deque
import json
import base64
import logging

# 로깅 설정
logger = logging.getLogger(__name__)

#베이스 노드
START_NODE_NUMBER = 6
# 그래프 생성
graph = {
    START_NODE_NUMBER: [(7,0)],
    7: [(8,1), (9,4)],
    8: [(9,2)],
    9: [(START_NODE_NUMBER,3)]
}

def preprocessInput(input):
    # 선택 노드 리스트 맨 앞, 맨 뒤에 시작노드 추가
    input.insert(0, START_NODE_NUMBER)
    input.append(START_NODE_NUMBER)
    return input

# 시작점, 도착점을 기준으로 최단경로를 찾아 path 기록
def BFS(startNode, endNode , inputQueue):
    
    # 시작 노드와 시작노드 to 시작노드까지의 경로 저장
    q = deque([(startNode, [])])
    # visited 기록용, 고유값저장 set
    visitedNodes = set()
    
    while q:
        # q 의 front : 현재노드, 현재까지의 경로
        nowNode, path = q.popleft()
        
        # 도착점에 도착한 경우
        if nowNode == endNode:
            # 시작점부터 도착점까지의 최단 path 반환
            return path

        # 만약 방문한 노드이면 스킵
        if nowNode in visitedNodes:
            continue

        # 현재노드를 visited 처리
        visitedNodes.add(nowNode)

        # graph 에서 현재노드와 연결된 값들을 반복문으로 뽑기
        for nextNode, edgeNum in graph[nowNode]:
            if nextNode in visitedNodes:
                continue
            
            # 다음노드, 현재까지의 경로를 저장
            # 만약 다음노드가 큐에 있는 것 = 체크 하는 노드라면 True
            # 다음노드가 큐에 없다면 = 지나치는 노드라면 False
            # 복귀 엣지는 항상 True
            if nextNode in inputQueue:
                q.append((nextNode, path + [(edgeNum, True)]))
            else:
                q.append((nextNode, path + [(edgeNum, False)]))
            
    # 경로가 없을 경우 None 반환
    return None



# 입력 받은 node input 을 기준으로 from ~ to 를 각각 계산하여 최종 경로에 추가
def findPath(input):
    # 최종 경로
    totalPath = []
    
    # node input 를 시작점, 도착점으로 각각 나누어 BFS 돌리기
    for i in range(len(input) - 1):
        startNode, endNode = input[i], input[i + 1]
        path = BFS(startNode, endNode, input)

        if path is None:
            raise ValueError(f"{startNode} 에서 {endNode} 로 가는 경로가 없습니다")

        # extend 로 경로누적
        totalPath.extend(path)

    return totalPath

# 로봇을 배정하고 배수구 탐색 큐를 저장하는 함수
@api_view(['POST'])
def SelectRobotAndDrain(request):
    try:
        data = json.loads(request.body)
        district_id = data.get('district_id')
        block_id = data.get('block_id')
        drain_ids = data.get('drain_ids', [])
        
        # 해당 구역 확인
        try:
            district = District.objects.get(id=district_id)
        except District.DoesNotExist:
            return JsonResponse({
                "error": "해당 구역을 찾을 수 없습니다."
            }, status=404)
        
        # 같은 district_id와 block_id를 가진 로봇이 이미 존재하는지 확인
        if Block.objects.filter(district=district, selected_robot__contains=str(block_id)).exists():
            return JsonResponse({
                "error": "해당 로봇이 이미 이 구역의 블록에 배정되어 있습니다."
            }, status=400)

        # 사용 가능한 로봇 찾기
        available_robot = Robot.objects.filter(
            district=district,
            is_robot_available=True
        ).order_by('?').first()

        if not available_robot:
            return JsonResponse({
                "error": "사용 가능한 로봇이 없습니다."
            }, status=404)
            
        # 드레인 ID 리스트를 JSON 문자열로 변환하여 저장
        drain_queue_str = json.dumps(drain_ids)
        
        inputQueue = preprocessInput(drain_ids)
        result = findPath(inputQueue)

        # 로봇 상태 업데이트 (SelectDrain 로직 통합)
        available_robot.selected_drain = drain_queue_str
        available_robot.is_robot_available = False
        available_robot.robot_unavailable_reason = "주행 중"
        available_robot.save()

        # 블록의 selected_robot 필드 업데이트
        block = Block.objects.get(id=block_id, district=district)
        block.selected_robot = str(available_robot.id)  # robot_id를 문자열로 저장
        block.save()

        # WebSocket을 통해 메시지 전송
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "robot",
            {
                "type": "robot_assignment",
                "message": {
                    "robot_id": available_robot.id,
                    "assigned_drains": drain_ids,
                    # "route" : result
                }
            }
        )

        return JsonResponse({
            "message": "로봇이 성공적으로 배정되었고 배수구 탐색 큐가 저장되었습니다.",
            "robot_id": available_robot.id,
            "assigned_drains": drain_ids
        }, status=201)
        
    except Exception as e:
        return JsonResponse({
            "error": str(e)
        }, status=400)

    
# 데이터 전송 형식(json)
# {
#     "district_id": 1,
#     "block_id": 1,
#     "drain_ids": [1, 2, 3]
# }


@api_view(['GET'])
def block_condition(request, block_id):
    block = get_object_or_404(Block, id=block_id)
    
    if request.method == 'GET':
        conditions = BlockCondition.objects.filter(block=block).order_by('-check_date')
        serializer = BlockConditionSerializer(conditions, many=True)
        return Response(serializer.data)
    
    return Response(status=405)


@api_view(['POST'])
def deactivate_robot(request, block_id):
    try:
        # 블록 정보 가져오기
        block = get_object_or_404(Block, id=block_id)
        robot = get_object_or_404(Robot, id=block.selected_robot)

        # 블록에 할당된 로봇 가져오기
        robot_id = block.selected_robot
        
        if not robot_id:
            return Response({'error': '이 블록에 할당된 로봇이 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 로봇 상태 업데이트
        robot.is_robot_available = True
        robot.robot_unavailable_reason = None
        robot.selected_drain = None
        robot.save()
        
        # 블록 상태 업데이트
        block.selected_robot = None
        block.save()
        
        # 배수구 상태 점수 업데이트
        get_drain_score(block_id)  

        # WebSocket을 통해 메시지 전송
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "robot",
            {
                "type": "robot_deactivate",
                "message": {
                    "command" : "deactivate",
                    "robot_id": robot.id,
                }
            }
        )
                
        return Response({
            'message': '로봇이 성공적으로 정지되었습니다.',
            'robot_id': robot.id,
            'block_id': block_id
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_200_OK)
    


@api_view(['GET'])
def get_flood_images(request):
    blocks = Block.objects.all()
    flood_images = {}

    for block in blocks:
        if block.Flood_Image:
            # 이미지 파일을 열고 Base64로 인코딩
            image_data = block.Flood_Image.read()
            encoded_image = base64.b64encode(image_data).decode('utf-8')
            flood_images[block.name] = f"data:image/png;base64,{encoded_image}"
        else:
            flood_images[block.name] = None

    return JsonResponse({
        "flood_images": flood_images
    })



# 배수구 상태 점수를 계산하는 하고 조회하는 함수
def get_drain_score(block_id):
    try:
        # block_id에 해당하는 drain을 필터링
        drains = Drain.objects.filter(block_id=block_id)
        if not drains:
            return Response({"message": "No drain found for the given block_id."}, status=status.HTTP_404_NOT_FOUND)

        total_score = 0
        id_count = 0

        for drain in drains:
            recent_condition = (
                DrainCondition.objects.filter(drain_id=drain.id)
                .order_by('-check_date')  # check_date 기준으로 내림차순 정렬
                .first()
            )
            score = convert_score(recent_condition.condition)
            id_count += 1
            total_score += score

        average_score = total_score / id_count

        # 소수점 2자리까지 반올림
        average_score_rounded = round(average_score, 2)

        BlockCondition.objects.create(
            block_id = block_id,
            condition = average_score_rounded
        )

        return Response({"score": "상태 점수 업데이트 성공"}, status=status.HTTP_200_OK)
        
    except Exception as e:
        # 예외 발생 시 에러 메시지 반환
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    


# 배수구 상태를 숫자로 변경하는 함수
def convert_score(condition):
    if '우수' in condition or 'good' in condition:
        return 100
    elif '양호' in condition or 'medium' in condition:
        return 50
    elif '위험' in condition or 'bad' in condition:
        return 0
    else:
        return 50  # 기본값