"""
사용법 : findPath() 매개변수로 서버로 넘어온 input 을 넘겨준다
반환값 : 경로 deque
"""


from collections import deque


START_NODE_NUMBER = 6

graph = {
    START_NODE_NUMBER: [(7,0)],
    7: [(8,1), (9,4)],
    8: [(9,2)],
    9: [(START_NODE_NUMBER,3)]
}

# 시작점, 도착점을 기준으로 최단경로를 찾아 path 기록
def BFS(startNode, endNode, nodes):
    
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
            if nextNode==endNode:
                q.append((nextNode, path + [(edgeNum, True)]))
            else:
                q.append((nextNode, path + [(edgeNum, False)]))
            
    # 경로가 없을 경우 None 반환
    return None



# 입력 받은 node input 을 기준으로 from ~ to 를 각각 계산하여 최종 경로에 추가
def findPath(input):
    # 최종 경로
    totalPath = deque()
    
    nodes = input["assigned_drains"][:] 
    nodes.sort()
    nodes.insert(0, START_NODE_NUMBER)
    nodes.append(START_NODE_NUMBER)

    # node input 를 시작점, 도착점으로 각각 나누어 BFS 돌리기
    for i in range(len(nodes) - 1):
        startNode, endNode = nodes[i], nodes[i + 1]
        path = BFS(startNode, endNode, nodes)

        if path is None:
            raise ValueError(f"{startNode} 에서 {endNode} 로 가는 경로가 없습니다")

        # extend 로 경로누적
        totalPath.extend(path)

    return totalPath

9

# # 테스트 메시지
# input = {
#     "message": "로봇이 성공적으로 배정되었고 배수구 탐색 큐가 저장되었습니다.",
#     "robot_id": 1,
#     "assigned_drains": [
#         7,
#         8
#     ]
# }



# if __name__ == "__main__":

#     result = findPath(input)
#     print(result)
