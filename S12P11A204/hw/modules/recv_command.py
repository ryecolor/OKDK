# command_listener.py
import asyncio
import websockets
import json
import threading
import queue
from .logger import app_logger


class CommandListener:
    def __init__(self, ws_url, command_callback=None):
        """
        :param ws_url: 연결할 웹소켓 URL
        :param command_callback: 명령 수신 시 호출할 콜백 함수 (명령을 인자로 받음)
                                 콜백 함수가 없으면 내부 큐에 명령을 저장합니다.
        """
        self.ws_url = ws_url
        # to set callback function 
        self.command_callback = command_callback
        self.command_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._start_loop, daemon=True)

    def _start_loop(self):
        # 새로운 이벤트 루프 생성 및 설정
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._listen_for_commands())
        except Exception as e:
            app_logger.error(f"[LOOP EXCEPTION] {e}")
        finally:
            loop.close()

    async def _listen_for_commands(self):
        while not self.stop_event.is_set():
            try:
                async with websockets.connect(self.ws_url) as websocket:
                    app_logger.info(f"서버({self.ws_url})에 연결되었습니다. 루트를 지정해주세요...")
                    while not self.stop_event.is_set():
                        # 서버로부터 메시지 수신
                        message = await websocket.recv()
                        app_logger.info(f"[RECEIVED] {message}")

                        try:
                            # JSON 문자열을 파싱하여 딕셔너리로 변환
                            data = json.loads(message)
                        except json.JSONDecodeError:
                            app_logger.error("수신한 메시지가 JSON 형식이 아닙니다.")
                            continue

                        # 'command' 키가 있는 경우 명령 처리
                        command = data.get("command")
                        if command:
                            app_logger.info(f" 명령어 '{command}' 처리 시작")
                            # 명령 처리: 콜백이 있으면 호출하거나 내부 큐에 저장
                            if self.command_callback:
                                self.command_callback(data)
                            else:
                                self.command_queue.put(data)

                            # Django 서버로 응답(acknowledgment) 메시지 전송 예제
                            response = {
                                "status": "success",
                                "command": command,
                                "message": "send back"
                            }
                            response_str = json.dumps(response)
                            await websocket.send(response_str)
                            app_logger.info(f"[SENT] 응답 메시지 전송: {response_str}")
                        else:
                            app_logger.error("[WARN] 'command' 키가 없는 메시지 수신")
            except websockets.ConnectionClosed:
                app_logger.error("서버와의 연결이 종료되었습니다. 5초 후 재연결 시도...")
                await asyncio.sleep(5)
            except Exception as e:
                app_logger.error(f"{e}. 5초 후 재연결 시도...")
                await asyncio.sleep(5)

    def start(self):
        """웹소켓 명령 수신 쓰레드를 시작합니다."""
        self.thread.start()

    def stop(self):
        """명령 수신을 중단합니다."""
        self.stop_event.set()

    def get_command(self, timeout=None):
        """
        내부 큐에 저장된 명령을 가져옵니다.
        :param timeout: 지정된 시간 동안 명령 대기 (초 단위)
        :return: 명령 문자열 또는 타임아웃 시 None
        """
        try:
            return self.command_queue.get(timeout=timeout)
        except queue.Empty:
            return None

