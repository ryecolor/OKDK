from queue import Queue
from transitions import Machine
from modules.controller import RobotController
from modules.recv_command import CommandListener
from modules.logger import app_logger
from modules.config import WS_ROBOT_URL

def main():
    # 외부 명령 전달을 위한 thread-safe 큐 생성
    cmd_queue = Queue()
    log_queue = Queue()

    def command_callback(command):
        """
        CommandListener에서 호출할 콜백 함수.
        수신한 명령을 큐(cmd_queue)에 추가합니다.
        """
        app_logger.info(f"[CALLBACK] 명령 수신: {command}")
        cmd_queue.put(command)
        app_logger.info(f"{command}이(가) 명령 큐에 저장되었습니다.")

    # 외부 명령 수신을 위한 웹소켓 리스너 시작
    listener = CommandListener(WS_ROBOT_URL, command_callback=command_callback)
    listener.start()

    # FSM 구성: 초기 상태는 'loading'
    controller = RobotController()
    # trigger -> method, before는 해당 메소드가 실행되기 전에 호출됨, after는 해당 메소드가 실행되고 호출됨
    transitions_config = [
        {'trigger': 'load', 'source': 'loading', 'dest': 'idle', 'before': 'load_models'},
        {'trigger': 'activate', 'source': 'idle', 'dest': 'active'},
        {'trigger': 'deactivate', 'source': 'active', 'dest': 'idle'},
        {'trigger': 'shutdown', 'source': '*', 'dest': 'off', 'after': 'cleanup'}
    ]
    machine = Machine(model=controller, states=RobotController.states,
                      transitions=transitions_config, initial='loading')

    # 모델 및 카메라 로드 후 idle 상태로 전이
    controller.load()

    while True:
        try:
            if controller.state == 'idle':
                # idle 상태에서 "activate" 명령을 대기
                controller.run_idle(cmd_queue)
            elif controller.state == 'active':
                # activate trigger에 의해 active 상태로 전이된 후, 프레임 처리 루틴 수행 (대기 중 "deactivate" 명령 수신)
                controller.run_active(cmd_queue)
            # active 상태 종료 후, shutdown 트리거를 호출하여 자원 정리
            elif controller.state == 'off':
                break
        except KeyboardInterrupt:
            break
    controller.shutdown() 
    listener.stop()

if __name__ == "__main__":
    main()