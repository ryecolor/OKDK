import board
import busio
from adafruit_pca9685 import PCA9685
from modules.logger import app_logger

class Motor:
    """모터 제어를 담당하는 클래스"""
    
    def __init__(self):
        """
        Motor 클래스 초기화
        - I2C 버스 설정
        - PCA9685 설정
        - 채널 설정
        """
        # I2C 버스 설정
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.pca = PCA9685(self.i2c)
        self.pca.frequency = 60

        # 채널 설정
        self.RIGHT_CHANNEL = -3
        self.LEFT_CHANNEL = 0

    def _set_pwm(self, channel, speed):
        """
        PWM 신호를 설정하여 모터를 제어
        
        Args:
            channel (int): 모터 채널
            speed (float): 모터 속도 (-1.0 ~ 1.0)
        """
        pulse = int(0xFFFF * abs(speed))
        
        # 채널 오프셋 계산
        base_channel = channel
        forward_channel = channel + 4
        backward_channel = channel + 3
        pwm_channel = channel + 5

        if channel == 0:  # 왼쪽 모터
            if speed < 0:      # 후진
                self._set_channel_values(pwm_channel, pulse, forward_channel, 0, backward_channel, 0xFFFF)
            elif speed > 0:    # 전진
                self._set_channel_values(pwm_channel, pulse, forward_channel, 0xFFFF, backward_channel, 0)
            else:             # 정지
                self._set_channel_values(pwm_channel, 0, forward_channel, 0, backward_channel, 0)
        else:  # 오른쪽 모터
            if speed < 0:      # 후진
                self._set_channel_values(pwm_channel, 0xFFFF, forward_channel, 0, backward_channel, pulse)
            elif speed > 0:    # 전진
                self._set_channel_values(pwm_channel, 0, forward_channel, 0xFFFF, backward_channel, pulse)
            else:             # 정지
                self._set_channel_values(pwm_channel, 0, forward_channel, 0, backward_channel, 0)

    def _set_channel_values(self, pwm_channel, pwm_value, forward_channel, forward_value, backward_channel, backward_value):
        """
        채널별 PWM 값을 설정
        
        Args:
            pwm_channel (int): PWM 채널
            pwm_value (int): PWM 값
            forward_channel (int): 전진 채널
            forward_value (int): 전진 값
            backward_channel (int): 후진 채널
            backward_value (int): 후진 값
        """
        self.pca.channels[pwm_channel].duty_cycle = pwm_value
        self.pca.channels[forward_channel].duty_cycle = forward_value
        self.pca.channels[backward_channel].duty_cycle = backward_value

    def motor(self, left, right):
        """
        양쪽 모터의 속도를 제어
        
        Args:
            left (float): 왼쪽 모터 속도 (1.0: 최대 전진, -1.0: 최대 후진)
            right (float): 오른쪽 모터 속도 (1.0: 최대 전진, -1.0: 최대 후진)
        """
        # 속도 보정 및 부호 반전
        left = -1 * left
        right = -1 * right
        
        # 모터 제어
        self._set_pwm(self.RIGHT_CHANNEL, right)
        self._set_pwm(self.LEFT_CHANNEL, left)

    def stop(self):
        """모터를 정지"""
        self._set_pwm(self.RIGHT_CHANNEL, 0)
        self._set_pwm(self.LEFT_CHANNEL, 0)

    def cleanup(self):
        """프로그램 종료 시 정리"""
        self.stop()
        self.pca.deinit()